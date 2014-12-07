#!/usr/bin/env python

from lv import LV, STYPES
from player import Player
import os
import signal
import time


class LVService():

    def __init__(self):
        self.lv=LV()
        self.lv.adminResetToNull()
        # define for how many seconds ir trigger should do nothing
        self.ir_enabled = True
        self.ir_playback_timer = time.time()
        self.ir_playback_timer_threshold = 120  # in seconds
        # list of all mpg321 processes, used for killing stale processes
        self.player_processes = []
        #player in use flag
        self.playing = False
        # schedule fetch retry scheme settings
        retry_counter = 0
        retry_number = 5
        retry_every_s = 10  # in seconds

        # try to get the schedule
        self.refresh_schedule()

        # try to fetch the schedule N-times
        while not self.schedule and (retry_counter < retry_number):
            retry_counter += 1
            print ("No schedule for me - #{} Retrying in {}s "
                  ).format(retry_counter, retry_every_s)
            time.sleep(retry_every_s)
            self.refresh_schedule()

        # configure the player if there is a schedule
        if self.schedule:
            # setup the player using custom callback functions
            self.player=Player(vibration_callback=self.vibration_callback,
                               nfc_callback=self.nfc_callback,
                               ir_callback=self.ir_callback,
                               magnetic_callback=self.magnetic_callback,
                               pushtocross_callback=self.pushtocross_callback,
                               internal_callback=self.internal_callback,
                               broadcast_callback=self.broadcast_callback,
                               emergency_callback=self.emergency_callback)
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

                self.audio_vibration = self.lv.get_adverts(self.schedule, u'1')
                self.audio_nfc = self.lv.get_adverts(self.schedule, u'2')
                self.audio_ir = self.lv.get_adverts(self.schedule, u'3')
                self.audio_magnetic = self.lv.get_adverts(self.schedule, u'4')
                self.audio_pushtocross = self.lv.get_adverts(self.schedule, u'5')
                self.audio_internal = self.lv.get_adverts(self.schedule, u'6')
                self.audio_broadcast = self.lv.get_adverts(self.schedule, u'7')
                self.audio_emergency = self.lv.get_adverts(self.schedule, u'8')


    def vibration_callback(self, channel):
        self.regular_playback(channel, self.audio_vibration)


    def nfc_callback(self, channel):
        self.regular_playback(channel, self.audio_nfc)


    def ir_callback(self, channel):
        """
        Custom callback method passed to the Player. 
        Should be executed when IR event is detected
        """
        if self.player.input(channel):
            print "IR switch callback"
            if self.audio_ir:
                diff = time.time() - self.ir_playback_timer
                print "Time diff={}".format(diff)
                if (diff > self.ir_playback_timer_threshold):
                    print "Re-enabling playback on IR trigger"
                    self.ir_enabled = True
                if not self.playing and self.ir_enabled:
                    if self.ir_enabled or (diff > self.ir_playback_timer_threshold):
                        self.playing = True
                        audio = os.path.basename(self.audio_ir[0]['filename'])
                        vol = self.audio_ir[0]['avolume']
                        self.player.toggleRedLed()
                        self.player_processes.append(self.player.playMp3(audio, vol))
                        self.ir_playback_timer = time.time()
                        print "Disabling playback on IR trigger for: {}s".format(self.ir_playback_timer_threshold)
                        self.ir_enabled = False
                        self.playing = False
                else:
                    wait = (self.ir_playback_timer_threshold - diff)
                    print "IR: sensor was triggered to quickly. Wait: {}s".format(wait)
            else:
                print "No ad to play for IR sensor"


    def magnetic_callback(self, channel):
        self.regular_playback(channel, self.audio_magnetic)


    def pushtocross_callback(self, channel):
        print "Push to cross callback"
        if self.player.input(channel):
            self.player.toggleGreenLed()

            if self.player_processes:
                print "Stopping playback"
                self.stop_playback()

            print "refreshing schedule"
            self.refresh_schedule()


    def internal_callback(self, channel):
        self.regular_playback(channel, self.audio_internal)


    def broadcast_callback(self, channel):
        self.regular_playback(channel, self.audio_broadcast)


    def emergency_callback(self, channel):
        self.regular_playback(channel, self.audio_emergency)


    def regular_playback(self, channel, ad):
        """
        Custom callback method passed to the Player. 
        Should be executed when tilt event is detected
        """
        if self.player.input(channel):
            stype = STYPES[int(ad[0]['stype'])]
            print "{} switch callback".format(stype)
            if ad:
                if not self.playing:
                    self.playing = True
                    audio = os.path.basename(ad[0]['filename'])
                    vol = ad[0]['avolume']
                    self.player.toggleRedLed()
                    self.player_processes.append(self.player.playMp3(audio, vol))
                    self.playing = False
                else:
                    print "Other ad is already playing"
            else:
                print "No ad to play for {} switch/sensor".format(stype)


    def stop_playback(self):
        """
        kill the server subprocess group
        """

        if self.player_processes:

            for pid in self.player_processes:
                print "\nKilling the player process: {}".format(pid)
                os.killpg(pid.pid, signal.SIGTERM)
            self.player_processes = []


if __name__ == "__main__":
    srvs=LVService()
