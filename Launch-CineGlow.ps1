$root = "$env:USERPROFILE\Desktop\movie-suggestion-website"
$backend = "$root\backend"
$frontend = "$root\frontend"

if (Test-Path "$root\.venv\Scripts\python.exe") {
    $python = "$root\.venv\Scripts\python.exe"
} elseif (Test-Path "$backend\.venv\Scripts\python.exe") {
    $python = "$backend\.venv\Scripts\python.exe"
} else {
    $python = (Get-Command python).Source
}

Write-Host "Starting CineGlow backend..."
Start-Process powershell.exe -ArgumentList '-NoExit','-Command',"Set-Location '$backend'; & '$python' -m uvicorn app.main:app --reload --port 8000"

Write-Host "Starting CineGlow frontend..."
Start-Process powershell.exe -ArgumentList '-NoExit','-Command',"Set-Location '$frontend'; npm run dev"

Start-Sleep -Seconds 8
Start-Process "http://localhost:5173"
Read-Host "Press Enter to close this launcher"
