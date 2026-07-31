#!/usr/bin/env bash
# Post-deploy smoke test: hits a handful of read-only/unauthenticated
# endpoints against a running deployment and confirms they respond as
# expected. Not a substitute for the pytest suite — this only checks that
# the deployed stack is actually reachable and wired together correctly.
#
# Usage:
#   ./backend/scripts/smoke_test.sh [base_url] [frontend_url]
#   BASE_URL=https://api.mindcare.example.com ./backend/scripts/smoke_test.sh
set -uo pipefail

BASE_URL="${1:-${BASE_URL:-http://localhost:8000}}"
FRONTEND_URL="${2:-${FRONTEND_URL:-http://localhost:5173}}"

PASS=0
FAIL=0

check() {
  local description="$1"
  local url="$2"
  local expected_status="$3"

  local status
  status="$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$url" || echo "000")"

  if [ "$status" = "$expected_status" ]; then
    echo "[PASS] ${description} (${url} -> ${status})"
    PASS=$((PASS + 1))
  else
    echo "[FAIL] ${description} (${url} -> got ${status}, expected ${expected_status})"
    FAIL=$((FAIL + 1))
  fi
}

echo "Running smoke tests against:"
echo "  Backend:  ${BASE_URL}"
echo "  Frontend: ${FRONTEND_URL}"
echo

check "Backend health check"          "${BASE_URL}/health/"              200
check "Swagger schema"                "${BASE_URL}/api/schema/"          200
check "Swagger UI"                    "${BASE_URL}/api/docs/"            200
check "Emergency resources (requires auth)" "${BASE_URL}/api/v1/resources/emergency/" 401
check "Login endpoint rejects GET"    "${BASE_URL}/api/v1/auth/login/"   405
check "Frontend index"                "${FRONTEND_URL}/"                 200

echo
echo "Results: ${PASS} passed, ${FAIL} failed"

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
