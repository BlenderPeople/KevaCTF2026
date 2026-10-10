import asyncio
import logging
import random

from tlv_func import StreamModes

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HOST = "0.0.0.0"
PORT = 64444
FLAG = r"kevactf{PaR$1nG_1s$_TH3_R3aL_D3aLl}"
ANSWER_TIMEOUT = 6
MAX_CONNECTIONS = 200

MODES = ["SUM", "MAX", "SEL"]
connection_semaphore = asyncio.Semaphore(MAX_CONNECTIONS)


def _encode_payload(payload: list[int]) -> tuple[bytes]:
    if not payload:
        return b""

    raw_bytes = bytes(payload)
    return tuple(raw_bytes)


def _build_tlv_stream(
    valid_types: list[int]
) -> tuple[bytes, list[tuple[int, list[int], bool]]]:
    packets_count = random.randint(6, 18)
    packets_meta: list[tuple[int, list[int]]] = []
    chunks = bytearray()

    for _ in range(packets_count):
        pkt_type = random.choice(valid_types)

        pkt_len = random.randint(1, 24)
        payload = list(random.randbytes(pkt_len))
        encoded_payload = _encode_payload(payload)
        encoded_len = len(encoded_payload)

        chunks.append(pkt_type)
        chunks.append(encoded_len)
        chunks.extend(encoded_payload)

        packets_meta.append((pkt_type, payload))

    return bytes(chunks), packets_meta


def _to_hex_line(data: bytes) -> str:
    return " ".join(f"{byte:02X}" for byte in data)


async def _safe_send(writer: asyncio.StreamWriter, data: bytes) -> bool:
    if writer.is_closing():
        return False
    try:
        writer.write(data)
        await writer.drain()
        return True
    except (ConnectionResetError, BrokenPipeError):
        return False


def get_tlv() -> tuple[str, list[int], int]:
    try:
        stream = StreamModes()
        selected_types = [random.randint(0, 255) for _ in range(random.randint(9, 20))]
        valid_types = [tp for tp in range(256)]
        ans_message = ""

        rounds_count = random.randint(14, 30)
        for _ in range(rounds_count):
            mode = random.choice(MODES)
            stream_bytes, packets_meta = _build_tlv_stream(valid_types)
            ans_message += f"{mode}\n{_to_hex_line(stream_bytes)}\n\n"

            for pkt_type, payload in packets_meta:
                data = {
                    "list_bytes": payload,
                    "elem_type": pkt_type,
                    "selected_types": selected_types,
                }
                getattr(stream, mode)(data)

        return ans_message, selected_types, stream.answer()
    except Exception:
        logger.error("Failed to generate task data.", exc_info=True)
        raise


async def handler_client(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    async with connection_semaphore:
        peer = writer.get_extra_info("peername")
        try:
            logger.info("Client connected: %s", peer)
            tlv_line, selected_types, answer = get_tlv()
            logger.info(f"Answer for peer {peer}: {answer}")
            selected_types_hex = " ".join(f"{byte:02X}" for byte in selected_types)

            output = (
                f"Селекторные байты (HEX):\n"
                f"{selected_types_hex}\n\n"
                f"Последовательность:\n"
                f"{tlv_line}\n"
                "Передай итоговый контрольный индекс одним целым числом:\n"
            )

            sent = await _safe_send(writer, output.encode())
            if not sent:
                logger.info("Client %s disconnected before receiving task.", peer)
                return

            raw = await asyncio.wait_for(reader.readline(), timeout=ANSWER_TIMEOUT)
            if not raw:
                logger.info("Client %s closed connection without answer.", peer)
                return
            user_answer = raw.decode(errors="ignore").splitlines()[0].strip()

            if user_answer == str(answer):
                await _safe_send(writer, f"Доступ подтверждён.\n{FLAG}\n".encode())
                logger.info("Client %s submitted a correct answer.", peer)
            else:
                await _safe_send(writer, "Неверный контрольный индекс.\n".encode())
                logger.info("Client %s submitted an incorrect answer: %s", peer, user_answer)
                return
        except asyncio.TimeoutError:
            logger.info("Client %s did not send an answer in time.", peer)
            await _safe_send(writer, "Время ожидания ответа истекло.\n".encode())
        except (ConnectionResetError, BrokenPipeError):
            logger.info("Client %s disconnected unexpectedly.", peer)
        except (ValueError, asyncio.LimitOverrunError):
            logger.info("Client %s sent an oversized line without a newline.", peer)
            await _safe_send(writer, "Неверный контрольный индекс.\n".encode())
        except Exception:
            logger.error("Error while handling client %s.", peer, exc_info=True)
            await _safe_send(writer, "Внутренняя ошибка сервера.\n".encode())
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except (ConnectionResetError, BrokenPipeError):
                pass
            logger.info("Connection closed: %s", peer)


async def main() -> None:
    try:
        server = await asyncio.start_server(handler_client, HOST, PORT)
        addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
        logger.info("Server started on %s", addrs)

        async with server:
            await server.serve_forever()
    except Exception:
        logger.error("Critical server error.", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
