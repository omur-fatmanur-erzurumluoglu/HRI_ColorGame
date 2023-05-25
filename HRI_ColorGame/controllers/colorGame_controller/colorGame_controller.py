"""colorGame_controller controller."""

from controller import Robot, Keyboard, LED, Motion
import random
import json
import socket
import time

colors = ['red', 'green', 'blue']
values = [0xff0000, 0x00ff00, 0x0000ff]

# the reference code
# https://github.com/cyberbotics/webots/blob/master/projects/robots/softbank/nao/controllers/nao_demo_python/nao_demo_python.py

class NaoRobot(Robot):
    PHALANX_MAX = 8

    # load motion files
    def loadMotionFiles(self):
        self.handwave = Motion('../motions/handwave.motion')
        self.step_right = Motion('../motions/SideStepRight.motion')
        self.step_left = Motion('../motions/SideStepLeft.motion')
        self.forwards =  Motion('../motions/forwards.motion')
        self.backwards =  Motion('../motions/backwards.motion')
        self.standup =  Motion('../motions/standup.motion')

    def findAndEnableDevices(self):
        # get the time step of the current world.
        self.timeStep = int(self.getBasicTimeStep())
        # camera
        self.cameraTop = self.getDevice("CameraTop")
        self.cameraBottom = self.getDevice("CameraBottom")
        self.cameraTop.enable(4 * self.timeStep)
        self.cameraBottom.enable(4 * self.timeStep)
        # accelerometer
        self.accelerometer = self.getDevice('accelerometer')
        self.accelerometer.enable(4 * self.timeStep)
        # gyro
        self.gyro = self.getDevice('gyro')
        self.gyro.enable(4 * self.timeStep)
        # gps
        self.gps = self.getDevice('gps')
        self.gps.enable(4 * self.timeStep)
        # inertial unit
        self.inertialUnit = self.getDevice('inertial unit')
        self.inertialUnit.enable(self.timeStep)
        # ultrasound sensors
        self.us = []
        usNames = ['Sonar/Left', 'Sonar/Right']
        for i in range(0, len(usNames)):
            self.us.append(self.getDevice(usNames[i]))
            self.us[i].enable(self.timeStep)
        # foot sensors
        self.fsr = []
        fsrNames = ['LFsr', 'RFsr']
        for i in range(0, len(fsrNames)):
            self.fsr.append(self.getDevice(fsrNames[i]))
            self.fsr[i].enable(self.timeStep)
        # there are 7 controlable LED groups in Webots
        self.leds = []
        self.leds.append(self.getDevice('ChestBoard/Led'))
        self.leds.append(self.getDevice('RFoot/Led'))
        self.leds.append(self.getDevice('LFoot/Led'))
        self.leds.append(self.getDevice('Face/Led/Right'))
        self.leds.append(self.getDevice('Face/Led/Left'))
        self.leds.append(self.getDevice('Ears/Led/Right'))
        self.leds.append(self.getDevice('Ears/Led/Left'))
        # get phalanx motor tags
        # the real Nao has only 2 motors for RHand/LHand
        # but in Webots we must implement RHand/LHand with 2x8 motors
        self.lphalanx = []
        self.rphalanx = []
        self.maxPhalanxMotorPosition = []
        self.minPhalanxMotorPosition = []
        for i in range(0, self.PHALANX_MAX):
            self.lphalanx.append(self.getDevice("LPhalanx%d" % (i + 1)))
            self.rphalanx.append(self.getDevice("RPhalanx%d" % (i + 1)))
            # assume right and left hands have the same motor position bounds
            self.maxPhalanxMotorPosition.append(self.rphalanx[i].getMaxPosition())
            self.minPhalanxMotorPosition.append(self.rphalanx[i].getMinPosition())
        # shoulder pitch motors
        self.RShoulderPitch = self.getDevice("RShoulderPitch")
        self.LShoulderPitch = self.getDevice("LShoulderPitch")
        # keyboard
        self.keyboard = self.getKeyboard()
        self.keyboard.enable(10 * self.timeStep)

    def startMotion(self, motion):
        # interrupt current motion
        if self.currentlyPlaying:
            self.currentlyPlaying.stop()

        # start new motion
        motion.play()
        self.currentlyPlaying = motion

    def __init__(self):
        Robot.__init__(self)
        self.currentlyPlaying = False

        # initialize stuff
        self.findAndEnableDevices()
        self.loadMotionFiles()

#
    def set_all_leds_color(self, rgb):
        # these leds take RGB values
        for i in range(0, len(self.leds)):
            self.leds[i].set(rgb)

    def main_loop(self):
        HOST = "127.0.0.1"
        PORT = 12345

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))

        n = random.randint(0, 2)
        print("The color is: " + colors[n])

        # open the LEDs according to the color
        self.set_all_leds_color(values[n])

        for i in range(5):
            if self.step(self.timeStep) != -1:
                pass

        # Main Loop
        turn = "child"
        while True:
            if self.step(self.timeStep) != -1:
                pass
            if turn == "child":
                message = {"step": "play", "color": colors[n]}
                msg = json.dumps(message)
                s.sendall(bytes(msg, encoding="utf-8"))
                while True:
                    try:
                        data = s.recv(1024)
                        break
                    except:
                        print("Nothing Response")
                data = data.decode("utf-8")
                print("Received: " + data)
                self.guess = data
                turn = "nao"

            if turn == "nao":
                if self.guess == colors[n]:
                    response = "correct"
                    print("Guessed Correctly")

                    # to solve the syncronization problem for motions
                    self.standup.play()
                    for i in range(200):
                        if self.step(self.timeStep) != -1:
                            pass

                    self.forwards.play()
                    for i in range(150):
                        if self.step(self.timeStep) != -1:
                            pass

                    self.backwards.play()
                    for i in range(150):
                        if self.step(self.timeStep) != -1:
                            pass

                    self.step_right.play()
                    for i in range(200):
                        if self.step(self.timeStep) != -1:
                            pass

                    self.step_left.play()
                    for i in range(200):
                        if self.step(self.timeStep) != -1:
                            pass

                    self.handwave.play()
                    for i in range(100):
                        if self.step(self.timeStep) != -1:
                            pass

                if self.guess == "hint":
                    response = "none"
                    print("Giving hint about " + colors[n])
                if self.guess != colors[n]:
                    response = "wrong"
                    print("Guessed Wrongly")

                    # to solve the syncronization problem for motions
                    self.handwave.play()
                    for i in range(100):
                        if self.step(self.timeStep) != -1:
                            pass

            if response == "correct":
                turn = "child"
                return
            else:
                turn = "child"

            if self.step(self.timeStep) == -1:
                break


# create the Robot instance.
nao = NaoRobot()
nao.main_loop()