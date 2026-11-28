param(
    [string]$Action    = "menu",
    [string]$RootDir   = "",
    [string]$AssetsDir = "",
    [string]$DocsDir   = "",
    [string]$DownloadsDir = "",
    [string]$Paths     = "",
    [string]$Urls      = ""
)

# ============================================================
#  Edukasi Recycle Bin - Dev Menu (PS1)
#  Tugasnya:
#    -Action menu     -> gambar menu
#    -Action explorer -> buka Explorer 1 jendela 4 tab (root, assets, docs, downloads)
#                        dengan deteksi anti-duplikat (reuse jendela jika sudah ada)
#    -Action browser  -> buka URL (Gemini, ChatGPT) yang belum terbuka di browser
# ============================================================

function Get-BraveExePath {
    $candidates = @(
        "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        (Join-Path $env:LOCALAPPDATA "BraveSoftware\Brave-Browser\Application\brave.exe"),
        "C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"
    )
    return ($candidates | Where-Object { Test-Path $_ } | Select-Object -First 1)
}

# -- Fokuskan jendela browser yang cocok dengan URL -------------------------
function Focus-BrowserWindow([string]$url) {
    if (-not ("BrowserWinApi" -as [type])) {
        Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class BrowserWinApi {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern void SwitchToThisWindow(IntPtr h, bool f);
}
"@ -ErrorAction SilentlyContinue
    }

    $browsers = @(Get-Process brave, chrome, msedge -ErrorAction SilentlyContinue |
        Where-Object { $_.MainWindowHandle -ne 0 })
    if ($browsers.Count -eq 0) { return }

    $hint = ""
    if ($url -like "*gemini.google.com*") { $hint = "gemini" }
    elseif ($url -like "*chatgpt.com*")  { $hint = "chatgpt" }

    $target = $null
    if ($hint) {
        $target = $browsers |
            Where-Object { $_.MainWindowTitle -and $_.MainWindowTitle.ToLowerInvariant().Contains($hint) } |
            Select-Object -First 1
    }
    if (-not $target) { $target = $browsers | Select-Object -First 1 }

    $h = [IntPtr]$target.MainWindowHandle
    [void][BrowserWinApi]::ShowWindow($h, 9)          # SW_RESTORE
    [BrowserWinApi]::SwitchToThisWindow($h, $true)
    [void][BrowserWinApi]::SetForegroundWindow($h)
}

function Get-OpenBrowserSignals {
    $signals = New-Object System.Collections.Generic.List[string]

    # 1) Ambil semua MainWindowTitle dari proses browser yang sedang berjalan
    Get-Process brave, chrome, msedge -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.MainWindowTitle) { [void]$signals.Add($_.MainWindowTitle.ToLowerInvariant()) }
    }

    # 2) Ambil judul seluruh tab (termasuk tab background) & isi address bar lewat UIAutomation
    try {
        Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes -ErrorAction SilentlyContinue
        $root = [System.Windows.Automation.AutomationElement]::RootElement
        if ($root) {
            $classCond = New-Object System.Windows.Automation.PropertyCondition(
                [System.Windows.Automation.AutomationElement]::ClassNameProperty,
                "Chrome_WidgetWin_1"
            )
            $wins = $root.FindAll([System.Windows.Automation.TreeScope]::Children, $classCond)
            $tabCond = New-Object System.Windows.Automation.PropertyCondition(
                [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
                [System.Windows.Automation.ControlType]::TabItem
            )
            $editCond = New-Object System.Windows.Automation.PropertyCondition(
                [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
                [System.Windows.Automation.ControlType]::Edit
            )

            for ($i = 0; $i -lt $wins.Count; $i++) {
                $w = $wins.Item($i)
                $wName = $w.Current.Name
                if ($wName) {
                    if ($wName -match "Private|Incognito|InPrivate") { continue }
                    [void]$signals.Add($wName.ToLowerInvariant())
                }

                $tabs = $w.FindAll([System.Windows.Automation.TreeScope]::Descendants, $tabCond)
                for ($t = 0; $t -lt $tabs.Count; $t++) {
                    $tName = $tabs.Item($t).Current.Name
                    if ($tName) { [void]$signals.Add($tName.ToLowerInvariant()) }
                }

                $edits = $w.FindAll([System.Windows.Automation.TreeScope]::Descendants, $editCond)
                for ($e = 0; $e -lt $edits.Count; $e++) {
                    $vp = $null
                    if ($edits.Item($e).TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern, [ref]$vp)) {
                        $val = $vp.Current.Value
                        if ($val) { [void]$signals.Add($val.ToLowerInvariant()) }
                    }
                }
            }
        }
    } catch {}

    return $signals
}

function Test-BrowserUrlAlreadyOpen([string]$url) {
    if (-not $url) { return $false }
    $u = $url.Trim().ToLowerInvariant()
    $signals = Get-OpenBrowserSignals
    if ($signals.Count -eq 0) { return $false }

    $keywords = New-Object System.Collections.Generic.List[string]
    [void]$keywords.Add($u.TrimEnd('/'))
    [void]$keywords.Add(($u -replace '^https?://', '').TrimEnd('/'))

    if ($u -like "*gemini.google.com*") {
        # Gemini chat / notebook memakai ID unik di URL -> jadikan keyword utama
        if ($u -match '/(?:app|notebook)/([0-9a-f-]{36})') {
            [void]$keywords.Add($Matches[1])
        }
        if ($u -like "*/notebook/*") {
            [void]$keywords.Add("gemini.google.com/notebook")
        }
        [void]$keywords.Add("gemini.google.com")
        [void]$keywords.Add("google gemini")
    }
    if ($u -like "*chatgpt.com*") {
        [void]$keywords.Add("6af25e4c-74c0-83ec-8f0a-a2aa0009e4c8")
        [void]$keywords.Add("chatgpt.com")
    }

    foreach ($sig in $signals) {
        foreach ($kw in $keywords) {
            if ($kw -and $sig.Contains($kw)) {
                return $true
            }
        }
    }
    return $false
}

# -- EXPLORER: 1 jendela, 3 tab (root, assets, docs) -----------
if ($Action -eq "explorer" -or $Action -eq "tabs") {
    Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes -ErrorAction SilentlyContinue
    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class WinApi {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
    [DllImport("user32.dll")] public static extern void SwitchToThisWindow(IntPtr h, bool f);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern IntPtr GetAncestor(IntPtr h, uint f);
}
"@ -ErrorAction SilentlyContinue

    if ($Paths) {
        $items = @($Paths -split '\|' | Where-Object { $_ -and (Test-Path $_) })
    } else {
        $items = @($RootDir, $AssetsDir, $DocsDir, $DownloadsDir) | Where-Object { $_ -and (Test-Path $_) }
    }
    if ($items.Count -eq 0) { exit 0 }

    $shell = New-Object -ComObject Shell.Application

    function ConvertTo-PathKey([string]$value) {
        if (-not $value) { return '' }
        try {
            if ($value -like 'file:*') { $value = ([uri]$value).LocalPath }
            return ([IO.Path]::GetFullPath($value)).TrimEnd('\').ToLowerInvariant()
        } catch { return $value.TrimEnd('\','/').ToLowerInvariant() }
    }

    function Get-TabsOf([int64]$h) {
        @($shell.Windows() | Where-Object {
            try { [int64]$_.HWND -eq $h } catch { $false }
        })
    }

    function Navigate-Tab($tab, [string]$path) {
        $want = ConvertTo-PathKey $path
        for ($i = 0; $i -lt 25; $i++) {
            try {
                $tab.Navigate2($path)
                for ($w = 0; $w -lt 15; $w++) {
                    Start-Sleep -Milliseconds 120
                    if ((ConvertTo-PathKey $tab.LocationURL) -eq $want) { return $true }
                }
            } catch { }
            Start-Sleep -Milliseconds 150
        }
        return $false
    }

    function Add-ExplorerTab([int64]$windowHwnd, [string]$targetPath) {
        $winEl = [System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]$windowHwnd)
        if (-not $winEl) { return $false }

        $addCond = New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::AutomationIdProperty, 'AddButton')
        $addBtn = $null
        for ($i = 0; $i -lt 30 -and -not $addBtn; $i++) {
            $addBtn = $winEl.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $addCond)
            if (-not $addBtn) { Start-Sleep -Milliseconds 150 }
        }
        if (-not $addBtn) { return $false }

        $tabsBefore = @(Get-TabsOf $windowHwnd)
        $countBefore = $tabsBefore.Count

        try {
            $addBtn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
        } catch { return $false }

        $newTab = $null
        for ($i = 0; $i -lt 40 -and -not $newTab; $i++) {
            Start-Sleep -Milliseconds 150
            $tabsNow = @(Get-TabsOf $windowHwnd)
            if ($tabsNow.Count -gt $countBefore) {
                $newTab = $tabsNow[$tabsNow.Count - 1]
            }
        }
        if (-not $newTab) { return $false }
        return (Navigate-Tab $newTab $targetPath)
    }

    $rootKey = ConvertTo-PathKey $items[0]

    # Cek apakah sudah ada jendela Explorer yang membuka tab RootDir
    $existingRootTab = $shell.Windows() | Where-Object {
        try { (ConvertTo-PathKey $_.LocationURL) -eq $rootKey } catch { $false }
    } | Select-Object -First 1

    $hwnd = [int64]0

    if ($existingRootTab) {
        $hwnd = [int64]$existingRootTab.HWND
        $rootWin = [WinApi]::GetAncestor([IntPtr]$hwnd, 2)
        if ($rootWin -eq [IntPtr]::Zero) { $rootWin = [IntPtr]$hwnd }
        [void][WinApi]::ShowWindow($rootWin, 9)
        [WinApi]::SwitchToThisWindow($rootWin, $true)
        [void][WinApi]::SetForegroundWindow($rootWin)

        # Pastikan tab yang sudah terbuka urutannya: 1) RootDir, 2) AssetsDir, 3) DocsDir
        $currentTabs = @(Get-TabsOf $hwnd)
        for ($idx = 0; $idx -lt $items.Count; $idx++) {
            $wantPath = $items[$idx]
            $wantKey  = ConvertTo-PathKey $wantPath
            if ($idx -lt $currentTabs.Count) {
                $curKey = ConvertTo-PathKey $currentTabs[$idx].LocationURL
                if ($curKey -ne $wantKey) {
                    [void](Navigate-Tab $currentTabs[$idx] $wantPath)
                }
            } else {
                if (-not (Add-ExplorerTab $hwnd $wantPath)) {
                    Start-Process "explorer.exe" -ArgumentList ('"' + $wantPath + '"')
                }
            }
        }
        exit 0
    }

    # Belum ada jendela RootDir -> buka SATU jendela Explorer baru
    $beforeHwnds = @($shell.Windows() | ForEach-Object {
        try { [int64]$_.HWND } catch { 0 }
    })

    $exe = Join-Path $env:WINDIR "explorer.exe"
    Start-Process -FilePath $exe -ArgumentList "/n" | Out-Null

    for ($i = 0; $i -lt 60 -and $hwnd -eq 0; $i++) {
        Start-Sleep -Milliseconds 200
        foreach ($w in $shell.Windows()) {
            try {
                if ($beforeHwnds -contains [int64]$w.HWND) { continue }
                $hwnd = [int64]$w.HWND
                break
            } catch { }
        }
    }

    if ($hwnd -eq 0) {
        foreach ($p in $items) {
            Start-Process "explorer.exe" -ArgumentList ('"' + $p + '"')
            Start-Sleep -Milliseconds 400
        }
        exit 0
    }

    # Tab 1 -> RootDir
    $tabs = @()
    for ($i = 0; $i -lt 40 -and $tabs.Count -eq 0; $i++) {
        Start-Sleep -Milliseconds 200
        $tabs = @(Get-TabsOf $hwnd)
    }
    if ($tabs.Count -gt 0) {
        [void](Navigate-Tab $tabs[0] $items[0])
    }

    # Tab 2 -> AssetsDir, Tab 3 -> DocsDir
    for ($n = 1; $n -lt $items.Count; $n++) {
        if (-not (Add-ExplorerTab $hwnd $items[$n])) {
            Start-Process "explorer.exe" -ArgumentList ('"' + $items[$n] + '"')
        }
    }

    $rootWin = [WinApi]::GetAncestor([IntPtr]$hwnd, 2)
    if ($rootWin -eq [IntPtr]::Zero) { $rootWin = [IntPtr]$hwnd }
    [void][WinApi]::ShowWindow($rootWin, 9)
    [WinApi]::SwitchToThisWindow($rootWin, $true)
    [void][WinApi]::SetForegroundWindow($rootWin)

    exit 0
}

# -- BROWSER: buka URL yang belum terbuka ---------------------
if ($Action -eq "browser") {
    if (-not $Urls) { exit 0 }

    $braveExe = Get-BraveExePath
    Start-Sleep -Milliseconds 400

    foreach ($url in ($Urls -split ',')) {
        $url = $url.Trim()
        if (-not $url) { continue }

        if (Test-BrowserUrlAlreadyOpen $url) {
            Write-Host "  [~] Sudah terbuka: $url"
            Focus-BrowserWindow $url
        } else {
            if ($braveExe) {
                Start-Process -FilePath $braveExe -ArgumentList @("`"$url`"")
            } else {
                Start-Process $url
            }
            Write-Host "  [+] Buka: $url"
            Start-Sleep -Milliseconds 700
        }
    }
    exit 0
}

# -- MENU: gambar tampilan -------------------------------------
$script:W = 62

function Sep   { Write-Host ("  +" + ("-" * ($script:W + 2)) + "+") -ForegroundColor DarkCyan }
function Blank { Write-Host ("  |" + (" " * ($script:W + 2)) + "|") -ForegroundColor DarkCyan }

function Row($text, $color = "White") {
    if ($text.Length -gt $script:W) { $text = $text.Substring(0, $script:W - 3) + '...' }
    $pad = $script:W - $text.Length
    Write-Host "  |" -NoNewline -ForegroundColor DarkCyan
    Write-Host (" " + $text + (" " * $pad) + " ") -NoNewline -ForegroundColor $color
    Write-Host "|" -ForegroundColor DarkCyan
}

function RowSub($text) { Row $text "DarkGray" }

if ($Action -ne "menu") { exit 0 }

Clear-Host
Write-Host ""
Sep
Row "EDUKASI RECYCLE BIN  |  Construct 2 r262 (1280 x 720)" "Cyan"
Sep
Blank
Row "[1]  Buka Semua          (Construct 2, Tab WT, Explorer, Web)" "Green"
RowSub "     Construct 2, OpenCode, OMP, Root CMD, Explorer, Browser"
Row "[2]  Construct 2         (D:\Apps\Construct 2\Construct2.exe)" "Cyan"
Row "[3]  Browser AI          (Tab Gemini + Tab ChatGPT)" "Magenta"
Row "[4]  File Explorer [E]   (root, assets, docs, Downloads)" "Yellow"
Row "[5]  Hapus Background    (GUI PNG transparan & Auto-Slice)" "White"
Row "[6]  Tab Terminal Baru   (OpenCode, OMP, Root CMD di WT ini)" "White"
Row "[7]  Konversi Audio WAV  (GUI MP3/M4A/OGG -> WAV Construct 2)" "Yellow"
Row "[8]  Konversi Hitam-Putih (Locked Grayscale untuk UI game)" "Gray"
Blank
Row "[0]  Keluar              (jendela yang terbuka tetap aman)" "Red"
Blank
Sep
Write-Host "  Tip: Salin teks perintah di tiap tab, tempel, lalu ENTER." -ForegroundColor DarkGray
Write-Host ""
