# Fetch real place photos from Wikimedia Commons into Images/places/{slug}.jpg
$ErrorActionPreference = "Stop"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -ErrorAction SilentlyContinue
if (-not $Root) { $Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path }
# Script is under tool/; repo root is parent
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$OutDir = Join-Path $Root "Images\places"
$LogPath = Join-Path $Root "tool\_place-photo-fetch-log.json"
$UA = "KoreaTravelGuidebook/1.0 (educational static site; offline asset mirror; https://github.com/)"

$Places = @(
  @{ slug = "myeongdong"; q = "Myeongdong Seoul street" },
  @{ slug = "gyeongbok"; q = "Gyeongbokgung Palace Geunjeongjeon" },
  @{ slug = "gangnam"; q = "Gangnam Seoul skyline OR Gangnam Station" },
  @{ slug = "hongdae"; q = "Hongdae Seoul Hongik" },
  @{ slug = "itaewon"; q = "Itaewon Seoul" },
  @{ slug = "suwon"; q = "Hwaseong Fortress Suwon" },
  @{ slug = "goyang"; q = "Ilsan Lake Park" },
  @{ slug = "gapyeong"; q = "Nami Island Gapyeong" },
  @{ slug = "haeundae"; q = "Haeundae Beach Busan" },
  @{ slug = "nampo"; q = "Jagalchi Market Busan" },
  @{ slug = "seomyeon"; q = "Seomyeon Busan" },
  @{ slug = "namsan"; q = "N Seoul Tower Namsan" },
  @{ slug = "bukchon"; q = "Bukchon Hanok Village" },
  @{ slug = "insadong"; q = "Insadong Seoul" },
  @{ slug = "dongdaemun"; q = "Dongdaemun Design Plaza DDP" },
  @{ slug = "lotte-tower"; q = "Lotte World Tower Seoul" },
  @{ slug = "songdo"; q = "Songdo Central Park Incheon" },
  @{ slug = "seoraksan"; q = "Seoraksan National Park" },
  @{ slug = "bulguksa"; q = "Bulguksa Temple" },
  @{ slug = "donggung"; q = "Donggung Wolji Pond Gyeongju" },
  @{ slug = "jeonju"; q = "Jeonju Hanok Village" },
  @{ slug = "seongsan"; q = "Seongsan Ilchulbong" },
  @{ slug = "jungmun"; q = "Jungmun Beach Jeju OR Jungmun Seogwipo" },
  @{ slug = "gamcheon"; q = "Gamcheon Culture Village" },
  @{ slug = "haedong"; q = "Haedong Yonggungsa" },
  @{ slug = "imjingak"; q = "Imjingak Paju" },
  @{ slug = "everland"; q = "Everland Yongin amusement" },
  @{ slug = "airport-icn"; q = "Incheon International Airport terminal" },
  @{ slug = "airport-gmp"; q = "Gimpo International Airport" },
  @{ slug = "airport-pus"; q = "Gimhae International Airport Busan" },
  @{ slug = "airport-cju"; q = "Jeju International Airport" },
  @{ slug = "airport-tae"; q = "Daegu International Airport" },
  @{ slug = "airport-cjj"; q = "Cheongju International Airport" },
  @{ slug = "seoul-global-center"; q = "Seoul City Hall OR Seoul Plaza" },
  @{ slug = "tourist-info-myeongdong"; q = "Myeongdong Seoul shopping street" },
  @{ slug = "embassy-us-seoul"; q = "United States Embassy Seoul" },
  @{ slug = "embassy-japan-seoul"; q = "Embassy of Japan Seoul" },
  @{ slug = "embassy-china-seoul"; q = "Chinese Embassy Seoul OR Embassy of China Seoul" },
  @{ slug = "noryangjin-cupbap"; q = "Noryangjin Fish Market" },
  @{ slug = "hangang-yeouido"; q = "Yeouido Hangang Park" },
  @{ slug = "hangang-banpo"; q = "Banpo Bridge Hangang OR Moonlight Rainbow Fountain" },
  @{ slug = "hallasan"; q = "Hallasan Jeju mountain" },
  @{ slug = "cheonjeyeon"; q = "Cheonjeyeon Falls" },
  @{ slug = "biff-square"; q = "BIFF Square Busan" },
  @{ slug = "hwangnidan"; q = "Hwangnidan-gil OR Gyeongju street heritage" },
  @{ slug = "hahoe"; q = "Hahoe Folk Village Andong" },
  @{ slug = "boseong"; q = "Boseong green tea plantation" },
  @{ slug = "suncheon-bay"; q = "Suncheon Bay wetland" },
  @{ slug = "tongyeong"; q = "Tongyeong harbor Korea" },
  @{ slug = "ulsan-daewangam"; q = "Daewangam Park Ulsan" },
  # Lockers: real station/airport photos (place-specific)
  @{ slug = "locker-seoul-station"; q = "Seoul Station building exterior" },
  @{ slug = "locker-yongsan-station"; q = "Yongsan Station Seoul" },
  @{ slug = "locker-busan-station"; q = "Busan Station building" },
  @{ slug = "locker-myeongdong-station"; q = "Myeongdong Station Seoul OR Myeongdong street" },
  @{ slug = "locker-hongdae-station"; q = "Hongik University Station OR Hongdae Seoul" },
  @{ slug = "locker-gangnam-station"; q = "Gangnam Station exit Seoul" },
  @{ slug = "locker-express-bus-terminal"; q = "Seoul Express Bus Terminal OR Express Bus Terminal Seoul" },
  @{ slug = "locker-icn-t1"; q = "Incheon Airport Terminal 1" },
  @{ slug = "locker-icn-t2"; q = "Incheon Airport Terminal 2" },
  @{ slug = "locker-dongdaemun-station"; q = "Dongdaemun History Culture Park OR Dongdaemun Gate" },
  @{ slug = "locker-haeundae-station"; q = "Haeundae Station OR Haeundae Beach" },
  # Ports
  @{ slug = "port-busan"; q = "Busan Port harbor skyline" },
  @{ slug = "port-incheon"; q = "Incheon Port harbor" },
  @{ slug = "port-jeju"; q = "Jeju Port harbor ferry" },
  @{ slug = "port-mokpo"; q = "Mokpo Port harbor" },
  @{ slug = "port-yeosu"; q = "Yeosu harbor Expo OR Yeosu Port" },
  @{ slug = "port-pohang"; q = "Pohang harbor Yeongil Bay OR Pohang Port" }
)

function Get-CommonsFileCandidates([string]$Query) {
  $searchUri = "https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=$([uri]::EscapeDataString($Query))&srnamespace=6&srlimit=12&format=json"
  $search = Invoke-RestMethod -Uri $searchUri -Headers @{ "User-Agent" = $UA } -TimeoutSec 60
  $titles = @($search.query.search | ForEach-Object { $_.title })
  if (-not $titles.Count) { return @() }

  $infoUri = "https://commons.wikimedia.org/w/api.php?action=query&titles=$([uri]::EscapeDataString(($titles -join '|')))&prop=imageinfo&iiprop=url|size|mime|extmetadata&iiurlwidth=1280&format=json"
  # titles with | need different encoding - use POST-like batch via separate calls if needed
  $chunks = @()
  for ($i = 0; $i -lt $titles.Count; $i += 5) {
    $chunk = $titles[$i..([Math]::Min($i + 4, $titles.Count - 1))]
    $joined = ($chunk | ForEach-Object { [uri]::EscapeDataString($_) }) -join "%7C"
    $u = "https://commons.wikimedia.org/w/api.php?action=query&titles=$joined&prop=imageinfo&iiprop=url|size|mime|extmetadata&iiurlwidth=1280&format=json"
    $info = Invoke-RestMethod -Uri $u -Headers @{ "User-Agent" = $UA } -TimeoutSec 60
    foreach ($page in $info.query.pages.PSObject.Properties.Value) {
      if (-not $page.imageinfo) { continue }
      $ii = $page.imageinfo[0]
      if ($ii.mime -notmatch "image/(jpeg|png|webp)") { continue }
      $w = [int]($ii.thumbwidth)
      $h = [int]($ii.thumbheight)
      if (-not $w) { $w = [int]$ii.width }
      if (-not $h) { $h = [int]$ii.height }
      if ($w -lt 400 -or $h -lt 250) { continue }
      $license = ""
      if ($ii.extmetadata -and $ii.extmetadata.LicenseShortName) {
        $license = [string]$ii.extmetadata.LicenseShortName.value
      }
      $url = $ii.thumburl
      if (-not $url) { $url = $ii.url }
      $chunks += [pscustomobject]@{
        title = $page.title
        url = $url
        width = $w
        height = $h
        size = [int64]$ii.size
        mime = $ii.mime
        license = $license
      }
    }
    Start-Sleep -Milliseconds 200
  }
  return $chunks
}

function Pick-Best($cands) {
  if (-not $cands -or $cands.Count -eq 0) { return $null }
  # Prefer landscape-ish JPEGs with free-looking licenses, decent size
  $scored = $cands | ForEach-Object {
    $score = 0
    if ($_.mime -eq "image/jpeg") { $score += 30 }
    if ($_.license -match "CC|Public domain|PD") { $score += 20 }
    if ($_.width -ge 800) { $score += 15 }
    if ($_.width -ge 1200) { $score += 10 }
    $ratio = if ($_.height -gt 0) { $_.width / $_.height } else { 1 }
    if ($ratio -ge 1.1 -and $ratio -le 2.2) { $score += 15 }
    if ($_.title -match "map|logo|icon|flag|svg|diagram|chart|poster|stamp") { $score -= 50 }
    $_ | Add-Member -NotePropertyName score -NotePropertyValue $score -PassThru
  }
  return ($scored | Sort-Object score -Descending | Select-Object -First 1)
}

$results = @()
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

foreach ($p in $Places) {
  Write-Host ("=== {0} :: {1}" -f $p.slug, $p.q)
  $ok = $false
  $err = $null
  $picked = $null
  try {
    $cands = Get-CommonsFileCandidates $p.q
    $picked = Pick-Best $cands
    if (-not $picked) {
      # secondary broader query: first two words of note-like query
      $alt = ($p.q -split " ")[0..1] -join " "
      $cands = Get-CommonsFileCandidates $alt
      $picked = Pick-Best $cands
    }
    if (-not $picked) { throw "No suitable Commons image found" }

    $dest = Join-Path $OutDir ($p.slug + ".jpg")
    $tmp = Join-Path $OutDir ($p.slug + ".download.tmp")
    Invoke-WebRequest -Uri $picked.url -OutFile $tmp -Headers @{ "User-Agent" = $UA } -TimeoutSec 120
    $len = (Get-Item $tmp).Length
    if ($len -lt 15000) { throw "Downloaded file too small ($len bytes): $($picked.title)" }

    # Convert PNG/WebP to JPEG via .NET if needed; else rename
    $bytes = [System.IO.File]::ReadAllBytes($tmp)
    $isJpeg = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xD8)
    if (-not $isJpeg) {
      Add-Type -AssemblyName System.Drawing
      $img = [System.Drawing.Image]::FromFile($tmp)
      $jpegCodec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" }
      $ep = New-Object System.Drawing.Imaging.EncoderParameters(1)
      $ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, 85L)
      $img.Save($dest, $jpegCodec, $ep)
      $img.Dispose()
      Remove-Item $tmp -Force
    } else {
      Move-Item -Force $tmp $dest
    }
    $finalLen = (Get-Item $dest).Length
    if ($finalLen -lt 15000) { throw "Final JPEG too small ($finalLen)" }
    Write-Host ("  OK {0} bytes <- {1} ({2})" -f $finalLen, $picked.title, $picked.license)
    $ok = $true
  } catch {
    $err = $_.Exception.Message
    Write-Host ("  FAIL: {0}" -f $err)
    if (Test-Path (Join-Path $OutDir ($p.slug + ".download.tmp"))) {
      Remove-Item (Join-Path $OutDir ($p.slug + ".download.tmp")) -Force -ErrorAction SilentlyContinue
    }
  }
  $results += [pscustomobject]@{
    slug = $p.slug
    ok = $ok
    title = if ($picked) { $picked.title } else { $null }
    license = if ($picked) { $picked.license } else { $null }
    url = if ($picked) { $picked.url } else { $null }
    error = $err
  }
  Start-Sleep -Milliseconds 350
}

$results | ConvertTo-Json -Depth 4 | Set-Content -Path $LogPath -Encoding UTF8
$okCount = ($results | Where-Object { $_.ok }).Count
$failCount = ($results | Where-Object { -not $_.ok }).Count
Write-Host ""
Write-Host ("DONE ok={0} fail={1} log={2}" -f $okCount, $failCount, $LogPath)
$results | Where-Object { -not $_.ok } | ForEach-Object { Write-Host ("MISSING: {0} — {1}" -f $_.slug, $_.error) }
