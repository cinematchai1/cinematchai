[System.Reflection.Assembly]::LoadFrom("C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\sshnet\lib\netstandard2.0\Renci.SshNet.dll")

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

# 2. Create session table by echoing to a sql file and executing it
$sql = @"
CREATE TABLE IF NOT EXISTS "session" (
  "sid" varchar NOT NULL COLLATE "default",
  "sess" json NOT NULL,
  "expire" timestamp(6) NOT NULL
);
DO `$`$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'session_pkey'
  ) THEN
    ALTER TABLE "session" ADD CONSTRAINT "session_pkey" PRIMARY KEY ("sid") NOT DEFERRABLE INITIALLY IMMEDIATE;
  END IF;
END `$`$;
CREATE INDEX IF NOT EXISTS "IDX_session_expire" ON "session" ("expire");
"@

# encode base64 locally
$bytes = [System.Text.Encoding]::UTF8.GetBytes($sql)
$b64 = [System.Convert]::ToBase64String($bytes)

$ssh.RunCommand("echo -n `"$b64`" | base64 -d > /root/movie-app/session.sql")
$cmd2 = $ssh.RunCommand("PGPASSWORD=cinematch_pass psql -h 127.0.0.1 -U cinematch_user -d cinematch_db -f /root/movie-app/session.sql")

Write-Host "Result:"
Write-Host $cmd2.Result
Write-Host "Error:"
Write-Host $cmd2.Error

$ssh.Disconnect()
$ssh.Dispose()
