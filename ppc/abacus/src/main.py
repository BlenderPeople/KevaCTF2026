import asyncio
import logging
import random

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HOST = "0.0.0.0"
PORT = 62222
MAX_CONNECTIONS = 200
MAX_ANSWER_DIGITS = 32

flag = r"kevactf{Y0u_AR3_G00d_A7_cAlCuLA71nG!}"
connection_semaphore = asyncio.Semaphore(MAX_CONNECTIONS)

operations = {"SUM": "+", "DIV": "//", "DIFF": "-", "POW": "**", "MUL": "*"}

def generate_operation() -> tuple[int, int, str, int]:
    rand_operation = random.choice(list(operations))
    symbol_operation = operations[rand_operation]

    if rand_operation == "POW":
        op1 = random.randint(2, 20)
        op2 = random.randint(2, 4)
    else:
        op1 = random.randint(1, 200)
        op2 = random.randint(1, 200)

    if rand_operation == "SUM":
        ans = op1 + op2
    elif rand_operation == "DIV":
        ans = op1 // op2
    elif rand_operation == "DIFF":
        ans = op1 - op2
    elif rand_operation == "POW":
        ans = op1 ** op2
    elif rand_operation == "MUL":
        ans = op1 * op2
        
    return op1, op2, symbol_operation, ans


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
            res = 0
            data = ""
            count_cycles = random.randint(30, 100)

            for _ in range(count_cycles):
                op1, op2, symbol_operation, ans = generate_operation()
                data += f"{op1} {symbol_operation} {op2}\n"
                res += ans

            if not await safe_write(writer, data.encode()):
                return

            if not await safe_write(writer, b"\n=== Stream ended ===\n"):
                return

            if not await safe_write(writer, b"Answer: "):
                return

            logger.info(f"Answer: {res}")

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

            cleaned = num.lstrip("+").lstrip("-").strip()
            if len(cleaned) > MAX_ANSWER_DIGITS or not cleaned.isdigit():
                await safe_write(writer, b"Invalid input. Send only a number.\n")
            else:
                try:
                    is_correct = int(num) == res
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