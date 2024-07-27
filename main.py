#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sensor import StepperMotor, DoorSensor

motor = StepperMotor(in1 = 12, in2 = 16, in3 = 20, in4 = 21)
door_sensor_close = DoorSensor(pin = 17)
time_limit = 10 

motor.move(gradi=360, rpm=18, direction=-1, time_limit=30, door_sensor=door_sensor_close)

motor.cleanup()
