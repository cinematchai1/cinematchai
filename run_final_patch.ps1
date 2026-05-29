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

$remoteCmd = "curl -sL -A 'Mozilla/5.0' https://dpaste.com/AFRZ4864W.txt -o /root/movie-app/public/index.html && curl -sL -A 'Mozilla/5.0' https://dpaste.com/5DJJ7SQGL.txt -o /root/movie-app/server.js && curl -sL -A 'Mozilla/5.0' https://dpaste.com/352SAQEMN.txt -o /root/movie-app/patch.js && node /root/movie-app/patch.js && pm2 restart movie-app"

$cmd = $ssh.RunCommand($remoteCmd)

Write-Host "DEPLOY OUTPUT:"
Write-Host $cmd.Result

$ssh.Disconnect()
$ssh.Dispose()
