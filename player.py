#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
import os
import subprocess
import signal # to handle Ctrl+C
import sys

class Player():

    def __init__(self,
                vibration_callback=None,
                nfc_callback=None,
                ir_callback=None,
                magnetic_callback=None,
                pushtocross_callback=None,
                internal_callback=None,
                broadcast_callback=None,
                emergency_callback=None,
                pin_vibration=11,
                pin_nfc=None,
                pin_ir=8,
                pin_magnetic=None,
                pin_pushtocross=13,
                pin_internal=15,
                pin_broadcast=None,
                pin_emergency=None,
                pin_led_green=18,
                pin_led_red=16):
        """
        Sets the Player with default pinout if not provided
        """
        self.vibration_callback = vibration_callback
        self.nfc_callback = nfc_callback
        self.ir_callback = ir_callback
        self.magnetic_callback = magnetic_callback
        self.pushtocross_callback = pushtocross_callback
        self.internal_callback = internal_callback
        self.broadcast_callback = broadcast_callback
        self.emergency_callback = emergency_callback

        self.pin_vibration = pin_vibration
        self.pin_nfc = pin_nfc
        self.pin_ir = pin_ir
        self.pin_magnetic = pin_magnetic
        self.pin_pushtocross = pin_pushtocross
        self.pin_internal = pin_internal
        self.pin_broadcast = pin_broadcast
        self.pin_emergency = pin_emergency
        
        self.pin_led_green = pin_led_green
        self.pin_led_red = pin_led_red

        self.pwd=os.path.dirname(__file__)


    def setup(self):
        # configure default audio output
        os.system("amixer -q cset numid=3 1")
        # hijack the Ctrl+C event and run teardown()
        signal.signal(signal.SIGINT, self.teardown)

        # setup the board type and clean the board config
        GPIO.setmode(GPIO.BOARD)
        GPIO.cleanup()
        
        # configure inputs and outputs
        GPIO.setup(self.pin_vibration, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pin_ir, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pin_internal, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pin_pushtocross, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pin_led_green, GPIO.OUT)
        GPIO.setup(self.pin_led_red, GPIO.OUT)

        # add an event listener and callback function for the tilt switch
        GPIO.add_event_detect(self.pin_vibration, GPIO.RISING, bouncetime=900)
        GPIO.add_event_callback(self.pin_vibration, self.vibration_callback, bouncetime=900)

        # add an event listener and callback function for the IR switch
        GPIO.add_event_detect(self.pin_ir, GPIO.RISING, bouncetime=500)
        GPIO.add_event_callback(self.pin_ir, self.ir_callback, bouncetime=500)

        # add an event listener and callback function for the INTERNAL switch
        GPIO.add_event_detect(self.pin_internal, GPIO.RISING, bouncetime=500)
        GPIO.add_event_callback(self.pin_internal, self.internal_callback, bouncetime=500)
        
        # add an event listener and callback function for the EXTERNAL switch
        GPIO.add_event_detect(self.pin_pushtocross, GPIO.RISING, bouncetime=500)
        GPIO.add_event_callback(self.pin_pushtocross, self.pushtocross_callback, bouncetime=500)

        # turn on the LEDs for 1 seconds to indicated that player booted up
        self.toggleGreenLed()
        self.toggleRedLed()
        time.sleep(1)
        self.toggleGreenLed()
        self.toggleRedLed()
        # wait until Ctrl+C is pressed
        signal.pause()


    def teardown(self, signal, frame):
        """
        Will close the app in a nice way.
        """
        # turn off the LEDs
        GPIO.output(self.pin_led_green, False) # turn the LED off
        GPIO.output(self.pin_led_red, False)
        # cleant the board config
        GPIO.cleanup()
        # terminate the app
        sys.exit(0)

        
    def toggleGreenLed(self):
        GPIO.output(self.pin_led_green, not GPIO.input(self.pin_led_green))


    def toggleRedLed(self):
        GPIO.output(self.pin_led_red, not GPIO.input(self.pin_led_red))


    def input(self, channel):
        return GPIO.input(channel)


    def playMp3(self, filename, volume=40):
        proc_cmd = "nohup mpg321 -q -g {} {}/audio/{} &".format(volume,
                                                               self.pwd,
                                                               filename)
        player_proc = subprocess.Popen(proc_cmd,
                                       shell=True,
                                       preexec_fn=os.setsid)
        print "Player process: {}".format(player_proc.pid)
        return player_proc

