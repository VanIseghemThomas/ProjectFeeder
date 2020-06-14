import time
import threading
from RPi import GPIO
from subprocess import check_output
from datetime import datetime
import os

#Backend
from repositories.DataRepository import DataRepository
from flask import Flask, jsonify, request, send_file
from flask_socketio import SocketIO
from flask_cors import CORS
#Livestream
import cv2
import base64
import numpy as np



#Socketio
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Hier mag je om het even wat schrijven, zolang het maar geheim blijft en een string is'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

endpoint = "/api/v1"

cap = cv2.VideoCapture(0)


#---------SENSORS/INTERFACING-------------
#Actuatoren en sensoren
from stepper import Stepper
from libs.VL53L0X_rasp_python.python import VL53L0X
from i2clcd import LCD

#Pin voor ir sensors
ir_sensor = 27

#TOF sensor
tof = VL53L0X.VL53L0X()

#Stepper
stepper = Stepper(200, 23, 6, 13, 19)

#LED's
led = 26


#Ongebrukte pinnen lcd aan de massa!
lcd = LCD()

#Global variable of connected IP
ip_address = ""

def setup():
    #Pins init
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ir_sensor, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(led, GPIO.OUT)

    #Devices init
    init_tof()

    GPIO.add_event_detect(ir_sensor, GPIO.FALLING, callback=ir_callback, bouncetime=1000)
    #Show ip's on screen
    get_ips()
    print("Programma gestart")

#INIT functions

def init_tof():
    tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)


def get_ips():
    
    lcd.write_string("   Connecting   ", 0)
    lcd.write_string("   To WiFi...   ", 1) 
    
    connection = False

    ip_wifi = ""
    ip_apipa = ""
    
    while connection == False:
        print("connecting to network...")
        ip_list = []
        
        #Ip adressen ophalen met linux command en omzetten naar string
        ips = str(check_output(['hostname', '--all-ip-addresses']))

        #Rommel in begin er uit halen
        ips = ips[2:len(ips)]
        #Omzetten naar list
        ip_list = ips.split()
        #Enkel IPV4 adressen behouden
        ip_list = [ip_list[0], ip_list[1]]
        print(ip_list)
        for ip in ip_list:
            if "192.168" in ip:
                connection = True
                ip_wifi = ip
                #Save WiFi IP as global variable to use in other parts of code
                ip_address = ip
            elif ip == "169.254.10.1":
                ip_apipa = ip

    time.sleep(1)

    if (ip_wifi != ""):
        lcd.write_string(ip_wifi, 0)

    if (ip_apipa != ""):
        lcd.write_string(ip_apipa, 1) 
    

#Callback
def ir_callback(channel):
    log_ir_detection(1)
    print('**IR DETECTION: ', 'Pet eating')

    state = 1
    while (state == 1):
        state = get_ir_status()
        time.sleep(1)

    log_ir_detection(0)
    socketio.emit('B2F_IR-detection')
    print('**IR DETECTION: ', 'Pet done')
    print('----------------------')
    time.sleep(0.2)


#---Measure functions---
def get_weight():   #HX711 MODULE KAPOT
    #Lezen werkt
    #Nog omzetten naar echte waarden
    val = hx.get_weight(5)[0]
    hx.power_down()
    hx.power_up()

    print("Scale: ", float(val))
    return float(val)

def get_distance():

    distance = tof.get_distance()
    
    print ("TOF: %d mm, %d cm" % (distance, (distance/10)))
    time.sleep(20000/1000000.00)
    return distance


def get_ir_status():
    status = not GPIO.input(ir_sensor)
    return status   


#---Logging functions---
def log_ir_detection(state):
    timestamp = datetime.now()
    value =  1
    unit = 'BIN'
    sensorid = 2
    res = DataRepository.add_measurement(timestamp, state, unit, sensorid)

def log_weight(value):
    timestamp = datetime.now()
    unit = 'g'
    sensorid = 1
    res = DataRepository.add_measurement(timestamp, value, unit, sensorid)

def log_container(value):
    timestamp = datetime.now()
    unit = 'mm'
    sensorid = 3
    print(value)
    res = DataRepository.add_measurement(timestamp, value, unit, sensorid)

def log_stepper(value):
    timestamp = datetime.now()
    unit = 'Steps'
    actuatorid = 1
    res = DataRepository.add_actuator_event(timestamp, value, unit, actuatorid)


#---Actuator functions---
def feed(amount, preset=None):
    #10 steps = 100/5g = 20g
    #+2 compartements = 40g = 20steps
    steps = int(amount/2) + 20

    if(preset):
        print('Feeding from preset: ', preset)
    else:
        print('Feeding...')

    GPIO.output(led, 1)
    #Turn stepper to dispence and log in db
    stepper.turn_steps(steps, 0.006, 0)
    log_stepper(steps)
    GPIO.output(led, 0)

    #Check container and log in db
    distance = get_distance()
    log_container(distance)

    socketio.emit('B2F_feeding')


#Setup call
setup()
 
def video_stream():  

    ret, frame = cap.read()
    string = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode()
    img = {
        'img': string
    }
    socketio.emit('B2F_video', img)

def main():
    
    try:  
        while True:
            t = threading.currentThread()

            while True:
                #Get current timestamp and day
                timestamp = datetime.now()
                timestamp_h = timestamp.hour
                timestamp_m = timestamp.minute
                timestamp_s = timestamp.second
                timestamp_dof = timestamp.strftime('%A')
                #print(timestamp_h, timestamp_m, timestamp_dof)
                
                presets = DataRepository.read_presets()

                for preset in presets:
                    if (preset['dayofweek'] == timestamp_dof and preset['hour'] == timestamp_h and preset['minute'] == timestamp_m and timestamp_s == 0):
                        feed(preset['amount'], preset['presetid'])
                time.sleep(1)

    except KeyboardInterrupt as e:
        print(e)
        #tof.stop_ranging()
        print("stop")
        GPIO.cleanup()

threading.Timer(0.5, main).start()

# API ENDPOINTS
@app.route(endpoint + '/events', methods=['GET'])
def get_events():
    if request.method == 'GET':
        data = DataRepository.read_logs()
        return jsonify(events=data), 200

@app.route(endpoint + '/events/measurements', methods=['GET'])
def get_measurements():
    if request.method == 'GET':
        data = DataRepository.read_measurements()
        return jsonify(measurements=data), 200

@app.route(endpoint + '/events/measurements/<id>', methods=['GET'])
def get_measurements_with_id(id):
    if request.method == 'GET':
        data = DataRepository.read_measurements_with_id(id)
        return jsonify(measurements=data), 200

@app.route(endpoint + '/event/measurement', methods=['POST'])
def add_measurement():
    if request.method == 'POST':
        params = DataRepository.json_or_formdata(request)
        data = DataRepository.add_measurement(params)
        return jsonify(measurement=data), 201

@app.route(endpoint + '/events/actuators', methods=['GET'])
def get_actuator_events():
    if request.method == 'GET':
        data = DataRepository.read_actuator_events()
        return jsonify(actions=data), 200

@app.route(endpoint + '/actuators', methods=['GET'])
def get_actuators():
    if request.method == 'GET':
        data = DataRepository.read_actuators()
        return jsonify(actuators=data), 200

@app.route(endpoint + '/event/actuator', methods=['POST'])
def add_actuator_event():
    if request.method == 'POST':
        params = DataRepository.json_or_formdata(request)
        data = DataRepository.add_actuator_event(params)
        return jsonify(measurement=data), 201

@app.route(endpoint + '/sensors', methods=['GET'])
def get_sensors():
    if request.method == 'GET':
        data = DataRepository.read_sensors()
        return jsonify(sensors=data), 200

@app.route(endpoint + '/presets', methods=['GET', 'POST'])
def get_settings():
    if request.method == 'GET':
        data = DataRepository.read_presets()
        return jsonify(presets=data), 200

    elif request.method == 'POST':
        jsonobject = DataRepository.json_or_formdata(request)
        nieuw_id = DataRepository.add_preset(jsonobject['dayofweek'], jsonobject['hour'], jsonobject['minute'], jsonobject['amount'])
        return jsonify(categorie_id=nieuw_id), 201


@app.route(endpoint + '/presets/<presetid>', methods=['DELETE'])
def get_setting(presetid):
    if request.method == 'DELETE':
        data = DataRepository.delete_preset(presetid)
        if data != 0:
            return jsonify(status="success", row_count=data), 201
        else:
            return jsonify(status="no update", row_count=data), 201

@app.route(endpoint + '/data/downloadcsv', methods=['GET'])
def get_csv():
    if request.method == 'GET':
        filePath = '/home/pi/project/download_cache/sample.csv'
        return send_file(filePath, as_attachment=True)


#This is for the Google Chrome extension
@app.route(endpoint + '/discover', methods=['GET'])
def get_discover():
    if request.method == 'GET':
        return jsonify(status="Feeder available!"), 200

# SOCKET IO
@socketio.on('connect')
def initial_connection():
    print('A new client connected')
    #Make a log for all sensors to update website's status
    #weight = get_weight()
    #status_ir = get_ir_status()
    status_container = get_distance()
    log_container(status_container)


    #log_weight(weight)
    #log_ir_detection(status_ir)
    #log_container(status_container)

    socketio.emit('B2F_status')

@socketio.on('F2B_status')
def get_status():
    status_container = get_distance()
    log_container = status_container

@socketio.on('F2B_feed')
def start_feed(jsonobject):
    amount = int(jsonobject['amount'])
    feed(amount)
    
@socketio.on('F2B_edit-preset')
def broadcast_edit_preset():
    print('preset edit')
    socketio.emit('B2F_edit-preset', broadcast=True)

@socketio.on('F2B_video')
def get_video():
    video_stream()

@socketio.on('F2B_create_csv')
def create_csv(data):
    filePath = '/home/pi/project/download_cache/sample.csv'
    csv_string = data['string']

    # As file at filePath is deleted now, so we should check if file exists or not not before deleting them
    if os.path.exists(filePath):
        os.remove(filePath)
        print("Old version deleted")
    else:
        print("No prior version")

    text_file = open(filePath, "wt")
    n = text_file.write(csv_string)
    text_file.close()
    socketio.emit('B2F_download_ready')
    print('download ready')



if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')

    