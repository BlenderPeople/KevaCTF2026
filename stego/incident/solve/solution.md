# Решение задачи Incident

## Общая информация

- **Уровень:** Medium
- **Категория:** stego
- **Техники:** PNG/ZIP-полиглот, метаданные PNG, LSB-стеганография

---

## Этап 1: Определяем природу файла

`file error.png` показывает обычные PNG image data. Пробуем поискать вложенные данные:

```sh
binwalk error.png
```

или сразу пробуем распаковать как архив:

```sh
unzip error.png
```

Это сработает, потому что ZIP-инструменты ищут структуру архива с конца файла — PNG-данные в начале им не мешают.

---

## Этап 2: Извлекаем архив

```sh
unzip error.png
```

Результат — файл `SYSTEM_BREACH_DETECTED.png`.

---

## Этап 3: Смотрим метаданные

```sh
strings SYSTEM_BREACH_DETECTED.png | grep -i comment -A1
```

или

```sh
exiftool SYSTEM_BREACH_DETECTED.png
```

Находим подсказку: `use zsteg`.

---

## Этап 4: Достаём флаг

```sh
zsteg SYSTEM_BREACH_DETECTED.png
```

Либо через референсный скрипт, который проходит всю цепочку сам (нужен `pillow`: `pip install pillow`):

```sh
python3 solve.py
```

Референсная реализация — в [solve.py](solve.py).

---

## Флаг

```
kevactf{N0_1nC1d3nt_C4n_H1d3_Fr0m_Y0u}
```
