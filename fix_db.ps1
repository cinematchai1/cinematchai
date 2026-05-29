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

$sql = @"
GRANT ALL PRIVILEGES ON TABLE movies_cache TO cinematch_user;
GRANT USAGE, SELECT ON SEQUENCE movies_cache_id_seq TO cinematch_user;
"@
$base64Sql = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($sql))

$ssh.RunCommand("echo '$base64Sql' | base64 -d > /tmp/grant.sql") | Out-Null
$res = $ssh.RunCommand("sudo -u postgres psql -d cinematch_db -f /tmp/grant.sql")
Write-Host $res.Result
Write-Host $res.Error

# Let's also check the remote server.js
$res2 = $ssh.RunCommand("head -n 20 /root/movie-app/server.js")
Write-Host "REMOTE HEAD:"
Write-Host $res2.Result

$ssh.Disconnect()
