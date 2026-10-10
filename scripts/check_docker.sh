#!/usr/bin/env bash
set -euo pipefail

root="${1:-.}"

python3 - "$root" <<'PY'
import re
import sys
from pathlib import Path
import yaml

root = Path(sys.argv[1]).resolve()
compose_files = sorted([*root.rglob('docker-compose.yml'), *root.rglob('docker-compose.yaml')])
errors = []
service_owner = {}
port_owner = {}

HEADING_RE = re.compile(r'^\s*#+\s*(.*?)\s*#*\s*$')

def find_task_readme(compose_path):
    current = compose_path.parent
    while True:
        for child in current.iterdir():
            if child.is_file() and child.name.lower() == 'readme.md':
                return child
        if current == root or current.parent == current:
            return None
        current = current.parent

def has_no_docker_marker(readme_path):
    try:
        text = readme_path.read_text(encoding='utf-8')
    except Exception:
        return False
    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if m and m.group(1).strip().lower() == 'no-docker':
            return True
    return False

def add_error(msg):
    errors.append(msg)

def normalize_published(value):
    if value is None:
        return []
    s = str(value).strip()
    if not s:
        return []
    m = re.fullmatch(r"(\d+)-(\d+)", s)
    if m:
        a = int(m.group(1))
        b = int(m.group(2))
        if a > b:
            a, b = b, a
        return [str(x) for x in range(a, b + 1)]
    if re.fullmatch(r"\d+", s):
        return [s]
    return []

def extract_ports(item):
    if isinstance(item, int):
        return []
    if isinstance(item, str):
        s = item.strip()
        if not s:
            return []
        s = s.split('/')[0]
        parts = s.split(':')
        if len(parts) < 2:
            return []
        host = parts[-2].strip()
        return normalize_published(host)
    if isinstance(item, dict):
        if 'published' in item:
            return normalize_published(item.get('published'))
    return []

def has_limits(service):
    if not isinstance(service, dict):
        return False
    if service.get('mem_limit') is not None:
        return True
    if service.get('cpus') is not None:
        return True
    deploy = service.get('deploy')
    if isinstance(deploy, dict):
        resources = deploy.get('resources')
        if isinstance(resources, dict):
            limits = resources.get('limits')
            if isinstance(limits, dict) and limits:
                return True
    return False

def resolve_dockerfile(compose_path, service):
    build = service.get('build')
    if build is None:
        return None
    if isinstance(build, str):
        context = build
        dockerfile = 'Dockerfile'
    elif isinstance(build, dict):
        context = build.get('context', '.')
        dockerfile = build.get('dockerfile', 'Dockerfile')
    else:
        return None
    base = compose_path.parent
    context_path = (base / context).resolve()
    dockerfile_path = (context_path / dockerfile).resolve()
    return dockerfile_path

if not compose_files:
    print('No docker-compose files found')
    sys.exit(0)

skipped = []
for compose_path in list(compose_files):
    readme_path = find_task_readme(compose_path)
    if readme_path is not None and has_no_docker_marker(readme_path):
        skipped.append((compose_path, readme_path))
        compose_files.remove(compose_path)

for compose_path, readme_path in skipped:
    print(f"Skipping {compose_path}: '# no-docker' heading found in {readme_path}")

for compose_path in compose_files:
    try:
        data = yaml.safe_load(compose_path.read_text(encoding='utf-8')) or {}
    except Exception as e:
        add_error(f"{compose_path}: yaml parse error: {e}")
        continue

    services = data.get('services')
    if not isinstance(services, dict) or not services:
        add_error(f"{compose_path}: services section missing or empty")
        continue

    for service_name, service in services.items():
        key = service_name.strip() if isinstance(service_name, str) else str(service_name)
        if key in service_owner:
            add_error(f"duplicate service name '{key}': {service_owner[key]} and {compose_path}")
        else:
            service_owner[key] = compose_path

        if not isinstance(service, dict):
            add_error(f"{compose_path}: service '{key}' must be mapping")
            continue

        dockerfile_path = resolve_dockerfile(compose_path, service)
        if dockerfile_path is not None and not dockerfile_path.is_file():
            add_error(f"{compose_path}: service '{key}' dockerfile not found: {dockerfile_path}")

        restart = service.get('restart')
        if restart is None or str(restart).strip() == '':
            add_error(f"{compose_path}: service '{key}' missing restart policy")

        if not has_limits(service):
            add_error(f"{compose_path}: service '{key}' missing limits")

        ports = service.get('ports', [])
        if ports is None:
            ports = []
        if not isinstance(ports, list):
            add_error(f"{compose_path}: service '{key}' ports must be list")
            ports = []

        for port_item in ports:
            for published in extract_ports(port_item):
                owner = f"{compose_path}:{key}"
                if published in port_owner:
                    add_error(f"duplicate published port '{published}': {port_owner[published]} and {owner}")
                else:
                    port_owner[published] = owner

if errors:
    print('Docker check failed:')
    for e in errors:
        print(f'- {e}')
    sys.exit(1)

print(f'Docker check passed ({len(compose_files)} compose files checked, {len(skipped)} skipped via no-docker)')
PY
