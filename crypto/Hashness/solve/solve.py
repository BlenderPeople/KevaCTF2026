import argparse
import itertools
import json
import string
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen


# Набор символов намеренно достаточно разнообразный, но остаётся нормальным
# для передачи в JSON и командную строку.
ALPHABET = string.ascii_letters + string.digits + "_-{}"


def request_hash(endpoint: str, value: str, timeout: float) -> dict:
    """Отправляет одну строку сервису и возвращает разобранный JSON."""
    body = json.dumps({"value": value}, ensure_ascii=False).encode("utf-8")
    request = Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def candidates(max_length: int):
    """Перебирает строки возрастающей длины без исходного слова flag."""
    for length in range(1, max_length + 1):
        for parts in itertools.product(ALPHABET, repeat=length):
            value = "".join(parts)
            if value != "flag":
                yield value


def main() -> None:
    parser = argparse.ArgumentParser(description="Поиск коллизии weak-hash без исходников")
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:16767/api/hash",
        help="URL API хэширования",
    )
    parser.add_argument("--workers", type=int, default=16, help="Число параллельных запросов")
    parser.add_argument("--batch-size", type=int, default=256, help="Размер пачки запросов")
    parser.add_argument("--max-length", type=int, default=5, help="Максимальная длина строки")
    parser.add_argument("--timeout", type=float, default=5.0, help="Таймаут одного запроса")
    args = parser.parse_args()

    if args.workers < 1 or args.batch_size < 1 or args.max_length < 1:
        parser.error("workers, batch-size и max-length должны быть положительными")

    try:
        target = request_hash(args.url, "flag", args.timeout)
    except Exception as error:
        raise SystemExit(f"Не удалось обратиться к сервису: {error}") from error

    target_hash = str(target.get("hash", "")).lower()
    if not target_hash:
        raise SystemExit(f"Сервис вернул неожиданный ответ: {target!r}")

    print(f"Целевой хэш flag: {target_hash}")
    started = time.monotonic()
    checked = 0
    iterator = candidates(args.max_length)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        while True:
            batch = list(itertools.islice(iterator, args.batch_size))
            if not batch:
                break

            jobs = [pool.submit(request_hash, args.url, value, args.timeout) for value in batch]
            for value, job in zip(batch, jobs):
                checked += 1
                try:
                    result = job.result()
                except Exception:
                    continue

                if str(result.get("hash", "")).lower() == target_hash:
                    print(f"Коллизия найдена: {value!r}")
                    if result.get("flag"):
                        print(f"Флаг: {result['flag']}")
                    print(f"Проверено строк: {checked}; время: {time.monotonic() - started:.1f} с")
                    return

            if checked % 4096 < args.batch_size:
                print(f"Проверено строк: {checked}")

    raise SystemExit(
        "Коллизия не найдена. Увеличьте --max-length или расширьте ALPHABET в скрипте."
    )

if __name__ == "__main__":
    main()
