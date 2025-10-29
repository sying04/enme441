# used webserver_threaded.py and web_gpio_POST.py as templates to start from
# website made with assistance from chatGPT

import socket
import RPi.GPIO as GPIO
import threading
from time import sleep

GPIO.setmode(GPIO.BCM)

pins = [16, 20, 21]
pwms = []
leds_brightness = []
for p in pins:
    GPIO.setup(p, GPIO.OUT)
    pwms.append(GPIO.PWM(p, 2000))
    leds_brightness.append(0)

# Generate HTML for the web page:
def web_page():
    html = """
        <!DOCTYPE html>
        <html>
        <body>

        <form action="/" method="POST">
              <label for="brightness">Brightness level: </label><br>
              <input type="range" id="brightness" name="brightness" min="0" max="100" value="50">

              <p>Select LED: </p>
              <p><input type="radio" id="1" name="selected_led" value="LED 1">
              <label for="1">LED 1 (""" + leds_brightness[0] + """)</label><br>
              <input type="radio" id="2" name="selected_led" value="LED 2">
              <label for="2">LED 2 """ + leds_brightness[1] + """</label><br>
              <input type="radio" id="3" name="selected_led" value="LED 3">
              <label for="3">LED 3 """ + leds_brightness[2] + """</label>
              <p><button type="submit" class="button" name="submit" value="">Change Brightness</button></p>
        </form>

        </body>
        </html>
        """

    return (bytes(html,'utf-8'))   # convert html string to UTF-8 bytes object

# Helper function to extract key,value pairs of POST data
def parsePOSTdata(data):
    data_dict = {}
    idx = data.find('\r\n\r\n')+4
    data = data[idx:]
    data_pairs = data.split('&')
    for pair in data_pairs:
        key_val = pair.split('=')
        if len(key_val) == 2:
            data_dict[key_val[0]] = key_val[1]
    return data_dict

# Serve the web page to a client on connection:
def serve_web_page():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP-IP socket
    s.bind(('', 8080))
    s.listen(3)  # up to 3 queued connections

    try:
        while True:
            print('Waiting for connection...')
            conn, (client_ip, client_port) = s.accept()     # blocking call
            request = conn.recv(1024)               # read request (required even if none)

            # post request stuff
            print(f'Connection from {client_ip}')
            client_message = conn.recv(2048).decode('utf-8')
            print(f'Message from client:\n{client_message}')
            data_dict = parsePOSTdata(client_message)
            if 'selected_led' in data_dict.keys():   # make sure data was posted
                selected_led = data_dict["selected_led"] # which LED to change
            elif 'brightness' in data_dict.keys():
                brightness = data_dict["brightness"] # value of from slider
            else:   # web page loading for 1st time so start with 0 for the LED byte
                selected_led = '0'
                brightness = '0'

            conn.send(b'HTTP/1.1 200 OK\n')         # status line
            conn.send(b'Content-type: text/html\n') # header (content type)
            conn.send(b'Connection: close\r\n\r\n') # header (tell client to close at end)
            # send body in try block in case connection is interrupted:
            try:
                conn.sendall(web_page())                  # body
            finally:
                conn.close()

            pwms[selected_led - 1].ChangeDutyCycle(brightness)
            leds_brightness[selected_led - 1] = brightness
    except:
        print('Closing socket')
        s.close()

webpageThread = threading.Thread(target=serve_web_page)
webpageThread.daemon = True
webpageThread.start()


# Do whatever we want while the web server runs in
# a separate thread:
while True:
    sleep(1)
    print('.')
    pwms[0].ChangeDutyCycle(20)
