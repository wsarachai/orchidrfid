import time
import re
import sys
import serial
from serial import Serial
import RPi.GPIO as GPIO

SEND_HEADER = 0xBA
cardPin = 21
serialPort = Serial("/dev/ttyS0", 115200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)

GetCardInformation = [0xBA, 0x02, 0x31]
GetBlcok0SecurityStatus = [0xBA, 0x04, 0x32, 0x0, 0x01]
ReadBlocks = [0xBA, 0x04, 0x33, 0x0, 0x10]
WriteBlock = [0xBA, 0x07, 0x34]
WriteAFI = [0xBA, 0x03, 0x35, 0xAA]
WriteDSFID = [0xBA, 0x03, 0x36, 0xBB]
LockBlock0 = [0xBA, 0x03, 0x37, 0x0]
LockAFI = [0xBA, 0x02, 0x38]
LockDSFID = [0xBA, 0x02, 0x39]
TrunOnRed = [0xBA, 0x03, 0x40, 0x01]
TrunOffRed = [0xBA, 0x03, 0x40, 0x0]


class SL015M:
  def __init__(self):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(cardPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(cardPin, GPIO.FALLING)
    GPIO.add_event_callback(cardPin, self.my_callback)

    self.taginfo = {
      'uid': [],
      'type': '',
      'afi': '',
      'dsfid': '',
      'status': ''
    }

    self.foundCard = False
    self.open()

  def open(self):
    if (serialPort.isOpen() == False):
      serialPort.open()

  def available(self):
    return serialPort.inWaiting() != 0

  def read(self):
    return serialPort.read()

  def read(self, n):
    return serialPort.read(n)

  def readline(self):
    return serialPort.readline()

  def waitAvailable(self):
    while True:
      if self.available():
        break

  def checkSum(self, data):
    csum = data[0]
    for i in range(len(data) - 1):
      csum = csum ^ data[i + 1]
    return csum

  def getCommand(self, data):
    cmd = chr(data[0])
    for i in range(len(data) - 1):
      cmd += chr(data[i + 1])
    cmd += chr(self.checkSum(data))
    return cmd

  def getResponse(self):
    while True:
      if (self.available() and ord(self.read(1)) == 0xBD):
        break

    self.waitAvailable()
    msg = hex(ord(self.read(1)))
    # print "LEN = " + msg

    self.waitAvailable()
    msg = hex(ord(self.read(1)))
    # print "CMD = " + msg

    self.waitAvailable()
    STATUS = ord(self.read(1))

    return STATUS

  def readTaginfo(self):
    frame = []
    frame.append(SEND_HEADER)
    frame.append(2);
    frame.append(0x31)
    serialPort.write(self.getCommand(frame))
    serialPort.flush()
    time.sleep(0.3)
    msg = ''

    STATUS = self.getResponse()

    if (STATUS == 0):  # Select Success
      self.taginfo['uid'] = []
      for i in range(8):
        self.waitAvailable()
        self.taginfo['uid'].append(hex(ord(self.read(1))))

      self.waitAvailable()
      self.taginfo['afi'] = hex(ord(self.read(1)))

      self.waitAvailable()
      self.taginfo['dsfid'] = hex(ord(self.read(1)))

      self.waitAvailable()
      self.taginfo['type'] = hex(ord(self.read(1)))

      self.waitAvailable()
      CHKSUM = hex(ord(self.read(1)))

  def readBlock(self, startblock, number):
    frame = []
    frame.append(SEND_HEADER)
    frame.append(4);
    frame.append(0x33)
    frame.append(startblock)
    frame.append(number)
    serialPort.write(self.getCommand(frame))
    serialPort.flush()
    time.sleep(0.3)
    msg = ''

    while True:
      if (self.available() and ord(self.read(1)) == 0xBD):
        break

    self.waitAvailable()
    LEN = ord(self.read(1))

    self.waitAvailable()
    msg = hex(ord(self.read(1)))

    self.waitAvailable()
    STATUS = ord(self.read(1))

    storedata = []

    if (STATUS == 0):  # Select Success
      for i in range(LEN - 3):
        self.waitAvailable()
        storedata.append(ord(self.read(1)))

      self.waitAvailable()
      CHKSUM = hex(ord(self.read(1)))

    return storedata

  def writeBlock(self, block, byte1, byte2, byte3, byte4):
    frame = []
    frame.append(SEND_HEADER)
    frame.append(7);
    frame.append(0x34)
    frame.append(block)
    frame.append(byte1)
    frame.append(byte2)
    frame.append(byte3)
    frame.append(byte4)
    serialPort.write(self.getCommand(frame))
    serialPort.flush()
    time.sleep(0.3)
    msg = ''

    STATUS = self.getResponse()

    storedata = []

    if (STATUS == 0):  # Select Success
      for i in range(4):
        self.waitAvailable()
        storedata.append(ord(self.read(1)))

      self.waitAvailable()
      CHKSUM = hex(ord(self.read(1)))

    return storedata

  def writeAFI(self, AFI):
    frame = []
    frame.append(SEND_HEADER)
    frame.append(3)
    frame.append(0x36)
    frame.append(AFI)
    serialPort.write(self.getCommand(frame))
    serialPort.flush()
    time.sleep(0.3)
    msg = ''

    return self.getResponse()

  def writeDSFID(self, DSFID):
    frame = []
    frame.append(SEND_HEADER)
    frame.append(3)
    frame.append(0x35)
    frame.append(DSFID)
    serialPort.write(self.getCommand(frame))
    serialPort.flush()
    time.sleep(0.3)
    msg = ''

    return self.getResponse()

  def LED(self, led):
    frame = []
    frame.append(SEND_HEADER)
    frame.append(3)
    frame.append(0x40)
    frame.append(led)
    serialPort.write(self.getCommand(frame))
    serialPort.flush()
    time.sleep(0.3)
    msg = ''

    return self.getResponse()

  def ledOn(self):
    self.LED(0x01)

  def ledOff(self):
    self.LED(0x00)

  def resetCardStatus(self):
    input = GPIO.input(cardPin)
    if (self.foundCard and input == GPIO.HIGH):
      self.foundCard = False;


  def cardInRange(self):
    input = GPIO.input(cardPin)
    if (self.foundCard and input == GPIO.LOW):
      return True
    else:
      return False

  def my_callback(self, val):
    self.foundCard = True

