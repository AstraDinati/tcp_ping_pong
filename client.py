import asyncio
import random
import datetime
import logging
from config import HOST, PORT, LOGGING_FORMAT, DATE_FORMAT, TIME_FORMAT


class Client:
    def __init__(self):
        self.host = HOST
        self.port = PORT
        self.request_count = 0

    async def connect_to_server(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        logging.info(f"Connected to server at {self.host}:{self.port}")

    async def send_ping(self):
        timestamp = datetime.datetime.now().strftime(LOGGING_FORMAT)
        message = f"[{self.request_count}] PING"
        self.writer.write(message.encode() + b"\n")
        await self.writer.drain()
        self.request_count += 1
        return timestamp, message

    async def receive_pong(self):
        response_time = datetime.datetime.now().strftime(TIME_FORMAT)
        response_date = datetime.datetime.now().strftime(DATE_FORMAT)
        data = await asyncio.wait_for(self.reader.readline())
        response = data.decode().strip()
        return response_date, response_time, response

    async def close_connection(self):
        self.writer.close()
        await self.writer.wait_closed()
        logging.info("Connection closed")


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(message)s",
        filename="client.log",
        filemode="a",
    )

    client = Client()
    await client.connect_to_server()

    try:
        while True:
            await asyncio.sleep(random.uniform(0.3, 3.0))
            timestamp, message = await client.send_ping()
            while True:
                try:
                    response_date, response_time, response = await asyncio.wait_for(
                        client.receive_pong(), timeout=1
                    )
                    if "keepalive" not in response:
                        break
                    else:
                        logging.info(
                            "%s; %s; %s", response_date, response_time, response
                        )
                except asyncio.TimeoutError:
                    response = "(таймаут)"
                    break
            if response == "(таймаут)":
                logging.info("%s; %s; %s", timestamp, message, response)
            else:
                logging.info(
                    "%s; %s; %s; %s",
                    timestamp,
                    message,
                    response_time,
                    response,
                )
    except KeyboardInterrupt:
        await client.close_connection()


asyncio.run(main())
