param(
    [switch]$OpenMiniProgram = $true
)

$ErrorActionPreference = 'Stop'

$workspaceRoot = 'D:\Ver5'
$runtimeDir = Join-Path $workspaceRoot '.runtime'
$logDir = Join-Path $runtimeDir 'logs'
$pidFile = Join-Path $runtimeDir 'pids.json'

$ruoyiRoot = 'D:\Ver5\MyRuoYi\dev\project\web_doctor_final\RuoYi-Vue-master'
$ruoyiJar = Join-Path $ruoyiRoot 'ruoyi-admin\target\ruoyi-admin.jar'
$ruoyiUi = Join-Path $ruoyiRoot 'ruoyi-ui'

$wxFamily = 'D:\Ver5\MyRuoYi\dev\project\wx_family_final\family'
$wxPatient = 'D:\Ver5\MyRuoYi\dev\project\wx_patient_final\patient'

New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Test-PortListening {
    param([int]$Port)
    $conn = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -First 1
    return $null -ne $conn
}

function Start-DetachedProcess {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$ArgumentList,
        [Parameter(Mandatory = $true)][string]$LogPath
    )

    $errLogPath = "$LogPath.err"

    $proc = Start-Process -FilePath $FilePath `
        -ArgumentList $ArgumentList `
        -WorkingDirectory $WorkingDirectory `
        -RedirectStandardOutput $LogPath `
        -RedirectStandardError $errLogPath `
        -PassThru

    Write-Host "[OK] $Name started (PID=$($proc.Id))"
    return $proc.Id
}

function Ensure-Command {
    param([string]$Cmd)
    if (-not (Get-Command $Cmd -ErrorAction SilentlyContinue)) {
        throw "Command not found: $Cmd"
    }
}

function Resolve-PythonExe {
    $fallbacks = @(
        'D:\Anaconda\envs\Ver5\python.exe',
        (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313\python.exe'),
        'C:\Python313\python.exe'
    )

    foreach ($candidate in $fallbacks) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    if ($env:CONDA_PREFIX) {
        $condaPython = Join-Path $env:CONDA_PREFIX 'python.exe'
        if (Test-Path $condaPython) {
            return $condaPython
        }
    }

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        return $pythonCmd.Source
    }

    throw 'Python executable not found.'
}

Ensure-Command 'java'
Ensure-Command 'mvn'
Ensure-Command 'npm'

$pythonExe = Resolve-PythonExe
Write-Host "[INFO] Python executable: $pythonExe"

$pids = [ordered]@{
    startedAt = (Get-Date).ToString('s')
}

if (-not (Test-PortListening -Port 8080)) {
    if (-not (Test-Path $ruoyiJar)) {
        Write-Host '[INFO] Backend jar missing, building now...'
        Push-Location $ruoyiRoot
        try {
            & mvn -pl ruoyi-admin -am -DskipTests package
            if ($LASTEXITCODE -ne 0) {
                throw 'Backend build failed.'
            }
        }
        finally {
            Pop-Location
        }
    }

    $backendLog = Join-Path $logDir 'ruoyi-backend.log'
    $pids.ruoyiBackend = Start-DetachedProcess -Name 'RuoYi backend' -WorkingDirectory (Split-Path $ruoyiJar) -FilePath 'java' -ArgumentList @('-jar', $ruoyiJar) -LogPath $backendLog
}
else {
    Write-Host '[SKIP] Port 8080 already in use, backend not started.'
}

if (-not (Test-PortListening -Port 80)) {
    $frontendLog = Join-Path $logDir 'ruoyi-frontend.log'
    $pids.ruoyiFrontend = Start-DetachedProcess -Name 'RuoYi frontend' -WorkingDirectory $ruoyiUi -FilePath 'cmd.exe' -ArgumentList @('/c', 'set NODE_OPTIONS=--openssl-legacy-provider && npm run dev') -LogPath $frontendLog
}
else {
    Write-Host '[SKIP] Port 80 already in use, frontend not started.'
}

if (-not (Test-PortListening -Port 8010)) {
    $agentLog = Join-Path $logDir 'multi-agent.log'
    $pids.multiAgent = Start-DetachedProcess -Name 'Multi-agent backend' -WorkingDirectory $workspaceRoot -FilePath $pythonExe -ArgumentList @('-m', 'uvicorn', 'MyAgentSystem.multi_agent_system_v2.api.app_api:app', '--host', '127.0.0.1', '--port', '8010') -LogPath $agentLog
}
else {
    Write-Host '[SKIP] Port 8010 already in use, multi-agent backend not started.'
}

if ($OpenMiniProgram) {
    $pf86 = [Environment]::GetEnvironmentVariable('ProgramFiles(x86)')
    $pf64 = [Environment]::GetEnvironmentVariable('ProgramFiles')
    $cliCandidates = @(
        (Join-Path $pf86 'Tencent\微信web开发者工具\cli.bat'),
        (Join-Path $pf64 'Tencent\微信web开发者工具\cli.bat')
    ) | Where-Object { $_ -and $_.Trim() -ne '' }

    $wxCli = $cliCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

    if ($wxCli) {
        Start-Process -FilePath $wxCli -ArgumentList @('open', '--project', $wxFamily) | Out-Null
        Start-Process -FilePath $wxCli -ArgumentList @('open', '--project', $wxPatient) | Out-Null
        Write-Host '[OK] WeChat DevTools projects open command sent.'
    }
    else {
        Write-Host '[WARN] WeChat DevTools CLI not found. Open these manually:'
        Write-Host "       $wxFamily"
        Write-Host "       $wxPatient"
    }
}

$pids | ConvertTo-Json | Set-Content -Path $pidFile -Encoding UTF8

Write-Host ''
Write-Host '================ Startup Done ================'
Write-Host "Log dir:    $logDir"
Write-Host "PID file:   $pidFile"
Write-Host 'Backend:    http://localhost:8080'
Write-Host 'Frontend:   http://localhost:80'
Write-Host 'Agent API:  http://127.0.0.1:8010/health'
Write-Host '=============================================='
