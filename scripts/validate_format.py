#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

CATEGORIES = ["web", "ppc", "crypto", "forensic", "misc", "pwn", "reverse", "stego", "osint", "admin"]
REQUIRED_SECTIONS = ["Информация", "Деплой", "Выдать участинкам", "Описание", "Решение", "Флаг"]
ALTERNATIVE_SECTION_NAMES = {"Выдать участинкам": ["Выдать участникам"]}
FLAG_RE = re.compile(r"`([^`]+)`")
HEADING_RE = re.compile(r"^\s*#+\s*(.*?)\s*#*\s*$")


def has_no_docker_marker(content: str) -> bool:
    for line in content.splitlines():
        m = HEADING_RE.match(line)
        if m and m.group(1).strip().lower() == "no-docker":
            return True
    return False


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def is_hidden(name: str) -> bool:
    return name.startswith(".")


def find_task_dirs(root: Path):
    tasks = []
    for category in CATEGORIES:
        category_path = root / category
        if not category_path.exists() or not category_path.is_dir():
            continue
        for item in sorted(category_path.iterdir()):
            if is_hidden(item.name) or not item.is_dir():
                continue
            tasks.append(item)
    return tasks


def parse_sections(content: str):
    sections = {}
    current = None
    for line in content.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            current = m.group(1)
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}


def has_section(sections, name: str) -> bool:
    if name in sections:
        return True
    for alt in ALTERNATIVE_SECTION_NAMES.get(name, []):
        if alt in sections:
            return True
    return False


def detect_section_name(sections, name: str) -> str:
    if name in sections:
        return name
    for alt in ALTERNATIVE_SECTION_NAMES.get(name, []):
        if alt in sections:
            return alt
    return ""


def validate_task(task_dir: Path, strict_deploy: bool):
    errors = []
    readme = task_dir / "README.md"
    if not readme.exists():
        errors.append(f"{task_dir}: отсутствует README.md")
        return errors

    content = read_text(readme)
    lines = content.splitlines()
    title_line = ""
    for line in lines:
        if line.strip():
            title_line = line.strip()
            break

    if not title_line.startswith("# "):
        errors.append(f"{readme}: первая непустая строка должна начинаться с '# '")
    else:
        title_value = title_line[2:].strip()
        parts = [p.strip() for p in title_value.split("|")]
        if len(parts) != 3 or not all(parts):
            errors.append(f"{readme}: заголовок должен быть формата '# Название | Уровень | Категория'")
        else:
            category_in_title = parts[2].lower()
            category_from_path = task_dir.parent.name.lower()
            if category_in_title != category_from_path:
                errors.append(
                    f"{readme}: категория в заголовке '{parts[2]}' не совпадает с директорией '{task_dir.parent.name}'"
                )

    sections = parse_sections(content)
    requires_public = "public/" in content
    no_docker = has_no_docker_marker(content)
    for section_name in REQUIRED_SECTIONS:
        if not has_section(sections, section_name):
            errors.append(f"{readme}: отсутствует раздел '## {section_name}'")

    deploy_dir = task_dir / "deploy"
    public_dir = task_dir / "public"
    solve_dir = task_dir / "solve"

    if not no_docker and strict_deploy and not deploy_dir.is_dir():
        errors.append(f"{task_dir}: отсутствует директория deploy")

    if requires_public and not public_dir.is_dir():
        errors.append(f"{task_dir}: отсутствует директория public")

    if not solve_dir.is_dir():
        errors.append(f"{task_dir}: отсутствует директория solve")

    if not no_docker and deploy_dir.is_dir():
        if not (deploy_dir / "Dockerfile").is_file():
            errors.append(f"{task_dir}: в deploy отсутствует Dockerfile")
        compose_ok = (deploy_dir / "docker-compose.yml").is_file() or (deploy_dir / "docker-compose.yaml").is_file()
        if not compose_ok:
            errors.append(f"{task_dir}: в deploy отсутствует docker-compose.yml|yaml")

    if requires_public and public_dir.is_dir():
        public_files = [p for p in public_dir.rglob("*") if p.is_file()]
        if not public_files:
            errors.append(f"{task_dir}: директория public пуста")

    if solve_dir.is_dir():
        solve_files = [p for p in solve_dir.rglob("*") if p.is_file()]
        if not solve_files:
            errors.append(f"{task_dir}: директория solve пуста")

    solve_section_name = detect_section_name(sections, "Решение")
    if solve_section_name:
        solve_text = sections[solve_section_name]
        if "solve/" not in solve_text:
            errors.append(f"{readme}: в разделе 'Решение' должна быть ссылка на файл из solve/")

    public_section_name = detect_section_name(sections, "Выдать участинкам")
    if requires_public and public_section_name:
        public_text = sections[public_section_name]
        if "public/" not in public_text:
            errors.append(f"{readme}: в разделе '{public_section_name}' должна быть ссылка на public/")

    flag_section_name = detect_section_name(sections, "Флаг")
    if flag_section_name:
        flag_text = sections[flag_section_name]
        m = FLAG_RE.search(flag_text)
        if not m:
            errors.append(f"{readme}: в разделе 'Флаг' значение должно быть в обратных кавычках")
        else:
            flag = m.group(1)
            if not flag:
                errors.append(f"{readme}: флаг не должен быть пустым")

    return errors


def validate_repo(root: Path, strict_deploy: bool):
    errors = []
    for category in CATEGORIES:
        category_path = root / category
        if not category_path.exists():
            errors.append(f"{category_path}: отсутствует категория")
            continue
        if not category_path.is_dir():
            errors.append(f"{category_path}: должна быть директорией")

    tasks = find_task_dirs(root)
    if not tasks:
        errors.append("Не найдено ни одной директории задания в формате category/task")
        return errors

    for task in tasks:
        errors.extend(validate_task(task, strict_deploy=strict_deploy))

    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--no-strict-deploy", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors = validate_repo(root, strict_deploy=not args.no_strict_deploy)

    if errors:
        print("Validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
