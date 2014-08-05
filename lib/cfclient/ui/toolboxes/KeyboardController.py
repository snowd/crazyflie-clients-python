__author__ = 'snowd'
__all__ = '[KeyboardController]'

import sys, time

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import Qt, pyqtSlot, pyqtSignal
import threading

keyboardcontroller_class = uic.loadUiType(sys.path[0] + "/cfclient/ui/toolboxes/keyboardControllerToolbox.ui")[0]

STEP_ROLL = 5
STEP_PITCH = 5
STEP_YAW = 5
STEP_THRUST = 8

RATIO_THRUST = 65535 / 100

OFFSET_ROLL = -4
OFFSET_PITCH = 2
OFFSET_YAW = 0.8

DEBUG = False


class FlieParams:

    def __init__(self):
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.thrust = 0.0


class KeyboardController(QtGui.QWidget, keyboardcontroller_class):

    def __init__(self, helper, *args):
        super(KeyboardController, self).__init__()
        self.setupUi(self)
        #self.update.connect(self.console.insertPlainText)
        self.helper = helper
        self.isenable = False
        self.updateCallback = None
        self.param = None

    def addUpdateCallback(self, callback):
        self.updateCallback = callback

    def keyPressEvent(self, event):
        if not self.isenable:
            return

        #print "key press >>> ", event.key()
        key = event.key()
        if key == Qt.Key_A:
            self.param.roll -= STEP_ROLL
        elif key == Qt.Key_D:
            self.param.roll += STEP_ROLL
        elif key == Qt.Key_W:
            self.param.pitch += STEP_PITCH
        elif key == Qt.Key_S:
            self.param.pitch -= STEP_PITCH

        elif key == Qt.Key_Left:
            self.param.yaw -= STEP_YAW
        elif key == Qt.Key_Right:
            self.param.yaw += STEP_YAW
        elif key == Qt.Key_Up:
            self.param.thrust += STEP_THRUST
            if self.param.thrust > 100:
                self.param.thrust = 100
        elif key == Qt.Key_Down:
            self.param.thrust -= STEP_THRUST
            if self.param.thrust < 0:
                self.param.thrust = 0

        elif key == Qt.Key_Q:
            self.param.roll = 0
            self.param.pitch = 0
            self.param.yaw = 0

        elif key == Qt.Key_E:
            self.param.roll = 0
            self.param.pitch = 0
            self.param.yaw = 0
            self.param.thrust = 0

    def getName(self):
        return "Keyboard Controller"

    def enable(self):
        self.isenable = True
        if self.param is None:
            self.param = UpdateTask(self.updateCallback)
        #self.param.setDaemon(True)
        self.param.start()

    def disable(self):
        self.isenable = False
        if self.param is not None:
            self.param.stop()
        self.param = None

    def preferedDockArea(self):
        return Qt.BottomDockWidgetArea


class UpdateTask(threading.Thread):

    def __init__(self, callback=None):
        super(UpdateTask, self).__init__()
        self.running = False
        self.callback = callback
        # flie data
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.thrust = 0.0

    def run(self):
        self.running = True
        while self.running:
            if DEBUG:
                print "running"
            if self.callback is None:
                print "none callback"
                time.sleep(3)
                continue

            if DEBUG:
                print "callback >>", self.roll, self.pitch, self.yaw, self.thrust
            self.callback.call(
                self.roll + OFFSET_ROLL,
                self.pitch + OFFSET_PITCH,
                self.yaw + OFFSET_YAW,
                self.thrust * RATIO_THRUST)

            time.sleep(0.01)

    def stop(self):
        self.running = False