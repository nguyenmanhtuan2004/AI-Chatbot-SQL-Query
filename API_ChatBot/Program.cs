using System.Threading;
using System.Threading.Tasks;
using API_ChatBot.Data;
using DotNetEnv;
using Microsoft.EntityFrameworkCore;
using API_ChatBot.Services;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using Qdrant.Client;
namespace API_ChatBot
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var cwd = Directory.GetCurrentDirectory();
            var envCandidates = new[]
            {
                Path.Combine(cwd, ".env"),
                Path.Combine(cwd, "API_ChatBot", ".env")
            };

            foreach (var envPath in envCandidates)
            {
                if (File.Exists(envPath))
                {
                    Env.Load(envPath);
                    break;
                }
            }

            var builder = WebApplication.CreateBuilder(args);

            builder.Services.AddControllers();
            builder.Services.AddEndpointsApiExplorer();
            builder.Services.AddSwaggerGen();

            // Đăng ký Semantic Kernel với Vertex AI (dùng API Key qua query param)
            var apiKey = builder.Configuration["API_KEY"]
                         ?? builder.Configuration["GoogleAI:ApiKey"]
                         ?? throw new InvalidOperationException("Thiếu API_KEY trong cấu hình.");

            var rawRequestUrl = builder.Configuration["REQUEST_URL"]
                                ?? throw new InvalidOperationException("Thiếu REQUEST_URL trong cấu hình.");

            // Gắn ?key= vào URL nếu chưa có
            var vertexUrl = rawRequestUrl.Contains("?key=")
                ? rawRequestUrl
                : $"{rawRequestUrl}?key={Uri.EscapeDataString(apiKey)}";

            builder.Services.AddKernel();
            builder.Services.AddSingleton<IChatCompletionService>(sp =>
                new VertexAIGeminiService(
                    sp.GetRequiredService<IHttpClientFactory>(),
                    vertexUrl));
            builder.Services.AddHttpClient("", client =>
            {
                client.Timeout = TimeSpan.FromMinutes(2);
            })
            .ConfigurePrimaryHttpMessageHandler(() => new SocketsHttpHandler
            {
                PooledConnectionLifetime = TimeSpan.FromMinutes(5), // Giữ kết nối lâu hơn để tái sử dụng
                KeepAlivePingDelay = TimeSpan.FromSeconds(60),
                KeepAlivePingTimeout = TimeSpan.FromSeconds(30),
                EnableMultipleHttp2Connections = true // Quan trọng cho Streaming và hiệu suất cao
            });

            builder.Services.AddDbContext<AppDbContext>(options =>
                options.UseSqlServer(builder.Configuration.GetConnectionString("site_chat"),
                    sqlServerOptionsAction: sqlOptions =>
                    {
                        sqlOptions.EnableRetryOnFailure(
                            maxRetryCount: 10,
                            maxRetryDelay: TimeSpan.FromSeconds(30),
                            errorNumbersToAdd: null);
                    }));

            builder.Services.AddSingleton(sp =>
            {
                var host = builder.Configuration["Qdrant:Host"] ?? "localhost";
                var port = int.Parse(builder.Configuration["Qdrant:Port"] ?? "6334");
                return new QdrantClient(host, port);
            });
            builder.Services.AddCors(options =>
            {
                options.AddPolicy("AllowFrontend",
                    policy =>
                    {
                        policy.WithOrigins("http://localhost:3000")
                              .AllowAnyHeader()
                              .AllowAnyMethod();
                    });
            });

            var app = builder.Build();

            if (app.Environment.IsDevelopment())
            {
                app.UseSwagger();
                app.UseSwaggerUI();
            }

            app.UseCors("AllowFrontend");
            app.UseAuthorization();
            app.MapControllers();

            if (app.Environment.IsDevelopment())
            {
                var url = "http://localhost:5026/swagger/index.html";
                Task.Run(() =>
                {
                    Thread.Sleep(1500);
                    System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
                    {
                        FileName = url,
                        UseShellExecute = true
                    });
                });
            }

            app.Run();
        }
    }
}
