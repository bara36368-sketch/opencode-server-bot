$botDir = "C:\Users\ARYASATYA\Desktop\opencode-server-bot"
$logFile = "$botDir\restart.log"
Set-Location $botDir
while ($true) {
    $start = Get-Date
    "$(Get-Date -Format 'HH:mm:ss') Starting bot..." | Out-File $logFile -Append
    try {
        $p = Start-Process -FilePath "python" -ArgumentList "opencode_bot.py" -WorkingDirectory $botDir -NoNewWindow -PassThru
        $p.WaitForExit()
        $exitCode = $p.ExitCode
        "$(Get-Date -Format 'HH:mm:ss') Bot exited with code $exitCode, restarting in 3s..." | Out-File $logFile -Append
    } catch {
        "$(Get-Date -Format 'HH:mm:ss') Crash: $_ , restarting in 5s..." | Out-File $logFile -Append
    }
    Start-Sleep -Seconds 3
}
