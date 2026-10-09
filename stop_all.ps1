$ErrorActionPreference = 'Stop'

$pidFile = 'D:\Ver5\.runtime\pids.json'

if (-not (Test-Path $pidFile)) {
    Write-Host '[INFO] 未找到 PID 文件，无需停止'
    exit 0
}

$pids = Get-Content $pidFile -Raw | ConvertFrom-Json

$processNames = @('ruoyiBackend', 'ruoyiFrontend', 'multiAgent')
foreach ($name in $processNames) {
    $procId = $pids.$name
    if ($procId) {
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($proc) {
            Stop-Process -Id $procId -Force
            Write-Host "[OK] 已停止 $name (PID=$procId)"
        }
        else {
            Write-Host "[SKIP] $name 对应进程不存在 (PID=$procId)"
        }
    }
}

Remove-Item $pidFile -Force
Write-Host '[DONE] 停止完成'
