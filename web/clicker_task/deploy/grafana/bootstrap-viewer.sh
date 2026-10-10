#!/bin/sh
set -eu

GRAFANA_URL="${GRAFANA_URL:-http://127.0.0.1:3000}"
# Use GF_SECURITY_* variables (Grafana standard naming)
PRIMARY_ADMIN_USER="${GF_SECURITY_ADMIN_USER:-${GRAFANA_ADMIN_USER:-admin}}"
PRIMARY_ADMIN_PASSWORD="${GF_SECURITY_ADMIN_PASSWORD:-${GRAFANA_ADMIN_PASSWORD:-admin}}"
PRIMARY_ADMIN_AUTH="${PRIMARY_ADMIN_USER}:${PRIMARY_ADMIN_PASSWORD}"
LEGACY_ADMIN_AUTH=""
ACTIVE_ADMIN_AUTH=""
VIEWER_USER="${GRAFANA_VIEWER_USER:?}"
VIEWER_PASSWORD="${GRAFANA_VIEWER_PASSWORD:?}"

if [ -n "${GRAFANA_LEGACY_ADMIN_USER:-}" ] && [ -n "${GRAFANA_LEGACY_ADMIN_PASSWORD:-}" ]; then
  LEGACY_ADMIN_AUTH="${GRAFANA_LEGACY_ADMIN_USER}:${GRAFANA_LEGACY_ADMIN_PASSWORD}"
fi

wait_for_grafana() {
  attempts=0
  until curl -fsS "${GRAFANA_URL}/api/health" >/dev/null 2>&1; do
    attempts=$((attempts + 1))
    if [ "$attempts" -ge 90 ]; then
      echo "grafana did not become ready in time" >&2
      exit 1
    fi
    sleep 2
  done
}

reset_admin_password() {
  if command -v grafana-cli >/dev/null 2>&1; then
    echo "attempting grafana-cli admin password reset"
    if grafana-cli admin reset-admin-password "${PRIMARY_ADMIN_PASSWORD}" >/dev/null 2>&1; then
      echo "admin password reset to desired value"
      return 0
    fi
  fi
  return 1
}

select_admin_auth() {
  for candidate in "${PRIMARY_ADMIN_AUTH}" "${LEGACY_ADMIN_AUTH}"; do
    if [ -n "${candidate}" ] && curl -fsS -u "${candidate}" "${GRAFANA_URL}/api/admin/settings" >/dev/null 2>&1; then
      ACTIVE_ADMIN_AUTH="${candidate}"
      return 0
    fi
  done

  echo "admin auth failed, trying password reset" >&2
  if reset_admin_password; then
    for candidate in "${PRIMARY_ADMIN_AUTH}" "${LEGACY_ADMIN_AUTH}"; do
      if [ -n "${candidate}" ] && curl -fsS -u "${candidate}" "${GRAFANA_URL}/api/admin/settings" >/dev/null 2>&1; then
        ACTIVE_ADMIN_AUTH="${candidate}"
        return 0
      fi
    done
  fi

  echo "failed to authenticate to grafana admin api" >&2
  return 1
}

lookup_user_id() {
  curl -fsS -u "${ACTIVE_ADMIN_AUTH}" "${GRAFANA_URL}/api/users/lookup?loginOrEmail=${VIEWER_USER}" \
    | sed -n 's/.*"id":[[:space:]]*\([0-9][0-9]*\).*/\1/p'
}

create_or_update_viewer() {
  create_payload=$(printf '{"name":"Clicker Log Viewer","email":"%s@ctf.local","login":"%s","password":"%s"}' "${VIEWER_USER}" "${VIEWER_USER}" "${VIEWER_PASSWORD}")
  curl -fsS -u "${ACTIVE_ADMIN_AUTH}" \
    -H "Content-Type: application/json" \
    -X POST \
    "${GRAFANA_URL}/api/admin/users" \
    -d "${create_payload}" >/dev/null 2>&1 || true

  user_id="$(lookup_user_id)"
  if [ -z "${user_id}" ]; then
    echo "failed to resolve viewer user id" >&2
    exit 1
  fi

  role_payload='{"role":"Viewer"}'
  curl -fsS -u "${ACTIVE_ADMIN_AUTH}" \
    -H "Content-Type: application/json" \
    -X PATCH \
    "${GRAFANA_URL}/api/orgs/1/users/${user_id}" \
    -d "${role_payload}" >/dev/null 2>&1 || true

  echo "waiting for clicker dashboard provisioning"
  dashboard_ready=0
  for _ in $(seq 1 60); do
    if curl -fsS -u "${ACTIVE_ADMIN_AUTH}" "${GRAFANA_URL}/api/search?query=clicker-dashboard" | grep -q '"uid":"clicker-dashboard"'; then
      dashboard_ready=1
      break
    fi
    sleep 1
  done

  if [ "${dashboard_ready}" -ne 1 ]; then
    echo "failed to detect clicker dashboard" >&2
    exit 1
  fi

  home_payload='{"homeDashboardUID":"clicker-dashboard"}'
  curl -fsS -u "${ACTIVE_ADMIN_AUTH}" \
    -H "Content-Type: application/json" \
    -X PUT \
    "${GRAFANA_URL}/api/org/preferences" \
    -d "${home_payload}" >/dev/null 2>&1 || true

  password_payload=$(printf '{"password":"%s"}' "${VIEWER_PASSWORD}")
  curl -fsS -u "${ACTIVE_ADMIN_AUTH}" \
    -H "Content-Type: application/json" \
    -X PUT \
    "${GRAFANA_URL}/api/admin/users/${user_id}/password" \
    -d "${password_payload}" >/dev/null
}

wait_for_grafana
select_admin_auth
create_or_update_viewer
 echo "grafana viewer account is ready"
