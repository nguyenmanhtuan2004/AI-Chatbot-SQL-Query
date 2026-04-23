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
        public async Task<IActionResult> AskAI([FromBody] ChatRequest request)
        {
            if (string.IsNullOrWhiteSpace(request.Question))
            {
                return BadRequest("Question không được để trống.");
            }

            try
            {
                var apiKey = _configuration["API_KEY"] ?? _configuration["GoogleAI:ApiKey"];
                var accessToken = _configuration["GOOGLE_ACCESS_TOKEN"];
                if (string.IsNullOrWhiteSpace(apiKey) && string.IsNullOrWhiteSpace(accessToken))
                {
                    return StatusCode(500, "Thiếu thông tin xác thực. Hãy cấu hình API_KEY hoặc GOOGLE_ACCESS_TOKEN.");
                }

                var requestUrlOverride = _configuration["REQUEST_URL"] ?? _configuration["GoogleAI:RequestUrl"];
                var requestUrl = ResolveRequestUrl(requestUrlOverride, apiKey ?? string.Empty, _configuration);

                var payload = JsonSerializer.Serialize(new
                {
                    contents = new[]
                    {
                        new
                        {
                            role = "user",
                            parts = new[] { new { text = request.Question } }
                        }
                    }
                });

                var client = _httpClientFactory.CreateClient();
                if (!string.IsNullOrWhiteSpace(accessToken))
                {
                    client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", accessToken);
                }

                var userProject = _configuration["GOOGLE_USER_PROJECT"];
                if (!string.IsNullOrWhiteSpace(userProject))
                {
                    client.DefaultRequestHeaders.Remove("x-goog-user-project");
                    client.DefaultRequestHeaders.Add("x-goog-user-project", userProject);
                }

                using var content = new StringContent(payload, Encoding.UTF8, "application/json");
                using var response = await client.PostAsync(requestUrl, content);
                var responseBody = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    if (response.StatusCode == HttpStatusCode.Forbidden)
                    {
                        return StatusCode(500, "Lỗi hệ thống AI: Google AI trả về 403 (Forbidden). Kiểm tra lại API key, project, model và quyền truy cập.");
                    }

                    return StatusCode((int)response.StatusCode, $"Lỗi từ dịch vụ AI: {responseBody}");
                }

                var answer = ExtractAnswerText(responseBody);
                return Ok(new { Answer = answer });
            }
            catch (Exception ex)
            {
                // Lỗi mạng/DNS khi gọi Google AI: trả 503 để client biết có thể retry.
                if (IsNetworkError(ex))
                {
                    return StatusCode(503, "Không thể kết nối tới dịch vụ AI (lỗi mạng hoặc DNS). Kiểm tra Internet/DNS và thử lại.");
                }

                if (ex.ToString().Contains("403", StringComparison.OrdinalIgnoreCase))
                {
                    return StatusCode(500, "Lỗi hệ thống AI: Google AI trả về 403 (Forbidden). Kiểm tra lại GoogleAI:ApiKey và quyền truy cập model trong Google AI Studio.");
                }

                return StatusCode(500, $"Lỗi hệ thống AI: {ex.Message}");
            }
        }

        private static string ExtractAnswerText(string responseBody)
        {
            using var doc = JsonDocument.Parse(responseBody);

            if (doc.RootElement.ValueKind == JsonValueKind.Array)
            {
                var streamText = new StringBuilder();
                foreach (var chunk in doc.RootElement.EnumerateArray())
                {
                    streamText.Append(ExtractTextFromObject(chunk));
                }

                var fullStreamAnswer = streamText.ToString().Trim();
                return string.IsNullOrWhiteSpace(fullStreamAnswer) ? responseBody : fullStreamAnswer;
            }

            return ExtractTextFromObject(doc.RootElement);
        }

        private static string ExtractTextFromObject(JsonElement root)
        {
            if (!root.TryGetProperty("candidates", out var candidates)
                || candidates.ValueKind != JsonValueKind.Array
                || candidates.GetArrayLength() == 0)
            {
                return string.Empty;
            }

            var first = candidates[0];
            if (!first.TryGetProperty("content", out var content)
                || !content.TryGetProperty("parts", out var parts)
                || parts.ValueKind != JsonValueKind.Array)
            {
                return string.Empty;
            }

            var builder = new StringBuilder();
            foreach (var part in parts.EnumerateArray())
            {
                if (part.TryGetProperty("text", out var textNode))
                {
                    builder.Append(textNode.GetString());
                }
            }

            return builder.ToString();
        }

        private static string BuildDefaultRequestUrl(string apiKey, IConfiguration configuration)
        {
            var modelId = configuration["GoogleAI:ModelId"] ?? "gemini-2.5-flash-lite";
            var endpointBase = configuration["GoogleAI:EndpointBase"]
                ?? "https://aiplatform.googleapis.com/v1/publishers/google/models";
            return $"{endpointBase.TrimEnd('/')}/{modelId}:generateContent?key={apiKey}";
        }

        private static string ResolveRequestUrl(string? requestUrlOverride, string apiKey, IConfiguration configuration)
        {
            if (string.IsNullOrWhiteSpace(requestUrlOverride))
            {
                return BuildDefaultRequestUrl(apiKey, configuration);
            }

            var requestUrl = requestUrlOverride.Replace("${API_KEY}", Uri.EscapeDataString(apiKey));

            if (!string.IsNullOrWhiteSpace(apiKey)
                && !requestUrl.Contains("key=", StringComparison.OrdinalIgnoreCase)
                && requestUrl.Contains("aiplatform.googleapis.com", StringComparison.OrdinalIgnoreCase))
            {
                requestUrl += requestUrl.Contains("?") ? $"&key={Uri.EscapeDataString(apiKey)}" : $"?key={Uri.EscapeDataString(apiKey)}";
            }

            return requestUrl;
        }

        private static bool IsNetworkError(Exception ex)
        {
            if (ex is SocketException)
            {
                return true;
            }

            if (ex is HttpRequestException httpEx)
            {
                // Nếu có mã trạng thái HTTP (vd: 403/429/500 upstream) thì không phải lỗi mạng.
                if (httpEx.StatusCode is not null)
                {
                    return false;
                }

                // Không có StatusCode thường là lỗi kết nối/DNS/timeout ở tầng network.
                return true;
            }

            return ex.InnerException is not null && IsNetworkError(ex.InnerException);
        }
    }

    public class ChatRequest
    {
        public string Question { get; set; } = string.Empty;
    }
}