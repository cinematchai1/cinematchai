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

# Read the local file and convert to base64
$bytes = [System.IO.File]::ReadAllBytes("C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\patch_v5.js")
$b64 = [System.Convert]::ToBase64String($bytes)

# Send to server and decode
$cmd1 = $ssh.RunCommand("echo `"$b64`" | base64 -d > /root/movie-app/patch_v5.js")
$cmd2 = $ssh.RunCommand("node /root/movie-app/patch_v5.js && pm2 restart movie-app")

Write-Host "DEPLOY OUTPUT:"
Write-Host $cmd2.Result
Write-Host "ERRORS:"
Write-Host $cmd2.Error

$ssh.Disconnect()
$ssh.Dispose()
