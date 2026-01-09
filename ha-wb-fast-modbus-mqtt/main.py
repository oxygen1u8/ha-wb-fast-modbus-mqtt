from fastmodbus import FastModbusSerialClient
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description='Fast Modbus')
    parser.add_argument('--options', type=str, help='Путь до options.json')

    args = parser.parse_args()
    path_to_options = args.options

    with open(path_to_options, "r", encoding="utf-8") as f:
        data = json.load(f)

    ports = []
    for port in data["Serial port config"]:
        port_path = port["Port"]
        baudrate = int(port["Baudrate"])
        stop_bit_count = int(port["Stop bit count"])
        parity = port["Parity"]
        ports.append(
            FastModbusSerialClient(
                port=port_path,
                baudrate=baudrate,
                stopbits=stop_bit_count,
                parity=parity
            )
        )

    for port in ports:
        port.connect()
        port.scan()
        print(port.slave_map)

    for port in ports:
        port.close()

if __name__ == "__main__":
    main()
