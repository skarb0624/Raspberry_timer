import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import json
import psutil

for proc in psutil.process_iter():
    if proc.name() == "libgpiod_pulsein" :
        proc.kill()

scale = [ 261, 294, 329, 349, 392, 440, 493, 523] #
term = [ 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1, 0.5, 0.5, 0.5, 0.5, 1 ] #
com = [ 4, 4, 5, 5, 4, 4, 2, 4, 4, 2, 2, 1]

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
global stop_message
global intimer
global push_button
global input_time

stop_message = 0
push_button = 1
intimer = 1
LED = 23
BUTTON = 24
buzzer_pin = 12
save_time =1
ledlight = True
GPIO.setup(BUTTON, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(buzzer_pin, GPIO.OUT)
p= GPIO.PWM(buzzer_pin,100)

MQTT_HOST = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60
MQTT_PUB_TOPIC = "mobile/Namgyu/timersetting"
MQTT_SUB_TOPIC = "mobile/Namgyu/timer"


def on_message(client,userdata, message) :
    global stop_message
    global count
    global input_time
    try:
        input_time = int(message.payload.decode("utf-8"))
        print(f"input times = {message.payload.decode('utf-8')}s")
        stop_message = 1
        countdown(input_time)
    except ValueError:
        print("Invalid input. Please provide a valid integer.")


def countdown(timer):
    while timer > 0:
        global intimer
        minutes, seconds = divmod(timer, 60)
        timer_format = '{:02d}:{:02d}'.format(minutes, seconds)
        print(timer_format, end='\r')
        time.sleep(1)   
        timer -= 1
        if timer == 0 :
            print("timeout.")
            intimer = 0

client =mqtt.Client()
client.on_message = on_message
client.connect(MQTT_HOST,MQTT_PORT,MQTT_KEEPALIVE_INTERVAL)
client.subscribe(MQTT_SUB_TOPIC)
client.loop_start()


def message_timer() :
    if stop_message == 0 :
        timermean = {
    "msg " : "Please enter the time of the timer , timer address: moilbe/Namgyu/timer",
        }
        value = json.dumps(timermean)
        client.publish(MQTT_PUB_TOPIC,value)
        print(value)
        time.sleep(5)



def message_button(channel) :
        global push_button
        global ledlight
        if intimer == 0 :
            push_button = 0
            print("Stop using the timer.")
            p.stop()
            ledlight = False
GPIO.add_event_detect(BUTTON, GPIO.RISING, callback=message_button)


def blink() :
    global ledlight
    while ledlight :
        GPIO.output(23,GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(23,GPIO.LOW)
        time.sleep(0.3)


try:
    while True :
        message_timer()
        if intimer == 0 :
            p.start(100)
            p.ChangeDutyCycle(90)
            blink()
            endmessage = {
                "msg" : "Timeout"
                }
            value2 = json.dumps(endmessage)
            client.publish(MQTT_PUB_TOPIC,value2)
            print(value2)
        if push_button == 0 :
            break
            for i in range(25):
                p.ChangeFrequency(scale[com[i]])
                time.sleep(term[i])
                print(push_button)    
except KeyboardInterrupt:
    print("User terminated the program.")
    GPIO.output(23,GPIO.LOW)
    GPIO.cleanup()
finally:
    GPIO.output(23,GPIO.LOW)
    GPIO.cleanup()