#!/bin/bash
curl -s -X POST 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=AIzaSyCnrWW9ZmGckRP6UtBO0rs2Ar8mAtdFIUU' \
-H 'Content-Type: application/json' \
-d '{"contents": [{"parts": [{"text": "Hi"}]}]}' > test-gemini.json
cat test-gemini.json
