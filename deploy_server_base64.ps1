[System.Reflection.Assembly]::LoadFrom("C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\sshnet\lib\netstandard2.0\Renci.SshNet.dll") | Out-Null

$hostName = "116.203.230.103"
$username = "root"
$password = "MovieApp123!@#"
$remoteDir = "/root/movie-app"
$localFile = "C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\server.js"

$connInfo = New-Object Renci.SshNet.PasswordConnectionInfo($hostName, $username, $password)
$client = New-Object Renci.SshNet.SshClient($hostName, $username, $password)
$client.Connect()

$fileBytes = [System.IO.File]::ReadAllBytes($localFile)
$base64 = [System.Convert]::ToBase64String($fileBytes)

$cmdText = "echo '$base64' | base64 -d > $remoteDir/server.js && pm2 restart movie-app"
$cmd = $client.RunCommand($cmdText)
Write-Output $cmd.Result

$client.Disconnect()
Write-Output "server.js deployed and PM2 restarted."
