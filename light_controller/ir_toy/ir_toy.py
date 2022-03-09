# -*- coding: utf-8 -*-
import logging
import time
import struct

import serial

from .ir_toy_settings import IR_ToySettings

__author__ = 'akm'


class CommandEnum:
    reset = 0x00
    SUMP_Run = 0x01
    SUMP_Id = 0x02
    transmit = 0x03
    getFrequencyReport = 0x04
    setSampleTimer = 0x05
    setFrequencyModulationTimer = 0x06
    setLED_MuteOn = 0x10
    setLED_MuteOff = 0x11
    setLED_On = 0x12
    setLED_Off = 0x13
    getSettingsReport = 0x23
    enableTX_ByteReport = 0x24
    enableTX_NotifyOnComplete = 0x25
    enableTX_Handshake = 0x26
    IO_Write = 0x30
    IO_Direction = 0x31
    IO_Read = 0x32
    IO_Direction = 0x31
    setupUART = 0x40
    closeUART = 0x41
    writeUART = 0x42


class IR_Toy:
    TERMINATOR = [255, 255]

    """
    0x00 Reset (returns to remote decoder mode)
    0x01 RESERVED for SUMP RUN
    0x02 RESERVED for SUMP ID
    0x03 Transmit (FW v07+)
    0x04 Frequency report (reserved for future hardware)
    0x05 Setup sample timer (FW v07+)
    0x06 Setup frequency modulation timer (FW v07+)
    0x10 LED mute on (FW v07+)
    0x11 LED mute off (FW v07+)
    0x12 LED on (FW v07+)
    0x13 LED off (FW v07+)
    0x23 Settings descriptor report (FW v20+)
    0x24 Enable transmit byte count report (FW v20+)
    0x25 Enable transmit notify on complete (FW v20+)
    0x26 Enable transmit handshake (FW v20+)
    0x30 IO write
    0x31 IO direction
    0x32 IO read
    0x40 UART setup
    0x41 UART close
    0x42 UART write
    """

    def __init__(self, comPort):
        self._connection = serial.Serial(comPort)
        self.protocolVersion = ""
        self.flush()
        self.setSamplingMode()

    def __del__(self):
        self.close()

    def close(self):
        if self._connection.isOpen():
            self._connection.close()

    def flush(self):
        """
        Flush the serial connection
        :return: None
        """
        self._connection.flushInput()
        self._connection.flush()
        self._connection.flushOutput()

    def read(self, num):
        """
        Read `num` bytes from the device
        :param num: Number of bytes to read
        :return: string of bytes
        """
        return self._connection.read(num)

    def write(self, data):
        """
        Write data to the device
        :param data: Data to be written
        :return: Number of bytes written
        """
        result = self._connection.write(data)
        return result

    def writeArray(self, data):
        """
        Write a list of bytes
        :param data: list of bytes
        :return: number of bytes written
        """
        bytes = bytearray(data)
        return self.write(bytes)

    def writeByte(self, data):
        """
        Convert a byte to char and write it out
        :param data: byte to write
        :return: number of bytes written
        """
        return self.writeArray([data, ])

    def enableTransmitMode(self):
        """
        Set transmission mode
        :return: Size of TX buffer
        """
        self.writeByte(CommandEnum.transmit)
        return ord(self.read(1))

    def getFrequencyReport(self):
        """
        Get the raw timing information for the previous IR signal

        :return: (timer at 2nd rising edge,
                  timer at 3rd rising edge,
                  timer at 4th rising edge,
                  total count of pulses since last 0xFF)
        """
        self.writeByte(CommandEnum.getFrequencyReport)
        buffer = self.read(8)
        return struct.unpack(">4H", buffer)

    def setSampleTimer(self, prescale):
        """
        The timer is 21.13333 us by default.
        111 (0x07)	1:256	21.3333uS
        110 (0x06)	1:128	10.6666uS
        101 (0x05)	1:64
        100 (0x04)	1:32
        011 (0x03)	1:16
        010 (0x02)	1:8
        001 (0x01)	1:4
        000 (0x00)	1:2
        :param prescale: see above for valid values
        :return: None
        """
        self.writeArray((CommandEnum.setSampleTimer, prescale))

    def setTX_Modulation(self, pr2, dutyCycle=0x0):
        """
        Configures the TX modulation of the IR Transmitter
        IR sample mode starts with a default 36kHz infrared transmit modulation frequency. The rate can be changed
        with the setup modulation command, followed by a byte that sets the pulse-width modulator match value (PR2),
        and a don't care byte.
        :param pr2: Pulse width modulator match value
        :param dutyCycle: Duty Cycle
        :return: None
        """
        self.writeArray((CommandEnum.setFrequencyModulationTimer, pr2, dutyCycle))

    def setMuteLED_On(self):
        """
        Disables the LED during sample mode
        :return: None
        """
        self.writeByte(CommandEnum.setLED_MuteOn)

    def setMuteLED_Off(self):
        """
        Enables the LED during sample mode
        :return: None
        """
        self.writeByte(CommandEnum.setLED_MuteOff)

    def setLED_On(self):
        """
        Turn the LED on
        :return: None
        """
        self.writeByte(CommandEnum.setLED_On)

    def setLED_Off(self):
        """
        Turn the LED off
        :return: None
        """
        self.writeByte(CommandEnum.setLED_Off)

    def getSettings(self):
        """
        Returns 8 bytes that describe the current IR Toy settings:

        Descriptor fields
        Bytes	Description
        1		PR2 value (PWM)
        1		Duty cycle
        1		PWM prescaler, 2 extra bits of duty cycle
        1		Transmit timer prescaler
        4		Clock frequency in Hz (eg 48,000,000Hz)
        :return: Descriptor Fields
        """
        self.writeByte(CommandEnum.getSettingsReport)
        settingsBuffer = self.read(8)
        print(len(settingsBuffer))
        report = IR_ToySettings(*struct.unpack(">BBBBL", settingsBuffer))
        return report

    def enableTX_ByteCount(self):
        """
        If enabled, the IR Toy returns the number of bytes transmitted at the end of a 0x03 command. The format is tXY,
        where XY is the 16bit count of bytes transmitted:

        't' is the character t
        X is the high 8 bits of byte count
        Y is the low 8 bits of byte count
        :return: None
        """
        self.writeByte(CommandEnum.enableTX_ByteReport)

    def enableTX_NotifyOnComplete(self):
        """
        If enabled, the IR Toy returns a success or error code at the end of a 0x03 transmit command.

        Notify on complete codes
        Code	Description
        C		Success, no errors, complete
        F		Buffer underrun during transmit
        :return: None
        """
        self.writeByte(CommandEnum.enableTX_NotifyOnComplete)

    def enableTX_Handshake(self):
        """
        If enabled, the IR Toy will request data packets during a transmit command. Each request is the number of bytes
        free in the USB buffer, currently always 62. The software interfacing the IR Toy should wait for each request
        before sending the data.
        :return: None
        """
        self.writeByte(CommandEnum.enableTX_Handshake)

    def reset(self):
        """
        Reset the device
        :return: None
        """
        self.writeArray(self.TERMINATOR)
        self.writeArray((CommandEnum.reset,) * 5)
        time.sleep(0.05)

    def getVersion(self):
        """
        Get the hardware and firmware versions
        :return: hardware string, firmware version
        """
        try:
            self.reset()
            self.writeByte(ord('v'))
            buffer = self.read(4)
            hardware, revision = struct.unpack('>2s2s', buffer)
            return hardware, int(revision)
        finally:
            self.setSamplingMode()

    def setTransmitMode(self):
        """
        Setup the device for transmitting.
        Enable handshakes and reports
        :return: TX buffer size
        """
        self.enableTX_Handshake()
        self.enableTX_ByteCount()
        self.enableTX_NotifyOnComplete()
        bufferSize = self.enableTransmitMode()
        return bufferSize

    def setSamplingMode(self):
        """
        Setup the device for sampling
        :return: None
        """
        self.reset()
        self.writeByte(ord('S'))
        self.protocolVersion = self.read(3)

    def receiveSignal(self):
        """
        Record a signal

        :return: List of bytes representing the ir code.
        """
        self.setSamplingMode()
        bytesToRead = 1
        readCount = 0
        irCode = []

        while (True):
            readByte = self.read(bytesToRead)
            if not readByte:
                continue
            readByte = ord(readByte)
            irCode.append(readByte)
            if irCode[-2:] == self.TERMINATOR:
                break
            readCount += 1
        return irCode

    def transmitCode(self, code):
        """
        Transmit an IR code
        :param code: A string of bytes to send in the same format as the recording
        :return: Success
        """
        if len(code) < 2 or len(code) % 2:
            raise ValueError("Length of code must be a multiple of 2")

        if code[-2:] != self.TERMINATOR:
            code.extend(self.TERMINATOR)

        idx = 0
        bytesSent = 0
        bufferSize = self.setTransmitMode()
        try:
            while bytesSent < len(code):
                sent = self.writeArray(code[idx:idx + bufferSize])
                idx += sent
                bytesSent += sent
                bufferSize = ord(self.read(1))

            # Wait for IR Toy to work out we're finished.
            time.sleep(0.05)
            completionReport = self.read(4)
            byteThing, bytesReported, complete = struct.unpack('>BHc', completionReport)

            if complete != 'C':
                self.reset()
                return False
            return True
        except:
            logging.error("Transmission abort", exc_info=True)
            self.reset()
        finally:
            self.setSamplingMode()
