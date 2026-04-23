using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using System.Net;
using System.Net.Http;
using System.Net.Sockets;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;

namespace API_ChatBot.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ChatController : ControllerBase
    {
        private readonly IHttpClientFactory _httpClientFactory;
        private readonly IConfiguration _configuration;

        public ChatController(IHttpClientFactory httpClientFactory, IConfiguration configuration)
        {
            _httpClientFactory = httpClientFactory;
            _configuration = configuration;
        }

        [HttpPost("ask")]
        public async Task AskAI([FromBody] ChatRequest request)
        {
            if (string.IsNullOrWhiteSpace(request.Question))
            {
                Response.StatusCode = (int)HttpStatusCode.BadRequest;
                await Response.WriteAsync("Question không được để trống.");
                return;
            }

            try
            {
                var apiKey = _configuration["API_KEY"] ?? _configuration["GoogleAI:ApiKey"];
                var requestUrl = ResolveRequestUrl(_configuration["REQUEST_URL"], apiKey ?? string.Empty);

                var payload = JsonSerializer.Serialize(new
                {
                    contents = new[] { new { role = "user", parts = new[] { new { text = request.Question } } } },
                    generationConfig = new { temperature = 0.7, maxOutputTokens = 2048 }
                });

                var client = _httpClientFactory.CreateClient();
                client.Timeout = TimeSpan.FromMinutes(2);

                if (!string.IsNullOrWhiteSpace(_configuration["GOOGLE_ACCESS_TOKEN"]))
                    client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", _configuration["GOOGLE_ACCESS_TOKEN"]);

                var userProject = _configuration["GOOGLE_USER_PROJECT"];
                if (!string.IsNullOrWhiteSpace(userProject))
                    client.DefaultRequestHeaders.Add("x-goog-user-project", userProject);

                using var requestMessage = new HttpRequestMessage(HttpMethod.Post, requestUrl)
                {
                    Content = new StringContent(payload, Encoding.UTF8, "application/json")
                };
                
                using var response = await client.SendAsync(requestMessage, HttpCompletionOption.ResponseHeadersRead);

                if (!response.IsSuccessStatusCode)
                {
                    Response.StatusCode = (int)response.StatusCode;
                    await Response.WriteAsync($"Lỗi AI: {await response.Content.ReadAsStringAsync()}");
                    return;
                }

                Response.ContentType = "text/plain; charset=utf-8";
                using var responseStream = await response.Content.ReadAsStreamAsync();
                using var reader = new StreamReader(responseStream);
                
                await ProcessStreamAsync(reader);
            }
            catch (Exception ex)
            {
                Response.StatusCode = (int)HttpStatusCode.InternalServerError;
                await Response.WriteAsync($"Lỗi hệ thống: {ex.Message}");
            }
        }

        private async Task ProcessStreamAsync(StreamReader reader)
        {
            var buffer = new char[8192];
            int charCount;
            var sb = new StringBuilder();

            while ((charCount = await reader.ReadAsync(buffer, 0, buffer.Length)) > 0)
            {
                sb.Append(buffer, 0, charCount);
                var contentStr = sb.ToString();

                int openBraceIndex;
                while ((openBraceIndex = contentStr.IndexOf('{')) >= 0)
                {
                    int braceCount = 0;
                    int closeBraceIndex = -1;

                    for (int i = openBraceIndex; i < contentStr.Length; i++)
                    {
                        if (contentStr[i] == '{') braceCount++;
                        else if (contentStr[i] == '}')
                        {
                            braceCount--;
                            if (braceCount == 0) { closeBraceIndex = i; break; }
                        }
                    }

                    if (closeBraceIndex == -1) break;

                    var jsonChunk = contentStr.Substring(openBraceIndex, closeBraceIndex - openBraceIndex + 1);
                    await WriteChunkAsync(jsonChunk);

                    contentStr = contentStr.Substring(closeBraceIndex + 1);
                    sb.Clear();
                    sb.Append(contentStr);
                }
            }
        }

        private async Task WriteChunkAsync(string jsonChunk)
        {
            try
            {
                using var doc = JsonDocument.Parse(jsonChunk);
                var text = ExtractTextFromObject(doc.RootElement);
                if (!string.IsNullOrEmpty(text))
                {
                    await Response.WriteAsync(text);
                    await Response.Body.FlushAsync();
                }
            }
            catch { /* Ignore invalid chunks */ }
        }

        private static string ExtractTextFromObject(JsonElement root)
        {
            if (!root.TryGetProperty("candidates", out var candidates) || candidates.ValueKind != JsonValueKind.Array || candidates.GetArrayLength() == 0)
                return string.Empty;

            var content = candidates[0];
            if (!content.TryGetProperty("content", out var contentNode) || !contentNode.TryGetProperty("parts", out var parts) || parts.ValueKind != JsonValueKind.Array)
                return string.Empty;

            var builder = new StringBuilder();
            foreach (var part in parts.EnumerateArray())
            {
                if (part.TryGetProperty("text", out var textNode))
                    builder.Append(textNode.GetString());
            }
            return builder.ToString();
        }

        private static string ResolveRequestUrl(string? requestUrlOverride, string apiKey)
        {
            if (string.IsNullOrWhiteSpace(requestUrlOverride))
                throw new InvalidOperationException("REQUEST_URL is not configured in .env");

            return requestUrlOverride.Replace("${API_KEY}", Uri.EscapeDataString(apiKey));
        }

        private static bool IsNetworkError(Exception ex)
        {
            if (ex is SocketException || (ex is HttpRequestException httpEx && httpEx.StatusCode == null))
                return true;

            return ex.InnerException != null && IsNetworkError(ex.InnerException);
        }
    }

    public class ChatRequest
    {
        public string Question { get; set; } = string.Empty;
    }
}