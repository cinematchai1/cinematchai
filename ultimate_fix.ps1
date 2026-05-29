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

$ssh = New-Object Renci.SshNet.SshClient($connInfo)
$ssh.Connect()

$sBytes = [System.IO.File]::ReadAllBytes("C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\server.js")
$sB64 = [System.Convert]::ToBase64String($sBytes)
$ssh.RunCommand("echo `"$sB64`" | base64 -d > /root/movie-app/server.js")

$iBytes = [System.IO.File]::ReadAllBytes("C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\original_index.html")
$iB64 = [System.Convert]::ToBase64String($iBytes)
$ssh.RunCommand("echo `"$iB64`" | base64 -d > /root/movie-app/public/index.html")

$pBytes = [System.IO.File]::ReadAllBytes("C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\patch_v5.js")
$pB64 = [System.Convert]::ToBase64String($pBytes)
$ssh.RunCommand("echo `"$pB64`" | base64 -d > /root/movie-app/patch_v5.js")

$cmd = $ssh.RunCommand("node /root/movie-app/patch_v5.js && pm2 restart movie-app")

Write-Host "DEPLOY OUTPUT:"
Write-Host $cmd.Result
Write-Host "ERRORS:"
Write-Host $cmd.Error

$ssh.Disconnect()
$ssh.Dispose()
