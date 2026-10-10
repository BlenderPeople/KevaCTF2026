#!/usr/bin/env bash
set -euo pipefail

src=""
out="public.zip"
excludes=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --exclude)
      [[ $# -lt 2 ]] && { echo "--exclude requires value" >&2; exit 1; }
      excludes+=("$2")
      shift 2
      ;;
    --output)
      [[ $# -lt 2 ]] && { echo "--output requires value" >&2; exit 1; }
      out="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 <source_dir> [--exclude pattern]... [--output public.zip]"
      exit 0
      ;;
    *)
      if [[ -z "$src" ]]; then
        src="$1"
      else
        echo "Unknown argument: $1" >&2
        exit 1
      fi
      shift
      ;;
  esac
done

[[ -z "$src" ]] && { echo "source_dir is required" >&2; exit 1; }
[[ -d "$src" ]] || { echo "source_dir does not exist: $src" >&2; exit 1; }

out_dir="$(dirname "$out")"
out_name="$(basename "$out")"
mkdir -p "$out_dir"
out_abs="$(cd "$out_dir" && pwd)/$out_name"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

rsync_args=("-a")
for pattern in "${excludes[@]}"; do
  rsync_args+=("--exclude" "$pattern")
done
rsync "${rsync_args[@]}" "$src"/ "$tmp"/

while IFS= read -r -d '' file; do
  if grep -Iq . "$file"; then
    perl -i -pe 's/[A-Za-z][A-Za-z0-9_]{1,32}\{[^{}\r\n]{1,200}\}/flag{this_is_flag}/g' "$file"
  fi
done < <(find "$tmp" -type f -print0)

rm -f "$out_abs"
(
  cd "$tmp"
  zip -qr "$out_abs" .
)

echo "$out_abs"
