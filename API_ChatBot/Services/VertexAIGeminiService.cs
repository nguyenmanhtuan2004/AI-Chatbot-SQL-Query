using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using System.Net.Http.Headers;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;

namespace API_ChatBot.Services
{
    /// <summary>
    /// IChatCompletionService tùy chỉnh, gọi Vertex AI Gemini endpoint với API Key.
    /// Tương thích hoàn toàn với Semantic Kernel DI.
    /// </summary>
    public class VertexAIGeminiService : IChatCompletionService
    {
        private readonly IHttpClientFactory _httpClientFactory;
        private readonly string _requestUrl;

        public IReadOnlyDictionary<string, object?> Attributes { get; } =
            new Dictionary<string, object?>();

        public VertexAIGeminiService(IHttpClientFactory httpClientFactory, string requestUrl)
        {
            _httpClientFactory = httpClientFactory;
            _requestUrl = requestUrl;
        }

        public async Task<IReadOnlyList<ChatMessageContent>> GetChatMessageContentsAsync(
            ChatHistory chatHistory,
            PromptExecutionSettings? executionSettings = null,
            Kernel? kernel = null,
            CancellationToken cancellationToken = default)
        {
            var payload = BuildPayload(chatHistory, executionSettings);
            var client = _httpClientFactory.CreateClient();

            using var request = new HttpRequestMessage(HttpMethod.Post, _requestUrl)
            {
                Content = new StringContent(payload, Encoding.UTF8, "application/json")
            };

            using var response = await client.SendAsync(request, cancellationToken);
            response.EnsureSuccessStatusCode();

            var body = await response.Content.ReadAsStringAsync(cancellationToken);
            var text = ExtractTextFromVertexResponse(body);

            return [new ChatMessageContent(AuthorRole.Assistant, text)];
        }

        public async IAsyncEnumerable<StreamingChatMessageContent> GetStreamingChatMessageContentsAsync(
            ChatHistory chatHistory,
            PromptExecutionSettings? executionSettings = null,
            Kernel? kernel = null,
            [EnumeratorCancellation] CancellationToken cancellationToken = default)
        {
            var payload = BuildPayload(chatHistory, executionSettings);
            var client = _httpClientFactory.CreateClient();
            client.Timeout = TimeSpan.FromMinutes(2);

            using var request = new HttpRequestMessage(HttpMethod.Post, _requestUrl)
            {
                Content = new StringContent(payload, Encoding.UTF8, "application/json")
            };

            using var response = await client.SendAsync(
                request,
                HttpCompletionOption.ResponseHeadersRead,
                cancellationToken);

            response.EnsureSuccessStatusCode();

            using var stream = await response.Content.ReadAsStreamAsync(cancellationToken);
            using var reader = new StreamReader(stream);

            var buffer = new StringBuilder();
            char[] readBuf = new char[4096];
            int charsRead;

            while ((charsRead = await reader.ReadAsync(readBuf, 0, readBuf.Length)) > 0)
            {
                buffer.Append(readBuf, 0, charsRead);
                var current = buffer.ToString();

                // Tìm từng JSON object hoàn chỉnh trong stream
                int start = 0;
                while (true)
                {
                    int openBrace = current.IndexOf('{', start);
                    if (openBrace < 0) break;

                    int depth = 0;
                    int close = -1;
                    for (int i = openBrace; i < current.Length; i++)
                    {
                        if (current[i] == '{') depth++;
                        else if (current[i] == '}')
                        {
                            depth--;
                            if (depth == 0) { close = i; break; }
                        }
                    }

                    if (close < 0) break;

                    var chunk = current.Substring(openBrace, close - openBrace + 1);
                    var text = TryExtractText(chunk);

                    if (!string.IsNullOrEmpty(text))
                        yield return new StreamingChatMessageContent(AuthorRole.Assistant, text);

                    start = close + 1;
                }

                // Giữ lại phần chưa parse xong
                var remaining = start < current.Length ? current[start..] : string.Empty;
                buffer.Clear();
                buffer.Append(remaining);
            }
        }

        // ── Helpers ──────────────────────────────────────────────────────────

        private static string BuildPayload(
            ChatHistory chatHistory,
            PromptExecutionSettings? settings)
        {
            var contents = chatHistory.Select(msg => new
            {
                role = msg.Role == AuthorRole.Assistant ? "model" : "user",
                parts = new[] { new { text = msg.Content ?? string.Empty } }
            }).ToArray();

            int maxTokens = 2048;
            float temperature = 0.7f;

            if (settings?.ExtensionData != null)
            {
                if (settings.ExtensionData.TryGetValue("max_tokens", out var mt) && mt is int mi)
                    maxTokens = mi;
                if (settings.ExtensionData.TryGetValue("temperature", out var temp) && temp is float tf)
                    temperature = tf;
            }

            return JsonSerializer.Serialize(new
            {
                contents,
                generationConfig = new { temperature, maxOutputTokens = maxTokens }
            });
        }

        private static string TryExtractText(string json)
        {
            try
            {
                using var doc = JsonDocument.Parse(json);
                return ExtractTextFromRoot(doc.RootElement);
            }
            catch { return string.Empty; }
        }

        private static string ExtractTextFromVertexResponse(string json)
        {
            try
            {
                // Vertex AI trả về array: [{...}, {...}]
                using var doc = JsonDocument.Parse(json);
                var sb = new StringBuilder();

                if (doc.RootElement.ValueKind == JsonValueKind.Array)
                {
                    foreach (var item in doc.RootElement.EnumerateArray())
                        sb.Append(ExtractTextFromRoot(item));
                }
                else
                {
                    sb.Append(ExtractTextFromRoot(doc.RootElement));
                }

                return sb.ToString();
            }
            catch { return string.Empty; }
        }

        private static string ExtractTextFromRoot(JsonElement root)
        {
            if (!root.TryGetProperty("candidates", out var candidates)
                || candidates.ValueKind != JsonValueKind.Array
                || candidates.GetArrayLength() == 0)
                return string.Empty;

            if (!candidates[0].TryGetProperty("content", out var content)
                || !content.TryGetProperty("parts", out var parts)
                || parts.ValueKind != JsonValueKind.Array)
                return string.Empty;

            var sb = new StringBuilder();
            foreach (var part in parts.EnumerateArray())
            {
                if (part.TryGetProperty("text", out var text))
                    sb.Append(text.GetString());
            }

            return sb.ToString();
        }
    }
}
