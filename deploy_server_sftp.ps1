[System.Reflection.Assembly]::LoadFrom("C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\sshnet\lib\netstandard2.0\Renci.SshNet.dll") | Out-Null

$hostName = "116.203.230.103"
$username = "root"
$password = "MovieApp123!@#"
$remoteDir = "/root/movie-app"
$localFile = "C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\server.js"
$remoteFile = "$remoteDir/server.js"

$connInfo = New-Object Renci.SshNet.PasswordConnectionInfo($hostName, $username, $password)

# Upload using SFTP
$sftp = New-Object Renci.SshNet.SftpClient($connInfo)
$sftp.Connect()
$fileStream = [System.IO.File]::OpenRead($localFile)
$sftp.UploadFile($fileStream, $remoteFile, $true)
$fileStream.Close()
$sftp.Disconnect()

# Restart PM2
$client = New-Object Renci.SshNet.SshClient($connInfo)
$client.Connect()
$cmd = $client.RunCommand("pm2 restart movie-app")
Write-Output $cmd.Result
$client.Disconnect()

Write-Output "server.js deployed via SFTP and PM2 restarted."
