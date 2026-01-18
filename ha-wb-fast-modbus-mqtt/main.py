from fastmodbus.asyncfastmodbus import AsyncFastModbusSerialClient
from pymodbus.pdu.decoders import *
import logging
import asyncio
import time
import json
import argparse


async def scan(serial_port: str):
    baudrates = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
    parity = ["O", "E", "N"]

    print("Start Fast Modbus scan...")
    slave_map = []
    t1 = time.time()
    for b in baudrates:
        for p in parity:
            client = AsyncFastModbusSerialClient(
                serial_port, baudrate=b, parity=p
            )
            await client.connect()
            print(f"[{serial_port}]: scan on {b} bps | parity: {p}")
            result = await client.scan()
            if len(result):
                slave_map += result
            client.close()
    t2 = time.time()

    print(f"[{serial_port}]: scan took {t2 - t1} s")
    for slave in slave_map:
        print(slave)

    return slave_map


async def main():
    parser = argparse.ArgumentParser(description="Fast Modbus")
    parser.add_argument("--options", type=str, help="Путь до options.json")

    args = parser.parse_args()
    path_to_options = args.options

    with open(path_to_options, "r", encoding="utf-8") as f:
        data = json.load(f)

    tasks = [asyncio.create_task(scan(port["Port"])) for port in data["Serial port config"]]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
