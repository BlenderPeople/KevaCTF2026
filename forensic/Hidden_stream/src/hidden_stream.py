#!/usr/bin/env python3
from scapy.all import *
import base64
import random
import argparse
import logging
import warnings

logging.getLogger("scapy").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")


def str_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)


def encode_symbol(char):
    binary = str_to_binary(char)
    return base64.b64encode(binary.encode()).decode()

def inject_flag_into_pcap(input_pcap, output_pcap, flag, target_ip, target_port):
    """
    Внедряет трафик с флагом в существующий pcap файл
    """
    print(f"[+] Загрузка pcap файла: {input_pcap}")

    # Загружаем исходный pcap
    original_packets = rdpcap(input_pcap)
    print(f"[+] Загружено пакетов: {len(original_packets)}")

    if len(original_packets) == 0:
        print("[-] Файл пуст")
        return

    # Создаем новые пакеты с флагом (с правильными Ethernet заголовками)
    flag_packets = []

    # Берем существующий Ethernet заголовок из первого пакета как образец
    if Ether in original_packets[0]:
        src_mac = original_packets[0][Ether].src
        dst_mac = original_packets[0][Ether].dst
    else:
        # Стандартные MAC адреса если нет Ethernet слоя
        src_mac = "00:11:22:33:44:55"
        dst_mac = "ff:ff:ff:ff:ff:ff"

    print(f"[+] Флаг: {flag}")
    print(f"[+] Длина: {len(flag)} символов")

    # Выбираем случайную позицию для внедрения
    min_index = int(len(original_packets) * 0.2)
    max_index = int(len(original_packets) * 0.8)
    insert_position = random.randint(min_index, max_index)

    print(f"[+] Внедрение после пакета {insert_position}")

    # Получаем время из соседних пакетов
    if insert_position > 0:
        prev_time = original_packets[insert_position - 1].time
    else:
        prev_time = original_packets[0].time - 1

    current_time = prev_time + 0.1

    # Создаем пакет начала
    ip_layer = IP(src="192.168.1.100", dst=target_ip)
    tcp_layer = TCP(sport=12345, dport=target_port)
    payload = Raw(load="flag start")
    pkt = Ether(src=src_mac, dst=dst_mac) / ip_layer / tcp_layer / payload
    pkt.time = current_time
    flag_packets.append(pkt)
    current_time += 0.01

    # Создаем пакеты с символами: каждый пакет хранит base64(binary(char))
    for char in flag:
        payload = encode_symbol(char)
        pkt = Ether(src=src_mac, dst=dst_mac) / IP(src="192.168.1.100", dst=target_ip) / TCP(sport=12345,
                                                                                              dport=target_port) / Raw(
            load=payload)

        pkt.time = current_time
        flag_packets.append(pkt)
        current_time += 0.01

    # Создаем пакет конца
    pkt = Ether(src=src_mac, dst=dst_mac) / IP(src="192.168.1.100", dst=target_ip) / TCP(sport=12345,
                                                                                         dport=target_port) / Raw(
        load="flag end")
    pkt.time = current_time
    flag_packets.append(pkt)

    print(f"[+] Создано пакетов с флагом: {len(flag_packets)}")

    # Внедряем в исходный список
    for i, pkt in enumerate(flag_packets):
        original_packets.insert(insert_position + 1 + i, pkt)

    # Сохраняем
    wrpcap(output_pcap, original_packets)
    print(f"[+] Сохранено в: {output_pcap}")
    print(f"[+] Итоговое количество пакетов: {len(original_packets)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="Входной pcap файл")
    parser.add_argument("-o", "--output", default="injected.pcap", help="Выходной pcap файл")
    parser.add_argument("-f", "--flag", default="kevactf{C4tch_me_1f_y0u_can}", help="Флаг для внедрения")
    parser.add_argument("-t", "--target", default="10.0.0.50", help="Целевой IP")
    parser.add_argument("-p", "--port", type=int, default=4444, help="Целевой порт")

    args = parser.parse_args()
    inject_flag_into_pcap(args.input, args.output, args.flag, args.target, args.port)


if __name__ == "__main__":
    main()
