import usocket as socket
import network
import onewire, ds18x20, time
from machine import Pin
import urequests
import secrets
import json

boot_led = Pin(16, Pin.OUT)
boot_led.value(0)
boot_led.value(1)

connect_led = Pin(15, Pin.OUT)
connect_led.value(0)

freezer_pin = Pin(26, Pin.IN)
freezer_sensor = ds18x20.DS18X20(onewire.OneWire(freezer_pin))

fridge_pin = Pin(27, Pin.IN)
fridge_sensor = ds18x20.DS18X20(onewire.OneWire(fridge_pin))

ap = network.WLAN(network.STA_IF)
ap.active(False)
ap.active(True)
ap.connect(secrets.wifi_name, secrets.wifi_pw)
time.sleep(1)
while not ap.isconnected():
    pass
connect_led.value(1)


def api():
    freezer_roms = freezer_sensor.scan()
    freezer_sensor.convert_temp()
    fridge_roms = fridge_sensor.scan()
    fridge_sensor.convert_temp()  
    time.sleep(1)  # docs say you have to wait 750ms before calling read_temp()
    freezer_temp = freezer_sensor.read_temp(freezer_roms[0])
    fridge_temp = fridge_sensor.read_temp(fridge_roms[0])
    return json.dumps({'fridge_temp': fridge_temp, 'freezer_temp': freezer_temp})
    

# set up a web server to listen for requests and return an html chunk
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creating socket object
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(5)
while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    response = api()
    conn.send('HTTP/1.0 200 OK\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n' + response + '\r\n')
    conn.close()

