using Microsoft.AspNetCore.Mvc;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Connectors.Google;
using System.Net;

namespace API_ChatBot.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ChatController : ControllerBase
    {
        private readonly IChatCompletionService _chatService;
        private readonly IConfiguration _configuration;

        public ChatController(IChatCompletionService chatService, IConfiguration configuration)
        {
            _chatService = chatService;
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
                var maxTokensStr = _configuration["MAX_OUTPUT_TOKENS"];
                int maxTokens = int.TryParse(maxTokensStr, out var val) ? val : 2048;

                var tempStr = _configuration["TEMPERATURE"];
                float temperature = float.TryParse(tempStr,
                    System.Globalization.NumberStyles.Any,
                    System.Globalization.CultureInfo.InvariantCulture,
                    out var t) ? t : 0.7f;

                var executionSettings = new GeminiPromptExecutionSettings
                {
                    MaxTokens = maxTokens,
                    Temperature = temperature
                };

                var history = new ChatHistory();
                if (request.Messages != null && request.Messages.Count > 0)
                {
                    foreach (var msg in request.Messages)
                    {
                        if (msg.Role == "assistant")
                            history.AddAssistantMessage(msg.Content);
                        else
                            history.AddUserMessage(msg.Content);
                    }
                }

                // Fallback: nếu history rỗng thì dùng question
                if (history.Count == 0)
                {
                    if (string.IsNullOrWhiteSpace(request.Question))
                    {
                        Response.StatusCode = (int)HttpStatusCode.BadRequest;
                        await Response.WriteAsync("Cần cung cấp 'question' hoặc 'messages' hợp lệ.");
                        return;
                    }
                    history.AddUserMessage(request.Question);
                }

                Response.ContentType = "text/plain; charset=utf-8";

                await foreach (var chunk in _chatService.GetStreamingChatMessageContentsAsync(
                    history,
                    executionSettings: executionSettings))
                {
                    if (!string.IsNullOrEmpty(chunk.Content))
                    {
                        await Response.WriteAsync(chunk.Content);
                        await Response.Body.FlushAsync();
                    }
                }
            }
            catch (Exception ex)
            {
                if (!Response.HasStarted)
                {
                    Response.StatusCode = (int)HttpStatusCode.InternalServerError;
                    await Response.WriteAsync($"Lỗi hệ thống: {ex.Message}");
                }
            }
        }
    }

    public class ChatRequest
    {
        public string Question { get; set; } = string.Empty;

        /// <summary>Lịch sử hội thoại (tùy chọn). Nếu có sẽ dùng thay vì Question đơn lẻ.</summary>
        public List<ChatMessage>? Messages { get; set; }
    }

    public class ChatMessage
    {
        public string Role { get; set; } = "user";
        public string Content { get; set; } = string.Empty;
    }
}
