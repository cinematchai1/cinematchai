Set objShell = WScript.CreateObject("WScript.Shell")
objShell.Run "C:\Users\fjpp8\.gemini\antigravity\scratch\putty\pscp.exe -pw 9pNMt43iFAaPKuCWqqtK C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\server.js root@116.203.230.103:/root/movie-app/server.js"
WScript.Sleep 1000
objShell.SendKeys "y"
objShell.SendKeys "{ENTER}"
