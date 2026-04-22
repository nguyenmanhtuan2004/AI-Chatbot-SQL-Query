using System.Threading;
using System.Threading.Tasks;
using API_ChatBot.Data;
using Microsoft.EntityFrameworkCore;
using Qdrant.Client;

namespace API_ChatBot
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            builder.Services.AddControllers();
            builder.Services.AddEndpointsApiExplorer();
            builder.Services.AddSwaggerGen();

            builder.Services.AddDbContext<AppDbContext>(options =>
                options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

            builder.Services.AddSingleton(sp =>
            {
                var host = builder.Configuration["Qdrant:Host"] ?? "localhost";
                var port = int.Parse(builder.Configuration["Qdrant:Port"] ?? "6334");
                return new QdrantClient(host, port);
            });

            var app = builder.Build();

            if (app.Environment.IsDevelopment())
            {
                app.UseSwagger();
                app.UseSwaggerUI();
            }

            app.UseAuthorization();
            app.MapControllers();

            if (app.Environment.IsDevelopment())
            {
                var url = "http://localhost:5025/swagger/index.html";
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
