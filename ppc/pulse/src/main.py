import asyncio
import logging
import random

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HOST = "0.0.0.0"
PORT = 55555
TOTAL_SYMBOLS = 100_000
MAX_CONNECTIONS = 200
MAX_ANSWER_DIGITS = 32

flag = r"kevactf{tth3_kK3Y_t00_Y00uR_$uCce$$_1$_H33r3}"
connection_semaphore = asyncio.Semaphore(MAX_CONNECTIONS)


def generate_cycle() -> str:
    part1 = '1' * random.randint(3, 5)
    num_zeros = random.randint(4, 10)
    part2 = '1' + '0' * num_zeros + '1'
    part3 = '0' * random.randint(3, 12)
    return part1 + part2 + part3


def generate_noise():
    if random.random() < 0.5:
        return '1' * random.randint(6, 25)
    else:
        return '0' * random.randint(1, 2) + '1' * random.randint(6, 15)


async def safe_write(writer: asyncio.StreamWriter, data: bytes) -> bool:
    try:
        if writer.is_closing():
            return False
        writer.write(data)
        await writer.drain()
        return True
    except (ConnectionResetError, BrokenPipeError, OSError):
        logger.debug("Connection lost during write")
        return False


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    async with connection_semaphore:
        try:
            count_symbols = 0
            max_length = 0
            data = ""

            while count_symbols <= TOTAL_SYMBOLS:
                rand = random.random()
                if rand <= 0.10:
                    count_cycles = random.randint(2, 50)
                elif rand <= 0.20:
                    count_cycles = random.randint(51, 100)
                elif rand <= 0.30:
                    count_cycles = random.randint(101, 150)
                elif rand <= 0.40:
                    count_cycles = random.randint(151, 200)
                elif rand <= 0.50:
                    count_cycles = random.randint(201, 250)
                elif rand <= 0.60:
                    count_cycles = random.randint(251, 300)
                elif rand <= 0.70:
                    count_cycles = random.randint(301, 350)
                elif rand <= 0.80:
                    count_cycles = random.randint(351, 400)
                elif rand <= 0.90:
                    count_cycles = random.randint(401, 450)
                else:
                    count_cycles = random.randint(451, 500)

                for _ in range(count_cycles):
                    cycle = generate_cycle()
                    data += cycle
                    count_symbols += len(cycle)

                max_length = max(max_length, count_cycles)

                noise = generate_noise()
                data += noise
                count_symbols += len(noise)

            if not await safe_write(writer, data.encode()):
                return

            if not await safe_write(writer, b"\n=== Stream ended ===\n"):
                return

            if not await safe_write(writer, "Max length: ".encode()):
                return

            logger.info(f"Answer: {max_length}")

            try:
                raw = await asyncio.wait_for(reader.readline(), timeout=6)
                num = raw.decode().strip()
            except TimeoutError:
                logger.warning("Client timed out while sending answer")
                return
            except (ConnectionResetError, BrokenPipeError):
                logger.debug("Client disconnected before sending answer")
                return
            except (ValueError, asyncio.LimitOverrunError):
                logger.info("Client sent an oversized line without a newline")
                await safe_write(writer, b"Invalid input. Send only a number.\n")
                return

            if len(num) > MAX_ANSWER_DIGITS or not num.isdigit():
                await safe_write(writer, b"Invalid input. Send only a number.\n")
            else:
                try:
                    is_correct = int(num) == max_length
                except ValueError:
                    is_correct = False

                if is_correct:
                    await safe_write(writer, f"\nCorrect!\n{flag}\n".encode())
                else:
                    await safe_write(writer, b"Wrong answer.\n")

        except asyncio.CancelledError:
            logger.debug("Task cancelled")
        except Exception:
            logger.error("Error in handle_client", exc_info=True)
        finally:
            try:
                if not writer.is_closing():
                    writer.close()
                    await writer.wait_closed()
            except Exception:
                pass


async def main() -> None:
    try:
        server = await asyncio.start_server(
            handle_client, 
            HOST, 
            PORT,
            limit=2**20
        )
        addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
        logger.info("Server started on %s", addrs)

        async with server:
            await server.serve_forever()
    except Exception:
        logger.error("Critical server error.", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())