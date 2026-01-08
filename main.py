from fastmodbus import FastModbusSerialClient

client = FastModbusSerialClient("/dev/ttyACM0", baudrate=115200)
client.connect()
client.scan()
print(client.slave_map)
client.close()
