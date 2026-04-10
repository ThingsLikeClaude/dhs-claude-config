$wake = New-Object System.Media.SoundPlayer (Join-Path $env:USERPROFILE '.claude\wake.wav')
$wake.PlaySync()
Start-Sleep -Milliseconds 1500
$notify = New-Object System.Media.SoundPlayer (Join-Path $env:USERPROFILE '.claude\notify-sound.wav')
$notify.PlaySync()
