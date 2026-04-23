$apiUrl = "http://localhost:5026/api/chat/ask"
$payload = @{
    Question = "Giải thích ngắn gọn SQL là gì?"
} | ConvertTo-Json

Write-Host "--- BẮT ĐẦU TEST THỜI GIAN PHẢN HỒI API ---" -ForegroundColor Cyan
Write-Host "Endpoint: $apiUrl"
Write-Host "Payload: $payload"
Write-Host "-------------------------------------------"

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$ttfb = $null
$totalContent = ""

try {
    $request = [System.Net.HttpWebRequest]::Create($apiUrl)
    $request.Method = "POST"
    $request.ContentType = "application/json"
    $request.Timeout = 120000 # 2 minutes

    $bytes = [System.Text.Encoding]::UTF8.GetBytes($payload)
    $request.ContentLength = $bytes.Length
    
    $requestStream = $request.GetRequestStream()
    $requestStream.Write($bytes, 0, $bytes.Length)
    $requestStream.Close()

    $response = $request.GetResponse()
    $responseStream = $response.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($responseStream)

    Write-Host "Đang nhận stream dữ liệu..." -ForegroundColor Yellow

    while (-not $reader.EndOfStream) {
        $char = [char]$reader.Read()
        if ($null -eq $ttfb) {
            $ttfb = $stopwatch.ElapsedMilliseconds
            Write-Host ">> Time To First Byte (TTFB): $($ttfb)ms" -ForegroundColor Green
        }
        $totalContent += $char
        # Write-Host -NoNewline $char # Uncomment if you want to see the real-time output
    }

    $stopwatch.Stop()
    $totalTime = $stopwatch.ElapsedMilliseconds

    Write-Host "`n-------------------------------------------"
    Write-Host "KẾT QUẢ TEST:" -ForegroundColor Cyan
    Write-Host "- TTFB: $($ttfb)ms"
    Write-Host "- Tổng thời gian: $($totalTime)ms"
    Write-Host "- Độ dài phản hồi: $($totalContent.Length) ký tự"
    
    if ($totalTime -gt 0) {
        $speed = [math]::Round(($totalContent.Length / ($totalTime / 1000)), 2)
        Write-Host "- Tốc độ trung bình: $speed ký tự/giây"
    }

} catch {
    Write-Host "LỖI KHI GỌI API: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.InnerException) {
        Write-Host "Chi tiết: $($_.Exception.InnerException.Message)" -ForegroundColor Red
    }
} finally {
    if ($response) { $response.Close() }
}
