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
SELECT omdb_data FROM movies_cache LIMIT 1;
"@
$base64Sql = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($sql))

$ssh.RunCommand("echo '$base64Sql' | base64 -d > /tmp/query.sql") | Out-Null
$res = $ssh.RunCommand("sudo -u postgres psql -d cinematch_db -f /tmp/query.sql")
Write-Host "DB OMDB DATA:"
Write-Host $res.Result

$ssh.Disconnect()
