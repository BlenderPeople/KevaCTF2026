# Password in glasses wallpaper download | Easy | forensic

## Информация

> В сеть утекла картинка `password.png`. Нам нужен только этот файл и флаг внутри него.

## Деплой

`Не требуются`

## Выдать участникам

[`traffic_dump.zip`](public/traffic_dump.zip) из директории [public/](public/)

## Описание

В дампе есть HTTP-запрос на скачивание `password.png`.

## Решение

1. Открыть `traffic_dump.pcap` в Wireshark.
2. В `File -> Export Objects -> HTTP` сохранить `password.png`.
3. Достать флаг из файла.

[Эксплойт](solve/exploit.py)

## Флаг

`kevactf{http_objects_are_easy}`

## no-docker
