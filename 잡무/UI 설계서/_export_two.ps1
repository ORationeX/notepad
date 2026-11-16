$ppt = New-Object -ComObject PowerPoint.Application
$path = "d:\유틸\잡무\UI 설계서\UI설계서_물류창고관리 고도화&운영_V0.2_20261116.pptx"
$out = "d:\유틸\잡무\UI 설계서\_preview"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$pres = $ppt.Presentations.Open($path, $true, $false, $false)
$pres.Slides.Item(3).Export("$out\s3.png", "PNG", 1600, 1108)
$pres.Slides.Item(10).Export("$out\s10.png", "PNG", 1600, 1108)
$pres.Close()
$ppt.Quit()
Write-Output "done"
