#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://localhost:8000"

echo "=== Testing Complete Flow ==="

# 1. Create Project
echo "1. Creating project..."
PROJECT_RESP=$(curl -s -X POST "$BASE_URL/api/projects" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Project '$(date +%s)'"}')
PROJECT_ID=$(echo "$PROJECT_RESP" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "   Project ID: $PROJECT_ID"

# 2. Create Document
echo "2. Creating document..."
DOC_RESP=$(curl -s -X POST "$BASE_URL/api/documents" \
  -H "Content-Type: application/json" \
  -d "{\"project_id\": \"$PROJECT_ID\", \"name\": \"Test Document\", \"ocr_url\": \"mock\"}")
DOC_ID=$(echo "$DOC_RESP" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "   Document ID: $DOC_ID"

# 3. Upload Sample JSON
echo "3. Uploading sample JSON..."
curl -s -X POST "$BASE_URL/api/documents/$DOC_ID/sample-json" \
  -F "sample=@demo.json" > /dev/null
echo "   Sample uploaded"

# 4. Get text fields
echo "4. Getting text fields..."
FIELDS=$(curl -s "$BASE_URL/api/documents/$DOC_ID/text-fields")
echo "   Fields: $FIELDS"

# 5. Upload a file (create a dummy file)
echo "5. Uploading file..."
echo "dummy pdf content" > /tmp/test_file.pdf
UPLOAD_RESP=$(curl -s -X POST "$BASE_URL/api/documents/$DOC_ID/upload" \
  -F "file=@/tmp/test_file.pdf")
UPLOAD_ID=$(echo "$UPLOAD_RESP" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "   Upload ID: $UPLOAD_ID"

# 6. Upload user input JSON
echo "6. Uploading user input..."
USER_INPUT='{"contract_no":"01/VIETTEL-ZTE/2024","contract_date":"27/09/2024","project_name":"Test Project","bidding_pack":"Test Pack","party_a_name":"VIETTEL GROUP"}'
echo "$USER_INPUT" > /tmp/user_input.json
curl -s -X POST "$BASE_URL/api/documents/$UPLOAD_ID/user-input" \
  -F "form_json=@/tmp/user_input.json" > /dev/null
echo "   User input uploaded"

# 7. Start validation
echo "7. Starting validation..."
JOB_RESP=$(curl -s -X POST "$BASE_URL/api/validation/run" \
  -H "Content-Type: application/json" \
  -d "{\"document_id\": \"$DOC_ID\"}")
JOB_ID=$(echo "$JOB_RESP" | grep -o '"job_id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "   Job ID: $JOB_ID"

# 8. Wait for validation to complete
echo "8. Waiting for validation..."
for i in {1..30}; do
  sleep 2
  STATUS_RESP=$(curl -s "$BASE_URL/api/validation/status/$JOB_ID")
  STATUS=$(echo "$STATUS_RESP" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)
  echo "   Status: $STATUS (attempt $i)"
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi
done

# 9. Get results
echo "9. Getting results..."
RESULT=$(curl -s "$BASE_URL/api/validation/result/$JOB_ID")
echo "   Result: $RESULT" | head -20

# 10. Get upload results
echo "10. Getting upload results..."
UPLOAD_RESULTS=$(curl -s "$BASE_URL/api/validation/upload/$UPLOAD_ID/results")
echo "   Upload results: $UPLOAD_RESULTS" | head -20

echo "=== Test Complete ==="

