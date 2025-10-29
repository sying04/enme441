# used webserver_threaded.py and web_gpio_POST.py as templates to start from
# website made with assistance from chatGPT

import socket
import RPi.GPIO as GPIO
import threading
from time import sleep

GPIO.setmode(GPIO.BCM)

pins = [23, 24, 25]
pwms = []

leds_brightness = [] # for the radio buttons
last_selected = 0 # i'm not a cs student i just want this to work

for (i, p) in enumerate(pins):
    GPIO.setup(p, GPIO.OUT)
    pwms.append(GPIO.PWM(p, 1000))
    pwms[i].start(0)
    leds_brightness.append(0)

# Generate HTML for the web page:
def web_page():
    html = """
        <!DOCTYPE html>
        <html>
        <body>

        <form action="/" method="POST">
              <label for="brightness">Brightness Level: </label><br>
              <input type="range" id="brightness" name="brightness" min="0" max="100" value="""" + str(last_selected) + """">

              <div>Select LED: </div>
              <p><input type="radio" id="led1" name="selected_led" value="0">
              <label for="1">LED 1 (""" + str(leds_brightness[0]) + """)</label><br>
              <input type="radio" id="led2" name="selected_led" value="1">
              <label for="2">LED 2 (""" + str(leds_brightness[1]) + """)</label><br>
              <input type="radio" id="led3" name="selected_led" value="2">
              <label for="3">LED 3 (""" + str(leds_brightness[2]) + """)</label>
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
    while True:
        print('Waiting for connection...')
        conn, (client_ip, client_port) = s.accept()     # blocking call

        # post request stuff
        print(f'Connection from {client_ip}')
        client_message = conn.recv(2048).decode('utf-8')
        print(f'Message from client:\n{client_message}')

        if client_message.startswith('POST'): # only post messages !!!
            data_dict = parsePOSTdata(client_message)
            try:
                selected_led = int(data_dict["selected_led"]) # which LED to change
                brightness = int(data_dict["brightness"]) # value from slider

                pwms[selected_led].ChangeDutyCycle(brightness)
                leds_brightness[selected_led] = brightness
                global last_selected
                last_selected = brightness # janky
            except Exception as e:  
                print("parsing error:", e)

        conn.send(b'HTTP/1.1 200 OK\n')         # status line
        conn.send(b'Content-type: text/html\r\n') # header (content type)
        conn.send(b'Connection: close\r\n\r\n') # header (tell client to close at end)
        # send body in try block in case connection is interrupted:
        try:
            conn.sendall(web_page())                  # body
        finally:
            conn.close()

# socket !!!
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # address reuse
s.bind(('', 8080))
s.listen(3)

webpageThread = threading.Thread(target=serve_web_page)
webpageThread.daemon = True
webpageThread.start()


# Do whatever we want while the web server runs in
# a separate thread:
try:
    while True:
        sleep(1)
        # print('.')

except KeyboardInterrupt:
    print('Closing socket')
    s.close()
    print('Joining webpageThread')
    webpageThread.join()
    GPIO.cleanup()
