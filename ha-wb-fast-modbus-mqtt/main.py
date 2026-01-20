from fastmodbus.manager import FastModbusManager
from pymodbus.pdu.decoders import *
import asyncio
import time
import json
import argparse


async def execute_scan(manager: FastModbusManager):
    t = time.time()
    slave_map = await manager.scan_bus()
    t = time.time() - t
    print(f"[{manager.port}]: scan took {t} s")
    if len(slave_map):
        for slave in slave_map:
            print(f"[{manager.port}]: {slave}")
    else:
        print(f"[{manager.port}]: no Fast Modbus device found")


async def main():
    parser = argparse.ArgumentParser(description="Fast Modbus")
    parser.add_argument("--options", type=str, help="Путь до options.json")

    args = parser.parse_args()
    path_to_options = args.options

    with open(path_to_options, "r", encoding="utf-8") as f:
        data = json.load(f)

    port_managers = [FastModbusManager(port["Port"]) for port in data["Serial port config"]]

    await asyncio.gather(
        *[asyncio.create_task(execute_scan(manager)) for manager in port_managers]
    )


if __name__ == "__main__":
    asyncio.run(main())
