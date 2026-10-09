[CmdletBinding()]
param(
    [ValidateSet('dev', 'test', 'staging', 'prod')]
    [string]$Environment = 'dev',

    [ValidateSet('backend', 'ai', 'kb', 'frontend', 'all')]
    [string]$Module = 'all',

    [string]$EnvFile
)

$ErrorActionPreference = 'Stop'
$values = @{}
$errors = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()

Get-ChildItem Env: | ForEach-Object { $values[$_.Name] = $_.Value }

if ($EnvFile) {
    if (-not (Test-Path -LiteralPath $EnvFile -PathType Leaf)) {
        [Console]::Error.WriteLine('Configuration file was not found.')
        exit 2
    }
    foreach ($line in Get-Content -LiteralPath $EnvFile) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith('#') -or -not $trimmed.Contains('=')) { continue }
        $parts = $trimmed.Split('=', 2)
        if (-not $values.ContainsKey($parts[0])) { $values[$parts[0]] = $parts[1] }
    }
}

function Get-ConfigValue([string]$Canonical, [string]$Legacy) {
    if ($values.ContainsKey($Canonical) -and $values[$Canonical]) {
        if ($Legacy -and $values.ContainsKey($Legacy) -and $values[$Legacy] -and $values[$Legacy] -ne $values[$Canonical]) {
            $warnings.Add("$Canonical overrides its legacy alias $Legacy.")
        }
        return $values[$Canonical]
    }
    if ($Legacy -and $values.ContainsKey($Legacy)) { return $values[$Legacy] }
    return $null
}

function Test-Placeholder([string]$Value) {
    return [string]::IsNullOrWhiteSpace($Value) -or $Value -match '^(change_me|example|todo)$|^replace-with-'
}

function Require-Config([string]$Canonical, [string]$Legacy = '') {
    $value = Get-ConfigValue $Canonical $Legacy
    if (Test-Placeholder $value) { $errors.Add("Missing or placeholder configuration: $Canonical.") }
    return $value
}

function Require-ExternalPath([string]$Canonical, [string]$Legacy = '') {
    $value = Require-Config $Canonical $Legacy
    if (-not $value) { return }
    if (-not [System.IO.Path]::IsPathRooted($value)) {
        $errors.Add("$Canonical must be an absolute path in $Environment.")
        return
    }
    $repositoryRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
    $fullPath = [System.IO.Path]::GetFullPath($value)
    if ($fullPath.StartsWith($repositoryRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        $errors.Add("$Canonical must not point inside the Git worktree.")
    }
}

if ($Module -in @('backend', 'all')) {
    $configuredEnvironment = Get-ConfigValue 'DFS_APP_ENV' 'SPRING_PROFILES_ACTIVE'
    if ($configuredEnvironment -and $configuredEnvironment -ne $Environment) {
        $errors.Add('DFS_APP_ENV does not match the requested -Environment.')
    }

    if ($Environment -in @('staging', 'prod')) {
        Require-Config 'DFS_DB_MASTER_URL' 'DB_MASTER_URL' | Out-Null
        Require-Config 'DFS_DB_MASTER_USERNAME' 'DB_MASTER_USERNAME' | Out-Null
        Require-Config 'DFS_DB_MASTER_PASSWORD' 'DB_MASTER_PASSWORD' | Out-Null
        Require-Config 'DFS_AUTH_JWT_SECRET' 'JWT_SECRET' | Out-Null
        Require-Config 'DFS_DRUID_MONITOR_USERNAME' 'DRUID_MONITOR_USERNAME' | Out-Null
        Require-Config 'DFS_DRUID_MONITOR_PASSWORD' 'DRUID_MONITOR_PASSWORD' | Out-Null

        $publicUrl = Require-Config 'DFS_STORAGE_PUBLIC_BASE_URL' 'FILES_PUBLIC_BASE_URL'
        if ($publicUrl -and -not $publicUrl.StartsWith('https://', [System.StringComparison]::OrdinalIgnoreCase)) {
            $errors.Add('DFS_STORAGE_PUBLIC_BASE_URL must use HTTPS outside dev/test.')
        }
        $druidAllow = Require-Config 'DFS_DRUID_MONITOR_ALLOW' 'DRUID_MONITOR_ALLOW'
        if ($druidAllow -and $druidAllow -match '^(\*|0\.0\.0\.0/0)$') {
            $errors.Add('Druid access allowlist must not be open to every address.')
        }
        $swagger = Get-ConfigValue 'DFS_SWAGGER_ENABLED' 'SWAGGER_ENABLED'
        if ($swagger -and $swagger.ToLowerInvariant() -eq 'true') {
            $errors.Add('Swagger must be disabled outside dev/test.')
        }
    }
}

if ($Module -in @('ai', 'all') -and $Environment -in @('staging', 'prod')) {
    Require-ExternalPath 'DFS_FITABASE_DATA_DIR' 'FITABASE_DATA_DIR'
    Require-ExternalPath 'DFS_APP_OUTPUT_DIR' 'APP_OUTPUT_DIR'
    Require-ExternalPath 'DFS_PATIENT_CONFIG_PATH' 'PATIENT_CONFIG_PATH'
}

if ($Module -in @('kb', 'all') -and $Environment -in @('staging', 'prod')) {
    Require-ExternalPath 'DFS_KB_BASE_DIR' 'KB_BASE_DIR'
    Require-ExternalPath 'DFS_CHROMA_DB_DIR' 'CHROMA_DB_DIR'
}

if ($Module -in @('frontend', 'all') -and $Environment -in @('staging', 'prod')) {
    $apiUrl = Require-Config 'DFS_MINIPROGRAM_API_BASE_URL'
    if ($apiUrl -and -not $apiUrl.StartsWith('https://', [System.StringComparison]::OrdinalIgnoreCase)) {
        $errors.Add('DFS_MINIPROGRAM_API_BASE_URL must use HTTPS outside dev/test.')
    }
}

foreach ($warning in $warnings) { Write-Warning $warning }
if ($errors.Count -gt 0) {
    foreach ($errorItem in $errors) { [Console]::Error.WriteLine("ERROR: $errorItem") }
    exit 1
}

Write-Output "Configuration validation passed for $Environment / $Module."
exit 0
