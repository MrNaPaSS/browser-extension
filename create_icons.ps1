Add-Type -AssemblyName System.Drawing

function New-Icon {
    param([int]$Size, [string]$Path)
    
    $bmp = New-Object System.Drawing.Bitmap($Size, $Size)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = 'AntiAlias'
    
    # Background
    $bgBrush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
        (New-Object System.Drawing.Point(0, 0)),
        (New-Object System.Drawing.Point($Size, $Size)),
        [System.Drawing.Color]::FromArgb(255, 10, 10, 26),
        [System.Drawing.Color]::FromArgb(255, 26, 10, 46)
    )
    $g.FillRectangle($bgBrush, 0, 0, $Size, $Size)
    
    $cx = [float]($Size / 2)
    $cy = [float]($Size / 2)
    $s  = [float]($Size / 128.0)
    
    # Hexagon
    $hexPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(200,0,212,255), [Math]::Max(2*$s,1))
    $r = [float](28 * $s)
    $hexPts = New-Object System.Drawing.PointF[] 6
    for ($i = 0; $i -lt 6; $i++) {
        $a = [Math]::PI / 3 * $i - [Math]::PI / 6
        $hexPts[$i] = [System.Drawing.PointF]::new([float]($cx + $r * [Math]::Cos($a)), [float]($cy + $r * [Math]::Sin($a)))
    }
    $g.DrawPolygon($hexPen, $hexPts)
    $hFill = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(25,0,212,255))
    $g.FillPolygon($hFill, $hexPts)
    
    # Lines
    $lp = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(150,124,58,237), [Math]::Max(1.5*$s, 0.8))
    $nodesX = @(($cx - 38*$s), ($cx + 38*$s), ($cx - 42*$s), ($cx + 42*$s), $cx, $cx)
    $nodesY = @(($cy - 30*$s), ($cy - 30*$s), ($cy + 15*$s), ($cy + 15*$s), ($cy - 45*$s), ($cy + 42*$s))
    
    for ($i = 0; $i -lt 6; $i++) {
        $g.DrawLine($lp, $cx, $cy, [float]$nodesX[$i], [float]$nodesY[$i])
    }
    
    # Dots
    $db = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(220,0,212,255))
    $dr = [float]([Math]::Max(4*$s, 1.5))
    for ($i = 0; $i -lt 6; $i++) {
        $g.FillEllipse($db, [float]($nodesX[$i]-$dr), [float]($nodesY[$i]-$dr), [float]($dr*2), [float]($dr*2))
    }
    
    # Center
    $cBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
    $cr = [float]([Math]::Max(6*$s, 2))
    $g.FillEllipse($cBrush, [float]($cx-$cr), [float]($cy-$cr), [float]($cr*2), [float]($cr*2))
    
    # Chart line
    $chartPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(200,0,255,136), [Math]::Max(2*$s,1))
    $baseY = [float]($cy + 48*$s)
    $chartPts = @(
        [System.Drawing.PointF]::new([float]($cx-40*$s), [float]($baseY+5*$s)),
        [System.Drawing.PointF]::new([float]($cx-25*$s), [float]($baseY-8*$s)),
        [System.Drawing.PointF]::new([float]($cx-10*$s), [float]($baseY+3*$s)),
        [System.Drawing.PointF]::new([float]($cx+5*$s),  [float]($baseY-12*$s)),
        [System.Drawing.PointF]::new([float]($cx+20*$s), [float]($baseY-6*$s)),
        [System.Drawing.PointF]::new([float]($cx+35*$s), [float]($baseY-18*$s))
    )
    $g.DrawLines($chartPen, $chartPts)
    
    # Save
    $bmp.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $bmp.Dispose()
    $bgBrush.Dispose()
    Write-Host "Created: $Path ($Size x $Size)"
}

# Save to TEMP (ASCII-only path) to avoid GDI+ Cyrillic path issues
$tmpDir = Join-Path $env:TEMP "ext_icons"
if (!(Test-Path $tmpDir)) { New-Item -ItemType Directory -Path $tmpDir | Out-Null }

New-Icon -Size 16  -Path (Join-Path $tmpDir "icon16.png")
New-Icon -Size 48  -Path (Join-Path $tmpDir "icon48.png")
New-Icon -Size 128 -Path (Join-Path $tmpDir "icon128.png")

# Copy to project
$destDir = "e:\Расширение для браузера\icons"
Copy-Item (Join-Path $tmpDir "icon16.png")  (Join-Path $destDir "icon16.png")  -Force
Copy-Item (Join-Path $tmpDir "icon48.png")  (Join-Path $destDir "icon48.png")  -Force
Copy-Item (Join-Path $tmpDir "icon128.png") (Join-Path $destDir "icon128.png") -Force

Write-Host "All icons copied to project!"
