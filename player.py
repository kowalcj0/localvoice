#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
import os
import signal # to handle Ctrl+C
import sys

class Player():

    def __init__(self,
                IR_SWITCH_CALLBACK,
                INTERNAL_SWITCH_CALLBACK,
                EXTERNAL_SWITCH_CALLBACK,
                TILT_SWITCH_CALLBACK,
                PIN_IR_SWITCH=8,
                PIN_INTERNAL_SWITCH=25,
                PIN_EXTERNAL_SWITCH=13,
                PIN_TILT_SWITCH=11,
                PIN_LED_GREEN=18,
                PIN_LED_RED=16):
        """
        Sets the Player with default pinout if not provided
        """
        self.IR_SWITCH_CALLBACK = IR_SWITCH_CALLBACK
        self.INTERNAL_SWITCH_CALLBACK = INTERNAL_SWITCH_CALLBACK
        self.EXTERNAL_SWITCH_CALLBACK = EXTERNAL_SWITCH_CALLBACK
        self.TILT_SWITCH_CALLBACK = TILT_SWITCH_CALLBACK

        self.PIN_IR_SWITCH = PIN_IR_SWITCH
        self.PIN_INTERNAL_SWITCH = PIN_INTERNAL_SWITCH
        self.PIN_EXTERNAL_SWITCH = PIN_EXTERNAL_SWITCH
        self.PIN_TILT_SWITCH = PIN_TILT_SWITCH
        
        self.PIN_LED_GREEN = PIN_LED_GREEN
        self.PIN_LED_RED = PIN_LED_RED

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
        GPIO.setup(self.PIN_LED_GREEN, GPIO.OUT) # green led
        GPIO.setup(self.PIN_LED_RED, GPIO.OUT) # red led
        GPIO.setup(self.PIN_TILT_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.PIN_EXT_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # add an event listener and callback function for the ext switch
        GPIO.add_event_detect(self.PIN_EXT_SWITCH, GPIO.RISING, bouncetime=500)
        GPIO.add_event_callback(self.PIN_EXT_SWITCH, self.EXT_SWITCH_CALLBACK, bouncetime=500)
        #GPIO.add_event_callback(self.PIN_EXT_SWITCH, self.extSwitchCallBack, bouncetime=200)
        # add an event listener and callback function for the tilt switch
        GPIO.add_event_detect(self.PIN_TILT_SWITCH, GPIO.RISING, bouncetime=500)
        GPIO.add_event_callback(self.PIN_TILT_SWITCH, self.TILT_SWITCH_CALLBACK, bouncetime=500)
        #GPIO.add_event_callback(self.PIN_TILT_SWITCH, self.tiltSwitchCallBack, bouncetime=500)
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
        GPIO.output(self.PIN_LED_GREEN, False) # turn the LED off
        GPIO.output(self.PIN_LED_RED, False)
        # cleant the board config
        GPIO.cleanup()
        # terminate the app
        sys.exit(0)
        
    def toggleGreenLed(self):
        GPIO.output(self.PIN_LED_GREEN, not GPIO.input(self.PIN_LED_GREEN))

    def toggleRedLed(self):
        GPIO.output(self.PIN_LED_RED, not GPIO.input(self.PIN_LED_RED))

    def input(self, channel):
        return GPIO.input(channel)

    def playMp3(self, filename, volume=40):
        try:
           with open('%s/audio/%s' % (self.pwd, filename)): 
               os.system("mpg321 -q -g {} {}/audio/{}".format(volume,
                                                              self.pwd,
                                                              filename))
        except IOError:
            print "Couldn't find audio file: ./audio/%s" % filename

    @staticmethod
    def tiltSwitchCallBack(channel):
        if GPIO.input(channel):
            #GPIO.output(self.PIN_LED_GREEN, not GPIO.input(self.PIN_LED_GREEN))
            print "Tilt switch triggered", time.time()

    @staticmethod
    def extSwitchCallBack(channel):
        if GPIO.input(channel):
            #GPIO.output(self.PIN_LED_RED, not GPIO.input(self.PIN_LED_RED))
            print "Ext Switch Pressed", time.time()


if __name__ == "__main__":
    p=Player(TILT_SWITCH_CALLBACK=Player.tiltSwitchCallBack,
            EXT_SWITCH_CALLBACK=Player.extSwitchCallBack)
    p.setup()
