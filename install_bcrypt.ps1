[System.Reflection.Assembly]::LoadFrom("C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\sshnet\lib\netstandard2.0\Renci.SshNet.dll")

$hostName = "116.203.230.103"
$username = "root"
$password = "MovieApp123!@#"

$keyboardAuth = New-Object Renci.SshNet.KeyboardInteractiveAuthenticationMethod($username)
$keyboardAuth.add_AuthenticationPrompt({
    param($sender, $e)
    foreach ($prompt in $e.Prompts) {
        if ($prompt.Request -match "Password:") {
            $prompt.Response = $password
        }
    }
})

$passwordAuth = New-Object Renci.SshNet.PasswordAuthenticationMethod($username, $password)
$connInfo = New-Object Renci.SshNet.ConnectionInfo($hostName, 22, $username, $passwordAuth, $keyboardAuth)
$ssh = New-Object Renci.SshNet.SshClient($connInfo)
$ssh.Connect()

$cmd = $ssh.RunCommand("cd /root/movie-app && npm install bcrypt && pm2 restart movie-app")
Write-Host "OUTPUT:"
Write-Host $cmd.Result

$ssh.Disconnect()
