try:
    import usocket as socket
except:
    import socket
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
freezer_temp_limit = -10

fridge_pin = Pin(27, Pin.IN)
fridge_sensor = ds18x20.DS18X20(onewire.OneWire(fridge_pin))
fridge_temp_limit = 3

ap = network.WLAN(network.STA_IF)
ap.active(False)
ap.active(True)
ap.connect(secrets.wifi_name, secrets.wifi_pw)
time.sleep(1)
while not ap.isconnected():
    pass
connect_led.value(1)


def update_temp(sensor: ds18x20.DS18X20) -> float:
    roms = sensor.scan()  # should be a list of one sensor in this pin
    sensor.convert_temp()  # docs say you have to wait 750ms before calling read_temp()
    time.sleep(1)
    return sensor.read_temp(roms[0])


def send_alert(device_name: str, current_temp: float, temp_limit: float):
    print("sending to: " + f"https://maker.ifttt.com/trigger/{secrets.ifttt_event}/json/with/key/{secrets.ifttt_token}")
    print("message: " + json.dumps({'alert': f"{device_name} temp is too warm!  Current temp = {current_temp}; Limit = {temp_limit}"}))
    response = urequests.post(
        f"https://maker.ifttt.com/trigger/{secrets.ifttt_event}/json/with/key/{secrets.ifttt_token}",
        headers = {'content-type': 'application/json'},
        data = json.dumps({'alert': f"{device_name} temp is too warm!  Current temp = {current_temp}; Limit = {temp_limit}"})
    )


def web_page(freezer_temp: float, fridge_temp: float):
    html = """
<html>
 <head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">
 </head>
 <body>
  <div class="container">
   <div class="row">
    <h1>Welcome to microcontrollerslab!</h1>
   </div>
   <div class="row">
    <ul class="list-group">
     <li class="list-group-item">Freezer temp is: {} C</li>
     <li class="list-group-item">Fridge temp is: {} C</li>
    </ul>
   </div>
  </div> 
 </body>
</html>""".format(freezer_temp, fridge_temp)
    return html


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creating socket object
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(5)

response = urequests.post("http://jsonplaceholder.typicode.com/posts", data = "some dummy content")

while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    print('Content = %s' % str(request))
    freezer_temp = update_temp(freezer_sensor)
    if freezer_temp > freezer_temp_limit:
        send_alert("Freezer", freezer_temp, freezer_temp_limit)
    fridge_temp = update_temp(fridge_sensor)
    response = web_page(freezer_temp, fridge_temp)
    conn.send(response)
    conn.close()
