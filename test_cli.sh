#!/bin/bash
cd /app/backend

# Test with a simple question via stdin
echo "What is the real remedy?" | timeout 60 python3 ambedkar_qa_cli.py <<EOF
What is the real remedy?
exit
EOF
