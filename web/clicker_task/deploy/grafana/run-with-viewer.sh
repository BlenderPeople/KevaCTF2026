#!/bin/sh
set -eu

/run.sh &
grafana_pid=$!

shutdown() {
  kill -TERM "${grafana_pid}" 2>/dev/null || true
  wait "${grafana_pid}" 2>/dev/null || true
}

trap shutdown INT TERM

/bin/sh /bootstrap-viewer.sh

wait "${grafana_pid}"
