#!/usr/bin/env python

from lv import LV
from player import Player
import os
import signal
import timeit
import time


class LVService():

    def __init__(self):
        self.lv=LV()
        self.lv.adminResetToNull()
        # define for how many seconds movement trigger should do nothing
        self.movement_playback_timer = timeit.timeit()
        self.movement_playback_timer_threshold = 120
        self.player_processes = []

        retry_counter = 0
        retry_number = 5
        retry_every_s = 10  # in seconds

        self.refresh_schedule()

        while not self.schedule and (retry_counter < retry_number):
            retry_counter += 1
            print ("No schedule for me - #{} Retrying in {}s "
                  ).format(retry_counter, retry_every_s)
            time.sleep(retry_every_s)
            self.refresh_schedule()

        if self.schedule:
            # setup the player using custom callback functions
            self.player=Player(IR_SWITCH_CALLBACK=self.ir_switch_callback,
                               INTERNAL_SWITCH_CALLBACK=self.internal_switch_callback,
                               EXTERNAL_SWITCH_CALLBACK=self.external_switch_callback,
                               TILT_SWITCH_CALLBACK=self.tilt_switch_callback)
            self.player.setup()


    def refresh_schedule(self):
        """
        Gets the current schedule, then 
        """
        self.schedule=self.lv.getSchedule()
        if self.schedule:
            print "Got a schedule containing: %d item(s)" % len(self.schedule['schedule'])
            print self.schedule['schedule']
            self.urls=self.lv.getDlUrls(self.schedule)

            #print "List of audio URLs to download \n %s \n" % u
            if self.lv.dlAllFiles(self.urls):
                self.lv.confirmScheduleRetrieval()

                self.audio_movement = self.lv.get_adverts(self.schedule, u'1')
                self.audio_nfc = self.lv.get_adverts(self.schedule, u'2')
                self.audio_ir = self.lv.get_adverts(self.schedule, u'3')
                self.audio_magnetic = self.lv.get_adverts(self.schedule, u'4')
                self.audio_pushtocross = self.lv.get_adverts(self.schedule, u'5')
                self.audio_internal = self.lv.get_adverts(self.schedule, u'6')
                self.audio_broadcast = self.lv.get_adverts(self.schedule, u'7')
                self.audio_emergency = self.lv.get_adverts(self.schedule, u'8')

                return True
        else:
            return False


    def ir_switch_callback(self, channel):
        """
        Custom callback method passed to the Player. 
        Should be executed when IR event is detected
        """
        if self.player.input(channel):
            print "IR switch callback"
            if self.audio_ir:
                current_timer = timeit.timeit()
                if ((self.movement_playback_timer - current_timer)*1000 <
                    self.movement_playback_timer_threshold):
                    audio = os.path.basename(self.audio_ir[0]['filename'])
                    vol = self.audio_ir[0]['avolume']
                    self.player.toggleRedLed()
                    if self.player_processes:
                        print "IR: Already playing audio"
                    else:
                        self.movement_playback_timer = timeit.timeit()
                        self.player_processes.append(self.player.playMp3(audio, vol))
                else:
                    print "IR: sensor was triggered to quickly"
                    if ((self.movement_playback_timer - current_timer)*1000 <
                        self.movement_playback_timer_threshold):
                        print "Resetting the IR timer"
                        self.movement_playback_timer = timeit.timeit()
            else:
                print "No ad to play for IR switch"


    def magnetic_switch_callback(self, channel):
        """
        Custom callback method passed to the Player. 
        Should be executed when IR event is detected
        """
        if self.player.input(channel):
            print "Magnetic switch callback"
            if self.audio_magnetic:
                audio = os.path.basename(self.audio_magnetic[0]['filename'])
                vol = self.audio_magnetic[0]['avolume']
                self.player.toggleRedLed()
                if self.player_processes:
                    print "Magnetic: Already playing audio"
                else:
                    self.player_processes.append(self.player.playMp3(audio, vol))
            else:
                print "No ad to play for Magnetic switch"


    def internal_switch_callback(self, channel):
        """
        Custom callback method passed to the Player. 
        Should be executed when an event from internal switch is detected
        """
        if self.player.input(channel):
            print "Internal switch callback"
            self.player.toggleGreenLed()
            if self.audio_internal:
                audio = os.path.basename(self.audio_internal[0]['filename'])
                vol = self.audio_internal[0]['avolume']
                self.player.toggleRedLed()
                if self.player_processes:
                    print "Internal Button: Already playing audio"
                else:
                    self.player_processes.append(self.player.playMp3(audio, vol))
            else:
                print "No ad to play for Internal Button"


    def tilt_switch_callback(self, channel):
        """
        Custom callback method passed to the Player. 
        Should be executed when tilt event is detected
        """
        if self.player.input(channel):
            print "tilt switch callback"
            if self.audio_movement:
                audio = os.path.basename(self.audio_movement[0]['filename'])
                vol = self.audio_movement[0]['avolume']
                self.player.toggleRedLed()
                if self.player_processes:
                    print "Already playing audio"
                else:
                    self.player_processes.append(self.player.playMp3(audio, vol))
            else:
                print "No ad to play for Tilt/Movement switch"


    def stop_playback(self):
        """
        kill the server subprocess group
        """

        if self.player_processes:

            for pid in self.player_processes:
                print "\nKilling the player process: {}".format(pid)
                os.killpg(pid.pid, signal.SIGTERM)
            self.player_processes = []


    def external_switch_callback(self, channel):
        """
        Custom callback method passed to the Player. 
        Should be executed when an event from external switch is detected
        """
        if self.player.input(channel):
            print "External switch callback"
            self.player.toggleGreenLed()

            if self.player_processes:
                print "Stopping playback"
                self.stop_playback()

            print "refreshing schedule"
            self.refresh_schedule()


if __name__ == "__main__":
    srvs=LVService()
