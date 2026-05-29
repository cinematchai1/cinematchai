Add-Type -Path "C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\sshnet\lib\net462\Renci.SshNet.dll"

$hostName = "116.203.230.103"
$username = "root"
$password = "MovieApp123!@#"

$keyboardAuth = New-Object Renci.SshNet.KeyboardInteractiveAuthenticationMethod($username)
$keyboardAuth.add_AuthenticationPrompt({
    param($sender, $e)
    foreach ($prompt in $e.Prompts) {
        if ($prompt.Request.IndexOf("Password", [System.StringComparison]::InvariantCultureIgnoreCase) -ne -1) {
            $prompt.Response = $password
        }
    }
})

$passwordAuth = New-Object Renci.SshNet.PasswordAuthenticationMethod($username, $password)
$connInfo = New-Object Renci.SshNet.ConnectionInfo($hostName, 22, $username, $passwordAuth, $keyboardAuth)

Write-Host "Connecting SFTP..."
$sftp = New-Object Renci.SshNet.SftpClient($connInfo)
$sftp.Connect()

$file1 = [System.IO.File]::OpenRead("C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\server.js")
$sftp.UploadFile($file1, "/root/movie-app/server.js", $true)
$file1.Close()
Write-Host "Uploaded server.js"

$file2 = [System.IO.File]::OpenRead("C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\public\index.html")
$sftp.UploadFile($file2, "/root/movie-app/public/index.html", $true)
$file2.Close()
Write-Host "Uploaded index.html"

$sftp.Disconnect()
$sftp.Dispose()

Write-Host "Connecting SSH to restart PM2..."
$ssh = New-Object Renci.SshNet.SshClient($connInfo)
$ssh.Connect()
$cmd = $ssh.RunCommand("pm2 restart movie-app")
Write-Host "PM2 Restart Output: $($cmd.Result)"
$ssh.Disconnect()
$ssh.Dispose()
