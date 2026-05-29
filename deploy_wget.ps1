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

$cmd1 = $ssh.RunCommand("wget -qO /root/movie-app/server.js https://dpaste.com/H7GABT3YQ.txt")
Write-Host "WGET 1: $($cmd1.Result)"

$cmd2 = $ssh.RunCommand("wget -qO /root/movie-app/public/index.html https://dpaste.com/AFRZ4864W.txt")
Write-Host "WGET 2: $($cmd2.Result)"

$cmd3 = $ssh.RunCommand("pm2 restart movie-app")
Write-Host "PM2 Restart Output: $($cmd3.Result)"

$ssh.Disconnect()
$ssh.Dispose()
