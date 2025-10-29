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
# last_selected = 0 # i'm not a cs student i just want this to work

for (i, p) in enumerate(pins):
    GPIO.setup(p, GPIO.OUT)
    pwms.append(GPIO.PWM(p, 1000))
    pwms[i].start(0)
    leds_brightness.append(0)

# Generate HTML for the web page:
def web_page():
    # taken & modified from ChatGPT
    html = f""" 
        <html>
        <head>
            <meta charset="UTF-8">
            <title>LED Control</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .led-control {{ margin-bottom: 20px; }}
                label {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>LED Brightness Control</h1>

            <div class="led-control">
                <label for="led0">LED 1:</label>
                <input type="range" id="led0" min="0" max="100" value="0">
                <span id="val0">0</span>%
            </div>

            <div class="led-control">
                <label for="led1">LED 2:</label>
                <input type="range" id="led1" min="0" max="100" value="0">
                <span id="val1">0</span>%
            </div>

            <div class="led-control">
                <label for="led2">LED 3:</label>
                <input type="range" id="led2" min="0" max="100" value="0">
                <span id="val2">0</span>%
            </div>

            <script>
                // Function to send a POST request with LED and brightness
                function updateLED(led, brightness) {{
                    fetch("/", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/x-www-form-urlencoded" }},
                        body: `selected_led=${{led}}&brightness=${{brightness}}`
                    }})
                    .then(response => response.text())
                    .then(data => {{
                        console.log(`LED ${{led}} set to ${{brightness}}`);
                    }})
                    .catch(error => console.error("Error:", error));
                }}

                // Attach input event listeners to all sliders
                for (let i = 0; i < 3; i++) {{
                    const slider = document.getElementById(`led${{i}}`);
                    const valueSpan = document.getElementById(`val${{i}}`);

                    slider.addEventListener("input", function() {{
                        const brightness = slider.value;
                        valueSpan.textContent = brightness; // Update displayed value
                        updateLED(i, brightness);           // Send POST request
                    }});
                }}
            </script>
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
                # global last_selected
                # last_selected = brightness # janky
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
    GPIO.cleanup() 
    print('Joining webpageThread')
    webpageThread.join()