param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^\d+\.\d+\.\d+$')]
    [string]$Version
)

$ErrorActionPreference = 'Stop'
$repoPath = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$targetPath = Join-Path $repoPath 'contracts/agent-runtime-api.yaml'
$stagePath = Join-Path $repoPath "contracts/.agent-runtime-$([guid]::NewGuid()).yaml"
$backupPath = Join-Path $repoPath "contracts/.agent-runtime-$([guid]::NewGuid()).backup"
$tempPath = Join-Path ([System.IO.Path]::GetTempPath()) ("portable-agent-contracts-" + [guid]::NewGuid())
$archiveName = "portable-agent-contracts-$Version.tgz"
$archivePath = Join-Path $tempPath $archiveName
$checksumPath = Join-Path $tempPath 'SHA256SUMS'
$releaseUrl = "https://github.com/portable-agent/contracts/releases/download/v$Version"

try {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        throw 'GitHub CLI is required to verify the contract attestation.'
    }
    New-Item -ItemType Directory -Path $tempPath | Out-Null
    Invoke-WebRequest -Uri "$releaseUrl/$archiveName" -OutFile $archivePath
    Invoke-WebRequest -Uri "$releaseUrl/SHA256SUMS" -OutFile $checksumPath

    $escapedName = [regex]::Escape($archiveName)
    $entries = @(Get-Content -LiteralPath $checksumPath | Where-Object {
        $_ -match "^(?<hash>[a-fA-F0-9]{64})\s+\*?$escapedName$"
    })
    if ($entries.Count -ne 1) {
        throw 'Checksum file does not contain exactly one entry for the contract bundle.'
    }
    $null = $entries[0] -match '^(?<hash>[a-fA-F0-9]{64})'
    $expectedHash = $Matches.hash.ToUpperInvariant()
    $actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $archivePath).Hash
    if ($actualHash -ne $expectedHash) {
        throw 'Checksum contract bundle does not match the release.'
    }

    & gh attestation verify $archivePath --repo portable-agent/contracts
    if ($LASTEXITCODE -ne 0) {
        throw 'Cannot verify the GitHub attestation for the contract bundle.'
    }

    & tar -xzf $archivePath -C $tempPath 'package/openapi/agent-runtime-api.yaml'
    if ($LASTEXITCODE -ne 0) {
        throw 'Cannot unpack contract bundle.'
    }
    $sourcePath = Join-Path $tempPath 'package/openapi/agent-runtime-api.yaml'
    if ((Get-Content -Raw -LiteralPath $sourcePath) -notmatch
        "(?m)^  version: $([regex]::Escape($Version))$") {
        throw 'Agent Runtime API version does not match the requested release.'
    }
    Copy-Item -LiteralPath $sourcePath -Destination $stagePath
    [System.IO.File]::Replace($stagePath, $targetPath, $backupPath, $true)
    Write-Output "Agent Runtime API updated to version $Version."
} finally {
    foreach ($localPath in @($stagePath, $backupPath)) {
        if (Test-Path -LiteralPath $localPath) {
            Remove-Item -LiteralPath $localPath -Force
        }
    }
    $resolvedTemp = [System.IO.Path]::GetFullPath($tempPath)
    $systemTemp = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
    if ($resolvedTemp.StartsWith($systemTemp, [System.StringComparison]::OrdinalIgnoreCase) -and
        (Test-Path -LiteralPath $resolvedTemp)) {
        Remove-Item -LiteralPath $resolvedTemp -Recurse -Force
    }
}
