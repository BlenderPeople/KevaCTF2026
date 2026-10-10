#!/bin/sh
set -e

GRAFANA_URL="http://clicker_task_grafana:3000"
ADMIN_USER="${GF_SECURITY_ADMIN_USER:-clicker_root}"
ADMIN_PASSWORD="${GF_SECURITY_ADMIN_PASSWORD:-stay_out_of_prod_dashboards_2026}"
VIEWER_USER="${GRAFANA_VIEWER_USER:-ops_viewer}"
VIEWER_PASSWORD="${GRAFANA_VIEWER_PASSWORD:-clk_logs_are_not_for_users}"
VIEWER_EMAIL="${VIEWER_USER}@ctf.local"

# Wait for Grafana to be ready
echo "Waiting for Grafana to be ready at ${GRAFANA_URL}..."
attempts=0
while [ $attempts -lt 120 ]; do
  if curl -fsS "${GRAFANA_URL}/api/health" >/dev/null 2>&1; then
    echo "Grafana is ready"
    break
  fi
  attempts=$((attempts + 1))
  sleep 1
done

if [ $attempts -eq 120 ]; then
  echo "Timeout waiting for Grafana"
  exit 1
fi

# Test admin auth
echo "Testing admin authentication..."
if ! curl -fsS -u "${ADMIN_USER}:${ADMIN_PASSWORD}" "${GRAFANA_URL}/api/admin/settings" >/dev/null 2>&1; then
  echo "ERROR: Cannot authenticate as admin with provided credentials"
  exit 1
fi

echo "Admin auth OK"

# Create or update viewer user
echo "Creating/updating viewer user: ${VIEWER_USER}"

# Try to create user (may fail if already exists, which is OK)
curl -fsS -u "${ADMIN_USER}:${ADMIN_PASSWORD}" \
  -X POST \
  -H "Content-Type: application/json" \
  "${GRAFANA_URL}/api/admin/users" \
  -d "{\"name\":\"Clicker Viewer\",\"email\":\"${VIEWER_EMAIL}\",\"login\":\"${VIEWER_USER}\",\"password\":\"${VIEWER_PASSWORD}\"}" \
  >/dev/null 2>&1 || echo "User creation skipped (may already exist)"

# Get user ID
echo "Looking up user ID for ${VIEWER_USER}..."
USER_ID=$(curl -fsS -u "${ADMIN_USER}:${ADMIN_PASSWORD}" \
  "${GRAFANA_URL}/api/users/lookup?loginOrEmail=${VIEWER_USER}" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

if [ -z "$USER_ID" ]; then
  echo "ERROR: Could not find user ID for ${VIEWER_USER}"
  exit 1
fi

echo "Found user ID: ${USER_ID}"

# Set user role to Viewer
echo "Setting user role to Viewer..."
curl -fsS -u "${ADMIN_USER}:${ADMIN_PASSWORD}" \
  -X PATCH \
  -H "Content-Type: application/json" \
  "${GRAFANA_URL}/api/orgs/1/users/${USER_ID}" \
  -d '{"role":"Viewer"}' \
  >/dev/null

echo "Waiting for clicker dashboard to be provisioned..."
dashboard_ready=0
for _ in $(seq 1 60); do
  if curl -fsS -u "${ADMIN_USER}:${ADMIN_PASSWORD}" "${GRAFANA_URL}/api/search?query=clicker-dashboard" | grep -q '"uid":"clicker-dashboard"'; then
    dashboard_ready=1
    break
  fi
  sleep 1
done

if [ "${dashboard_ready}" -ne 1 ]; then
  echo "ERROR: clicker dashboard did not appear in time" >&2
  exit 1
fi

# Make the clicker dashboard the landing page so the viewer sees it immediately.
echo "Setting home dashboard to clicker..."
curl -fsS -u "${ADMIN_USER}:${ADMIN_PASSWORD}" \
  -X PUT \
  -H "Content-Type: application/json" \
  "${GRAFANA_URL}/api/org/preferences" \
  -d '{"homeDashboardUID":"clicker-dashboard"}' \
  >/dev/null

# Update password
echo "Updating user password..."
curl -fsS -u "${ADMIN_USER}:${ADMIN_PASSWORD}" \
  -X PUT \
  -H "Content-Type: application/json" \
  "${GRAFANA_URL}/api/admin/users/${USER_ID}/password" \
  -d "{\"password\":\"${VIEWER_PASSWORD}\"}" \
  >/dev/null

# Verify login works
echo "Verifying login with ${VIEWER_USER}..."
sleep 1
if curl -fsS -u "${VIEWER_USER}:${VIEWER_PASSWORD}" "${GRAFANA_URL}/api/user" >/dev/null 2>&1; then
  echo "SUCCESS: Viewer account created and verified"
else
  echo "ERROR: Could not verify viewer login"
  exit 1
fi
