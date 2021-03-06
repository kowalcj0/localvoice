#!/usr/bin/env python

import os
from urllib import urlencode
from urllib2 import urlopen, URLError, HTTPError, Request
import json


STYPES = {
        1: 'Vibration',
        2: 'NFC',
        3: 'IR',
        4: 'Magnetic',
        5: 'PushToCross',
        6: 'Internal',
        7: 'Broadcast',
        8: 'Emergency'
        }


class LV:
    """
    Local Voice main class
    """

    def __init__(self,
                SERVER="http://www.ht0004.mobi",
                PID="P137960410446628"):
        """
        Initiates object with default SERVER AND PID values.
        """
        self.SERVER=SERVER
        self.PID=PID
        self.SCHED_CTX="/api/players/%s/schedule" % self.PID
        self.RETR_CTX="/api/players/%s/retrieved"  % self.PID
        self.SCHED_URL="%s%s" % (self.SERVER,self.SCHED_CTX)
        self.RETR_URL="%s%s" % (self.SERVER,self.RETR_CTX)
        self.RESET_2NULL_URL="%s%s" % (self.SERVER,"/debug/debug_processor.php?action=reset_to_null&value=0")

    def getSchedule(self):
        """Gets the schedule.
        Returns the serialize JSON response as a dictionary.
        An empty one if something went wrong or schedule was empty."""
        try:
            req = urlopen(self.SCHED_URL)
            if (req.getcode() != 200):
                print "Something's wrong! Resp.code is %s" % req.getcode()
                return {}
            j=json.load(req)
            if j['schedule'] == []:
                return {}
            else:
                return j
        #handle errors
        except HTTPError, e:
            print "HTTP Error:", e.code, self.SCHED_URL
        except URLError, e:
            print "URL Error:", e.reason, self.SCHED_URL
            

    def dlFile(self, url):
        """Download a file from provided URL"""
        # Open the url
        try:
            f = urlopen(url)
            print "Downloading " + url
            # Open our local file for writing
            #with open("audio/"+os.path.basename(url), "wb") as local_file:
                #local_file.write(f.read())
        #handle errors
        except HTTPError, e:
            print "HTTP Error:", e.code, url
        except URLError, e:
            print "URL Error:", e.reason, url


    def dlAllFiles(self, urls):
        """Downloads all the files specified in the passed list.
            Return True if all files were downloaded successfully and False otherwise"""
        if urls:
            for url in urls:
                self.dlFile(url)
                print "Downloaded file: %s " % url
            return True
        else:
            return False


    def getDlUrls(self, json):
        """Extracts all the audio file URLs
        Returns a list of the URLs to download"""
        urls=[]
        if json:
            for ad in json["schedule"]:
                urls.append(ad["filename"])
        return urls


    def confirmScheduleRetrieval(self):
        """Sends a POST request that confirms that schedule and all the audio
        files were downloaded successfully. 
        Doesn't return anything.
        """
        values={}
        data=urlencode(values)
        # Open the url
        try:
            req=Request(self.RETR_URL, data)
            resp=urlopen(req)
            print "Send a retrieval confirmation to %s.\nServer response: '%s'\n" % (self.RETR_URL, resp.read())
        #handle errors
        except HTTPError, e:
            print "HTTP Error:", e.code, req
        except URLError, e:
            print "URL Error:", e.reason, req


    def getHighestBid(self, json):
        if json:
            for ad in json['schedule']:
                if ad['priority'] == 1:
                    return ad
        else:
           return ()

    
    def get_adverts(self, json, stype):
        """
        Return adverts of given type, and return None if no advert was found.
        :param type: an type of the sensor (should be an int in quoutes)
        """
        result = []
        for ad in filter(lambda x: 'stype' in x and x['stype'] == stype,
                         json['schedule']):
            print "Found ad for '{}' sensor type: {}".format(STYPES[int(stype)],
                                                             stype)
            result.append(ad)
        return result
        

    def adminResetToNull(self):
        """
        Makes an request that resets all the schedules to NULL
        """
        try:
            print "Resetting schedule to null"
            req = urlopen(self.RESET_2NULL_URL)
            if (req.getcode() != 200):
                print "Something's wrong! Resp.code is %s" % req.getcode()
        #handle errors
        except HTTPError, e:
            print "HTTP Error:", e.code, self.RESET_2NULL_URL
        except URLError, e:
            print "URL Error:", e.reason, self.RESET_2NULL_URL

