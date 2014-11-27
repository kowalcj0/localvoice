#!/usr/bin/env python

from lv import LV
from player import Player
import os


class LVService():

    def __init__(self):
        self.lv=LV()
        self.lv.adminResetToNull()
        if self.refresh_schedule():
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
            self.urls=self.lv.getDlUrls(self.schedule)
            #print "List of audio URLs to download \n %s \n" % u
            if self.lv.dlAllFiles(self.urls):
                self.lv.confirmScheduleRetrieval()
                self.highestBid=self.lv.getHighestBid(self.schedule)
                self.audiofile=os.path.basename(self.highestBid['filename'])
                self.volume = int(self.schedule['schedule'][0]['avolume'])
                print self.highestBid
                print self.audiofile
                return True
        else:
            import ipdb; ipdb.set_trace()
            print "I've got nothing to do because I've received an empty schedule!"
            return False


    def ir_switch_callback(self, channel):
        """
        Custom callback method passed to the Player. 
        Should be executed when IR event is detected
        """
        if self.player.input(channel):
            print "IR switch callback"
            self.player.toggleRedLed()
            self.player.playMp3(self.audiofile, volume=self.volume)


    def internal_switch_callback(self, channel):
        """
        Custom callback method passed to the Player. 
        Should be executed when an event from internal switch is detected
        """
        if self.player.input(channel):
            print "internal ext switch callback"
            self.player.toggleGreenLed()
            self.refreshSchedule()


    def tilt_switch_callback(self, channel):
        """
        Custom callback method passed to the Player. 
        Should be executed when tilt event is detected
        """
        if self.player.input(channel):
            print "tilt switch callback"
            self.player.toggleRedLed()
            self.player.playMp3(self.audiofile, volume=self.volume)


    def external_switch_callback(self, channel):
        """
        Custom callback method passed to the Player. 
        Should be executed when an event from external switch is detected
        """
        if self.player.input(channel):
            print "ext switch callback"
            self.player.toggleGreenLed()
            self.refreshSchedule()


if __name__ == "__main__":
    srvs=LVService()
