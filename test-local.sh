#!/bin/bash
curl -s -X POST 'http://localhost/api/recommend' \
-H 'Content-Type: application/json' \
-d '{"movie": "The Matrix"}' > local-test.json
cat local-test.json
