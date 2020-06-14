from RPi import GPIO
import time

class Stepper:
    full_steps = [
        [1,0,1,0],
        [1,0,0,1],
        [0,1,0,1],
        [0,1,1,0]
    ]

    full_steps_bak = [
        [1,0,0,0],
        [0,0,1,0],
        [0,1,0,0],
        [0,0,0,1]
    ]
    GPIO.setmode(GPIO.BCM)
    def __init__(self, stepsPerRev=200, in1=23, in2=6, in3=13, in4=19):
        self._in1 = in1
        self._in2 = in2
        self._in3 = in3
        self._in4 = in4

        self._stepsPerRev = stepsPerRev

        self._pins = [in1, in2, in3, in4]
        self._currentStep = 0

        self._setup()

    def _setup(self):
        for pin in self._pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

    def _set_step(self, pins):
        GPIO.output(self._pins[0], pins[0])
        GPIO.output(self._pins[1], pins[1])
        GPIO.output(self._pins[2], pins[2])
        GPIO.output(self._pins[3], pins[3])

    def turn_steps(self, steps, delay=0.006, dir=1):
        if dir == 1:
            for i in range(0, steps):
                for i in range(len(Stepper.full_steps)):
                    self._set_step(Stepper.full_steps[i])
                    time.sleep(delay)
        elif dir == 0:
            for i in range(0, steps):
                for i in range(len(Stepper.full_steps)):
                    self._set_step(Stepper.full_steps[len(Stepper.full_steps) - 1 - i])
                    time.sleep(delay)

        GPIO.output(self._pins[0], 0)
        GPIO.output(self._pins[1], 0)
        GPIO.output(self._pins[2], 0)
        GPIO.output(self._pins[3], 0)


    

    

    