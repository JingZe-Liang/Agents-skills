param(
    [Parameter(Mandatory = $true)]
    [string]$ModelName,

    [Parameter(Mandatory = $true)]
    [string]$WorkspacePath,

    [Parameter(Mandatory = $true)]
    [string]$S32DSRoot,

    [Parameter(Mandatory = $true)]
    [string]$ECUCoderRoot,

    [switch]$Fix,
    [switch]$RunBuild
)

$ErrorActionPreference = 'Stop'

function Info($message) { Write-Host "[INFO] $message" }
function Ok($message) { Write-Host "[OK] $message" -ForegroundColor Green }
function Warn($message) { Write-Host "[WARN] $message" -ForegroundColor Yellow }
function Fail($message) { Write-Host "[FAIL] $message" -ForegroundColor Red }

function Backup-File($path) {
    if (-not (Test-Path -LiteralPath $path)) { return $null }
    $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $backup = "$path.bak_$stamp"
    Copy-Item -LiteralPath $path -Destination $backup
    return $backup
}

function Replace-InFile($path, $pattern, $replacement) {
    $text = Get-Content -Raw -LiteralPath $path
    $newText = $text -replace $pattern, $replacement
    if ($newText -ne $text) {
        $backup = Backup-File $path
        Set-Content -LiteralPath $path -Value $newText -NoNewline
        Ok "Updated $path (backup: $backup)"
        return $true
    }
    return $false
}

$projectPath = Join-Path $WorkspacePath $ModelName
$debugPath = Join-Path $projectPath 'Debug_FLASH'
$s32dsExe = Join-Path $S32DSRoot 'eclipse\eclipsec.exe'
$workspacePrefs = Join-Path $S32DSRoot 'eclipse\configuration\.settings\org.eclipse.ui.ide.prefs'
$configFile = Join-Path $ECUCoderRoot 'ec311\s32k311_s32dsconfig.txt'
$projectCproject = Join-Path $projectPath '.cproject'
$templateCproject = Join-Path $ECUCoderRoot 'S32DSU34\.cproject'

Info "ModelName: $ModelName"
Info "WorkspacePath: $WorkspacePath"
Info "S32DSRoot: $S32DSRoot"
Info "ECUCoderRoot: $ECUCoderRoot"
Info "Fix mode: $Fix"

$required = @($WorkspacePath, $S32DSRoot, $ECUCoderRoot, $projectPath, $s32dsExe)
foreach ($path in $required) {
    if (Test-Path -LiteralPath $path) { Ok "Found $path" } else { Fail "Missing $path" }
}

Info "Checking running S32DS/Eclipse processes"
$procs = Get-Process -Name s32ds,eclipsec,eclipse,java,javaw -ErrorAction SilentlyContinue
if ($procs) {
    $procs | Select-Object ProcessName, Id, MainWindowTitle, Path | Format-Table -AutoSize
    Warn "Close S32DS GUI/headless processes before running import/build on this workspace."
} else {
    Ok "No S32DS/Eclipse/Java build processes are running"
}

Info "Checking ECUCoder S32DS config"
if (Test-Path -LiteralPath $configFile) {
    $lines = @(Get-Content -LiteralPath $configFile)
    if ($lines.Count -ge 3) {
        Info "Config line 1 S32DS path: $($lines[0])"
        Info "Config line 2 workspace: $($lines[1])"
        Info "Config line 3 build mode: $($lines[2])"
        if ($lines[2].Trim() -eq '1') {
            Ok "ECUCoder automatic build mode is enabled"
        } else {
            Warn "ECUCoder automatic build mode is not 1"
            if ($Fix) {
                $backup = Backup-File $configFile
                $lines[2] = '1'
                Set-Content -LiteralPath $configFile -Value $lines
                Ok "Set ECUCoder automatic build mode to 1 (backup: $backup)"
            }
        }
    } else {
        Fail "Config file has fewer than 3 lines: $configFile"
    }
} else {
    Fail "Missing ECUCoder config: $configFile"
}

Info "Checking S32DS workspace launcher prefs"
if (Test-Path -LiteralPath $workspacePrefs) {
    $prefs = Get-Content -Raw -LiteralPath $workspacePrefs
    if ($prefs -match 'SHOW_WORKSPACE_SELECTION_DIALOG=false') {
        Ok "S32DS workspace selection dialog is disabled"
    } else {
        Warn "S32DS workspace selection dialog is not disabled"
        if ($Fix) {
            $backup = Backup-File $workspacePrefs
            if ($prefs -match 'SHOW_WORKSPACE_SELECTION_DIALOG=') {
                $prefs = $prefs -replace 'SHOW_WORKSPACE_SELECTION_DIALOG=.*', 'SHOW_WORKSPACE_SELECTION_DIALOG=false'
            } else {
                $prefs = $prefs.TrimEnd() + "`r`nSHOW_WORKSPACE_SELECTION_DIALOG=false`r`n"
            }
            Set-Content -LiteralPath $workspacePrefs -Value $prefs -NoNewline
            Ok "Disabled S32DS workspace selection dialog (backup: $backup)"
        }
    }
} else {
    Warn "Missing prefs file: $workspacePrefs"
    if ($Fix) {
        $dir = Split-Path -Parent $workspacePrefs
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        Set-Content -LiteralPath $workspacePrefs -Value @(
            'MAX_RECENT_WORKSPACES=10'
            ('RECENT_WORKSPACES=' + ($WorkspacePath -replace '\\', '\\' -replace ':', '\:'))
            'RECENT_WORKSPACES_PROTOCOL=3'
            'SHOW_RECENT_WORKSPACES=false'
            'SHOW_WORKSPACE_SELECTION_DIALOG=false'
            'eclipse.preferences.version=1'
        )
        Ok "Created S32DS workspace prefs"
    }
}

Info "Checking .cproject files"
$cprojects = @($projectCproject, $templateCproject) | Where-Object { Test-Path -LiteralPath $_ }
foreach ($cproject in $cprojects) {
    $text = Get-Content -Raw -LiteralPath $cproject
    Info "Inspecting $cproject"
    if ($text -match 'S32K344DEMO2') {
        Warn "Found stale S32K344DEMO2 references"
        if ($Fix) { Replace-InFile $cproject 'S32K344DEMO2' $ModelName | Out-Null }
    } else {
        Ok "No S32K344DEMO2 references"
    }

    $expectedBuildPath = ('buildPath="${workspace_loc:/' + $ModelName + '}/Debug_FLASH"')
    if ($text -match [regex]::Escape($expectedBuildPath)) {
        Ok "Build path uses explicit project name"
    } else {
        Warn "Build path may not use explicit project name"
        if ($Fix) {
            Replace-InFile $cproject 'buildPath="\$\{workspace_loc:/[^}]+}/Debug_FLASH"' $expectedBuildPath | Out-Null
        }
    }

    if ($text -match 'workspacePath="/[^"]+"' -and $text -notmatch ('workspacePath="/' + [regex]::Escape($ModelName) + '"')) {
        Warn "Found refreshScope paths that may not match $ModelName"
        if ($Fix) {
            Replace-InFile $cproject 'workspacePath="/[^"]+"' ('workspacePath="/' + $ModelName + '"') | Out-Null
        }
    }
}

Info "Checking build artifacts"
if (Test-Path -LiteralPath $debugPath) {
    Get-ChildItem -Path (Join-Path $debugPath "$ModelName.*") -ErrorAction SilentlyContinue |
        Select-Object Name, Length, LastWriteTime |
        Sort-Object Name |
        Format-Table -AutoSize
} else {
    Warn "Debug_FLASH directory does not exist: $debugPath"
}

if ($RunBuild) {
    Info "Running headless import"
    & $s32dsExe -consoleLog -nosplash `
        -application org.eclipse.cdt.managedbuilder.core.headlessbuild `
        -data $WorkspacePath `
        -import $projectPath
    Info "Running headless build"
    & $s32dsExe -consoleLog -nosplash `
        -application org.eclipse.cdt.managedbuilder.core.headlessbuild `
        -data $WorkspacePath `
        -build $ModelName
}

$logPath = Join-Path $WorkspacePath '.metadata\.log'
if (Test-Path -LiteralPath $logPath) {
    Info "Recent Eclipse log hints"
    Select-String -Path $logPath -Pattern 'NullPointerException|sources.mk|already exists|does not exist|Build Finished|workspace exited' |
        Select-Object -Last 20 |
        ForEach-Object { $_.Line }
}
