# -*- coding: utf-8 -*-
import sys
import time
import threading

import requests

from light_controller import LightController


class BuildBotSession:
    failColour = "red"
    busyColour = "orange"
    goodColour = "green"
    exceptionColour = "purple"

    def __init__(self, builderURL, slaveName):
        self.builderURL = builderURL
        self.slaveName = slaveName
        self._statusURL = "{}/json/builders/{}".format(self.builderURL,
                                                       self.slaveName)

        self.lightController = LightController("/dev/ttyACM0",
                                               "data/buttons.json")
        self.lightController.lightsOn()
        self.lightController.setColour('white')

    def __del__(self):
        self.lightController.lightsOff()

    def start(self):
        """
        Poll as a thread
        """
        poller = threading.Thread(
            target=self.getStatus)
        poller.run()
        poller.join()

    def getStatus(self):
        """
        Get the general status of the builder
        Runs continuously, polls every 60 seconds
        """
        while True:
            status = requests.get(self._statusURL)
            returned = status.json()
            state = returned['state']
            if state == 'idle':
                self.getBuildStatus()
            if state == 'building':
                self.setBuildingState()
            time.sleep(60)

    def getBuildStatus(self):
        """
        Get the status for the builder
        """
        statusURL = "{}/builds".format(self._statusURL)
        params = {'select': '-1'}
        status = requests.get(statusURL, params=params)
        returned = status.json()['-1']
        if int(returned.get("results", 0)):
            if returned["results"] == 5:
                self.setExceptionState()
            else:
                self.setFailState()
        else:
            self.setGoodState()

    def setFailState(self):
        print("Fail")
        sys.stdout.flush()
        self.lightController.setColour(self.failColour)

    def setGoodState(self):
        print("Good")
        sys.stdout.flush()
        self.lightController.setColour(self.goodColour)

    def setBuildingState(self):
        print("Busy")
        sys.stdout.flush()
        self.lightController.setColour(self.busyColour)

    def setExceptionState(self):
        print("Exception")
        sys.stdout.flush()
        self.lightController.setColour(self.exceptionColour)


if __name__ == '__main__':
    session = BuildBotSession('http://forge-linux.aka.assurance.com',
                              'CloudBrowse Builder')
    session.getStatus()
