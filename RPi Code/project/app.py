# pylint: skip-file
from repositories.DataRepository import DataRepository
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS

import time
import threading

# Code voor led
from helpers.klasseknop import Button
from RPi import GPIO

led1 = 26
knop1 = Button(20)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(led1, GPIO.OUT)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Hier mag je om het even wat schrijven, zolang het maar geheim blijft en een string is'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

endpoint = "/api/v1"

print("Running...")

# API ENDPOINTS
@app.route(endpoint + '/events', methods=['GET'])
def get_events():
    if request.method == 'GET':
        data = DataRepository.read_events()
        return jsonify(events=data), 200

@app.route(endpoint + '/actions/measurements', methods=['GET'])
def get_measurements():
    if request.method == 'GET':
        data = DataRepository.read_measurements()
        return jsonify(measurements=data), 200

@app.route(endpoint + '/actions/actuators', methods=['GET'])
def get_actuator_actions():
    if request.method == 'GET':
        data = DataRepository.read_actuator_actions()
        return jsonify(actions=data), 200

@app.route(endpoint + '/actuators', methods=['GET'])
def get_actuators():
    if request.method == 'GET':
        data = DataRepository.read_actuators()
        return jsonify(actuators=data), 200

@app.route(endpoint + '/sensors', methods=['GET'])
def get_sensors():
    if request.method == 'GET':
        data = DataRepository.read_sensors()
        return jsonify(sensors=data), 200

@app.route(endpoint + '/schemas', methods=['GET'])
def get_schemas():
    if request.method == 'GET':
        data = DataRepository.read_schemas()
        return jsonify(schemas=data), 200

@app.route(endpoint + '/settings', methods=['GET'])
def get_settings():
    if request.method == 'GET':
        data = DataRepository.read_settings()
        return jsonify(settings=data), 200


# SOCKET IO
@socketio.on('connect')
def initial_connection():
    print('A new client connect')
    # # Send to the client!
    # vraag de status op van de lampen uit de DB
    status = DataRepository.read_status_lampen()
    socketio.emit('B2F_status_lampen', {'lampen': status})


@socketio.on('F2B_switch_light')
def switch_light(data):
    print('licht gaat aan/uit')
    lamp_id = data['lamp_id']
    new_status = data['new_status']
    # spreek de hardware aan
    # stel de status in op de DB
    res = DataRepository.update_status_lamp(lamp_id, new_status)
    print(lamp_id)
    if lamp_id == "2":
        lees_knop(20)
    # vraag de (nieuwe) status op van de lamp
    data = DataRepository.read_status_lamp_by_id(lamp_id)
    socketio.emit('B2F_verandering_lamp', {'lamp': data})


def lees_knop(pin):
    print("button pressed")
    if GPIO.input(led1) == 1:
        GPIO.output(led1, GPIO.LOW)
        res = DataRepository.update_status_lamp("2", "0")
    else:
        GPIO.output(led1, GPIO.HIGH)
        res = DataRepository.update_status_lamp("2", "1")
    data = DataRepository.read_status_lamp_by_id("2")
    socketio.emit('B2F_verandering_lamp', {'lamp': data})


knop1.on_press(lees_knop)


if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
