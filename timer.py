import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import json
import psutil

for proc in psutil.process_iter():
    if proc.name() == "libgpiod_pulsein" :
        proc.kill()
#벨소리 설정
scale = [ 261, 294, 329, 349, 392, 440, 493, 523] #주파수
term = [ 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1, 0.5, 0.5, 0.5, 0.5, 1 ] #간격
com = [ 4, 4, 5, 5, 4, 4, 2, 4, 4, 2, 2, 1]

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

global a
global b
a=1
b=1
LED =23
BUTTON = 24
buzzer_pin = 12

GPIO.setup(BUTTON, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(buzzer_pin, GPIO.OUT)
p= GPIO.PWM(buzzer_pin,100)

MQTT_HOST = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60
MQTT_PUB_TOPIC = "mobile/Namgyu/timer"
MQTT_SUB_TOPIC = "mobile/Namgyu/timer"


def on_message(client,userdata, message) :
    input_time=int(message.payload.decode("utf-8"))
    print(f"received message = {message.payload.decode('utf-8')}")
    countdown(input_time)
        
        
def countdown(timer):
    while timer > 0:
        minutes, seconds = divmod(timer, 60)
        timer_format = '{:02d}:{:02d}'.format(minutes, seconds)
        print(timer_format, end='\r')  # 타이머를 덮어쓰기 위해 \r 사용
        time.sleep(1)  # 1초 대기
        timer -= 1
        if timer == 0 :
            print("시간이 다되었습니다.")
client =mqtt.Client()
client.on_message = on_message
client.connect(MQTT_HOST,MQTT_PORT,MQTT_KEEPALIVE_INTERVAL)
client.subscribe(MQTT_SUB_TOPIC)
client.loop_start()

def message_button(channel) :
        print("Stop using the timer.")
        p.stop()
GPIO.add_event_detect(BUTTON, GPIO.RISING, callback=message_button)
def blink() :
    GPIO.output(23,GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(23,GPIO.LOW)
    time.sleep(0.3)

try:
    print(b)
    while True :
        if b == 1 :
            p.start(100)
            p.ChangeDutyCycle(90)         
            for i in range(25):
                p.ChangeFrequency(scale[com[i]])
                time.sleep(term[i])
                while True:    # 무한 루프
                    try :
                        blink()
                        if b == 0 :
                            break;
                    except RuntimeError:
                        time.sleep(2)
                    continue
                    time.sleep(10)
except KeyboardInterrupt:
    print("사용자가 프로그램을 종료했습니다.")

finally:
    GPIO.output(23,GPIO.LOW)
    GPIO.cleanup()

