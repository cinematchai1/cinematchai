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
DROP TABLE IF EXISTS movies_cache;
CREATE TABLE movies_cache (
    imdb_id VARCHAR(20) NOT NULL,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    title VARCHAR(255),
    type VARCHAR(20),
    tmdb_data JSONB,
    omdb_data JSONB,
    cinemeta_data JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (imdb_id, language)
);
GRANT ALL PRIVILEGES ON TABLE movies_cache TO cinematch_user;
"@

$base64Sql = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($sql))

$ssh.RunCommand("echo '$base64Sql' | base64 -d > /tmp/migrate.sql") | Out-Null
$res = $ssh.RunCommand("sudo -u postgres psql -d cinematch_db -f /tmp/migrate.sql")
Write-Host $res.Result
Write-Host $res.Error

$ssh.Disconnect()
