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
<<<<<<< HEAD
                options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));
=======
                options.UseSqlServer(builder.Configuration.GetConnectionString("site_chat"),
                    sqlServerOptionsAction: sqlOptions =>
                    {
                        sqlOptions.EnableRetryOnFailure(
                            maxRetryCount: 10,
                            maxRetryDelay: TimeSpan.FromSeconds(30),
                            errorNumbersToAdd: null);
                    }));
>>>>>>> main

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
