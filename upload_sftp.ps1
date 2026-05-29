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

$sftp = New-Object Renci.SshNet.SftpClient($connInfo)
$sftp.Connect()

$localDir = "C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app"

$fs = [System.IO.File]::OpenRead("$localDir\original_index.html")
$sftp.UploadFile($fs, "/root/movie-app/public/index.html", $true)
$fs.Close()

$fs = [System.IO.File]::OpenRead("$localDir\server.js")
$sftp.UploadFile($fs, "/root/movie-app/server.js", $true)
$fs.Close()

$fs = [System.IO.File]::OpenRead("$localDir\patch_v5.js")
$sftp.UploadFile($fs, "/root/movie-app/patch_v5.js", $true)
$fs.Close()

$sftp.Disconnect()
$sftp.Dispose()

$ssh = New-Object Renci.SshNet.SshClient($connInfo)
$ssh.Connect()
$cmd = $ssh.RunCommand("cd /root/movie-app && node patch_v5.js && pm2 restart movie-app")
Write-Host "DEPLOY OUTPUT:"
Write-Host $cmd.Result
Write-Host "ERRORS:"
Write-Host $cmd.Error
$ssh.Disconnect()
$ssh.Dispose()
