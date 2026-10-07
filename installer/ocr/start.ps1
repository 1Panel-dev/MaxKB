param([switch]$Foreground)
$ErrorActionPreference = 'Stop'
$ocrRoot = $PSScriptRoot
$ocrPython = Join-Path $ocrRoot '.venv\Scripts\python.exe'
$ocrServer = Join-Path $ocrRoot 'server.py'
$ocrRuntime = Join-Path $ocrRoot 'runtime'
if (!(Test-Path -LiteralPath $ocrPython)) {
    throw 'Create the isolated OCR environment first; see installer/ocr/README.md.'
}
if (!(Test-Path -LiteralPath (Join-Path $ocrRuntime 'text-models\manifest.json'))) {
    & $ocrPython $ocrServer --warmup
    if ($LASTEXITCODE -ne 0) { throw 'OCR model warmup failed.' }
}
if ($Foreground) {
    & $ocrPython $ocrServer
    exit $LASTEXITCODE
}
$ocrTokenPath = Join-Path $ocrRuntime 'token'
if (Test-Path -LiteralPath $ocrTokenPath) {
    $ocrToken = [System.IO.File]::ReadAllText($ocrTokenPath).Trim()
    try {
        $ocrHealth = Invoke-RestMethod -Uri 'http://127.0.0.1:11637/health' -Headers @{ Authorization = "Bearer $ocrToken" } -TimeoutSec 3
        if ($ocrHealth.ready) { Write-Output 'Local OCR service is already ready.'; exit 0 }
    } catch { }
}
$ocrProcess = Start-Process -FilePath $ocrPython -ArgumentList ('"{0}"' -f $ocrServer) -WorkingDirectory $ocrRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $ocrRuntime 'service.log') -RedirectStandardError (Join-Path $ocrRuntime 'service-error.log')
$ocrProcess.Id | Set-Content -LiteralPath (Join-Path $ocrRuntime 'service.pid')
Write-Output "Local OCR service is starting (PID $($ocrProcess.Id))."
