# -*- coding: utf-8 -*-
import json
import os
import sys
import time

from light_controller.ir_toy.ir_toy import IR_Toy

__author__ = 'akm'


class LightController:
    """
    IR Light Controller interface

    Controls several RGB LED globes and strips that use a common 24 button
    IR remote to change colours.

    They use slightly different protocols you can record the buttons to store
    in JSON which is loaded by this class.

    :param comPort: Serial device to connect to.
    """
    buttonNames = (
        'brightnessDown', 'brightnessUp', 'off', 'on',
        'red', 'green', 'blue', 'white',
        'red2', 'green2', 'blue2', 'flash',
        'orange', 'cyan', 'purple', 'strobe',
        'orange2', 'cyan2', 'violet', 'fade',
        'yellow', 'teal', 'lavender', 'smooth'
    )
    _colours = (
        'red', 'green', 'blue', 'white',
        'red2', 'green2', 'blue2',
        'orange', 'cyan', 'purple',
        'orange2', 'cyan2', 'violet',
        'yellow', 'teal', 'lavender',
    )
    _commands = (
        'brightnessUp', 'brightnessDown',
        'flash', 'strobe', 'fade', 'smooth',
    )

    def __init__(self, comPort, buttons='buttons.json'):
        self.toy = IR_Toy(comPort)
        self._buttons = {}
        self._buttonsFile = buttons
        self.loadButtons()

    def loadButtons(self):
        """
        Load button codes from the file
        :return: None
        """
        if os.path.exists(self._buttonsFile):
            with open(self._buttonsFile, 'rb') as fp:
                buttons = json.load(fp)
                self._buttons = buttons

    def getSettings(self):
        """
        Return the IR Toy settings
        """
        return self.toy.getSettings()

    def recordButton(self, button, dump=True):
        """
        Record a single button press

        :param button: Name of the button
        :param dump: Whether to save the current button list
        """
        self.toy.reset()
        self.toy.setSamplingMode()
        print("Press {}".format(button))
        sys.stdout.flush()
        irCode = self.toy.receiveSignal()
        self._buttons[button] = irCode
        if dump:
            self.dumpButtons()

    def dumpButtons(self):
        """
        Record All The Buttons!
        Saves the buttons into the configured button file
        """
        with open(self._buttonsFile, 'wb') as fp:
            json.dump(self._buttons, fp)

    def recordButtons(self):
        """
        Record button presses from the remote
        :return: SFA
        """
        print("Protocol Version:", self.toy.protocolVersion)
        for button in sorted(self.buttonNames):
            self.recordButton(button, dump=False)
        self.dumpButtons()

    def lightsOn(self):
        """
        Turn the lights on
        :return:
        """
        self.toy.transmitCode(self._buttons['on'])

    def lightsOff(self):
        """
        Turn the lights off
        :return:
        """
        self.toy.transmitCode(self._buttons['off'])

    def setColour(self, colour):
        """
        Change the light colours
        :param colour: Colour name from :mod:`getColours`
        :return: None
        """
        if colour in self._colours:
            self.toy.transmitCode(self._buttons[colour])

    def sendCommand(self, command):
        """
        Send a command
        :param command: Command to send to the lights
        :return: None
        """
        if command in self._commands:
            self.toy.transmitCode(self._buttons[command])

    def getVersion(self):
        """
        Get version information from the IR Toy

        :returns: Hardware version, firmware version
        """
        return self.toy.getVersion()

    @property
    def colours(self):
        return self._colours

    @property
    def commands(self):
        return self._commands

    @property
    def protocolVersion(self):
        return self.toy.protocolVersion


if __name__ == '__main__':
    changer = LightController('/dev/ttyACM0')
    print(changer.protocolVersion)
    print(changer.getVersion())
    sys.stdout.flush()

    print("Turning lights on")
    changer.lightsOn()
    changer.setColour('white')
    time.sleep(1)
    try:
        done = False
        while (not done):
            done = True
            # for colour in ('red', 'green', 'blue'):
            #     print colour
            #     changer.setColour(colour)
            #     time.sleep(1)
            #
            # for colour in ('red2', 'green2', 'blue2'):
            #     print colour
            #     changer.setColour(colour)
            #     time.sleep(1)

            # for colour in ('orange', 'cyan', 'purple'):
            #     print colour
            #     changer.setColour(colour)
            #     time.sleep(1)
            #
            # for colour in ('orange2', 'cyan2', 'violet'):
            #     print colour
            #     changer.setColour(colour)
            #     time.sleep(1)

            for colour in ('yellow', 'teal', 'lavender'):
                print(colour)
                changer.setColour(colour)
                time.sleep(1)
            break
    finally:
        changer.setColour('white')
        print("Turning lights off")
        changer.lightsOff()
