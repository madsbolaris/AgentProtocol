# Start all echo bots on their configured ports
# Reads port configuration from echo-bot-ports.json at project root

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$PortsFile = Join-Path $ProjectRoot "echo-bot-ports.json"

# Check if ports file exists
if (-not (Test-Path $PortsFile)) {
    Write-Error "Error: echo-bot-ports.json not found at project root"
    exit 1
}

# Read ports from JSON file
$portsConfig = Get-Content $PortsFile | ConvertFrom-Json
$PythonPort = $portsConfig.python
$DotnetPort = $portsConfig.dotnet
$TypeScriptPort = $portsConfig.typescript

Write-Host "Starting echo bots with configured ports:"
Write-Host "  Python: $PythonPort"
Write-Host "  .NET: $DotnetPort"
Write-Host "  TypeScript: $TypeScriptPort"
Write-Host ""

# Create log directory
$LogDir = Join-Path $ProjectRoot ".logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

# Array to store job objects
$Jobs = @()

# Function to stop all echo bots on exit
function Stop-EchoBots {
    Write-Host ""
    Write-Host "Stopping all echo bots..."
    $Jobs | ForEach-Object { Stop-Job $_; Remove-Job $_ }
    Write-Host "All echo bots stopped."
}

# Register cleanup on exit
Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Stop-EchoBots }

try {
    # Start Python echo bot
    Write-Host "Starting Python echo bot on port $PythonPort..."
    $PythonDir = Join-Path $ProjectRoot "python/samples/agents/echo-bot"
    $PythonLog = Join-Path $LogDir "python-echo-bot.log"
    $env:PORT = $PythonPort
    $PythonJob = Start-Job -ScriptBlock {
        param($dir, $log, $port)
        Set-Location $dir
        $env:PORT = $port
        python src/start_server.py 2>&1 | Tee-Object -FilePath $log
    } -ArgumentList $PythonDir, $PythonLog, $PythonPort
    $Jobs += $PythonJob
    Write-Host "  Python echo bot Job ID: $($PythonJob.Id)"

    # Start .NET echo bot
    Write-Host "Starting .NET echo bot on port $DotnetPort..."
    $DotnetDir = Join-Path $ProjectRoot "dotnet/samples/agents/EchoBot"
    $DotnetLog = Join-Path $LogDir "dotnet-echo-bot.log"
    $env:PORT = $DotnetPort
    $DotnetJob = Start-Job -ScriptBlock {
        param($dir, $log, $port)
        Set-Location $dir
        $env:PORT = $port
        dotnet run 2>&1 | Tee-Object -FilePath $log
    } -ArgumentList $DotnetDir, $DotnetLog, $DotnetPort
    $Jobs += $DotnetJob
    Write-Host "  .NET echo bot Job ID: $($DotnetJob.Id)"

    # Start TypeScript echo bot
    Write-Host "Starting TypeScript echo bot on port $TypeScriptPort..."
    $TypeScriptDir = Join-Path $ProjectRoot "typescript/samples/echo-bot"
    $TypeScriptLog = Join-Path $LogDir "typescript-echo-bot.log"
    $env:PORT = $TypeScriptPort
    $TypeScriptJob = Start-Job -ScriptBlock {
        param($dir, $log, $port)
        Set-Location $dir
        $env:PORT = $port
        npm start 2>&1 | Tee-Object -FilePath $log
    } -ArgumentList $TypeScriptDir, $TypeScriptLog, $TypeScriptPort
    $Jobs += $TypeScriptJob
    Write-Host "  TypeScript echo bot Job ID: $($TypeScriptJob.Id)"

    Write-Host ""
    Write-Host "All echo bots started successfully!"
    Write-Host "Logs are available in $LogDir/"
    Write-Host ""
    Write-Host "To test the echo bots, use:"
    Write-Host "  Invoke-WebRequest -Method GET http://localhost:$PythonPort/health"
    Write-Host "  Invoke-WebRequest -Method GET http://localhost:$DotnetPort/health"
    Write-Host "  Invoke-WebRequest -Method GET http://localhost:$TypeScriptPort/health"
    Write-Host ""
    Write-Host "Press Ctrl+C to stop all echo bots"
    Write-Host ""

    # Wait for all jobs
    $Jobs | Wait-Job | Out-Null
}
finally {
    Stop-EchoBots
}
