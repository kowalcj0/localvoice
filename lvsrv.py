#!/usr/bin/env python

from lv import LV
from player import Player
import os


class LVService():

    def __init__(self):
        self.lv=LV()
        self.lv.adminResetToNull()
        if self.refreshSchedule():
            # setup the player using custom callback functions
            self.player=Player(TILT_SWITCH_CALLBACK=self.tiltSwitchCallback,
                               EXT_SWITCH_CALLBACK=self.extSwitchCallback)
            self.player.setup()

    def refreshSchedule(self):
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
                print self.highestBid
                print self.audiofile
                return True
        else:
            print "I've got nothing to do because I've received an empty schedule!"
            return False


    def tiltSwitchCallback(self, channel):
        """
        Custom callback method passed to the Player. 
        Should be executed when tilt event is detected
        """
        if self.player.input(channel):
            print "tilt switch callback"
            self.player.toggleRedLed()
            self.player.playMp3(self.audiofile)

    def extSwitchCallback(self, channel):
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
