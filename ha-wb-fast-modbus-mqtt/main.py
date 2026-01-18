from fastmodbus.asyncfastmodbus import AsyncFastModbusSerialClient
from pymodbus.pdu.decoders import *
import logging
import asyncio
import time
import json
import argparse


async def scan(serial_port: str):
    baudrates = [9600, 115200]
    parity = ["O", "E", "N"]
    stop_bits = [1]

    print("Fast Modbus scan...")
    slave_map = []
    t1 = time.time()
    for b in baudrates:
        for p in parity:
            for s in stop_bits:
                client = AsyncFastModbusSerialClient(
                    serial_port, baudrate=b, parity=p, stopbits=s
                )
                await client.connect()
                # result = await client.read_holding_registers(0x6E, device_id=115)
                print(f"[{serial_port}]: scan on {b} bps | parity: {p}")
                result = await client.scan()
                if len(result):
                    slave_map += result
                client.close()
    t2 = time.time()

    print(f"[{serial_port}]: scan took {t2 - t1} s")
    for slave in slave_map:
        print(slave)

    slave_id = 37
    reg_addr = 0x6E
    print(f"Default Modbus scan device with {slave_id}...")
    client = AsyncFastModbusSerialClient(serial_port, baudrate=115200, parity="N", stopbits=2)
    await client.connect()
    result = await client.read_holding_registers(address=reg_addr, device_id=slave_id)
    print(f"From slave_id {hex(slave_id)} reg {hex(reg_addr)}: {result}")
    client.close()

    return slave_map


async def main():
    parser = argparse.ArgumentParser(description="Fast Modbus")
    parser.add_argument("--options", type=str, help="Путь до options.json")

    args = parser.parse_args()
    path_to_options = args.options

    with open(path_to_options, "r", encoding="utf-8") as f:
        data = json.load(f)

    # tasks = [asyncio.create_task(scan(port["Port"])) for port in data["Serial port config"]]
    # await asyncio.gather(*tasks)
    await scan("/dev/ttyACM1")


if __name__ == "__main__":
    asyncio.run(main())
