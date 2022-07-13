#!/usr/bin/env python3

# Import the necessary libraries
import time
import math
from ev3dev2.motor import *
from ev3dev2.sound import Sound
from ev3dev2.button import Button
from ev3dev2.sensor import *
from ev3dev2.sensor.lego import *
from ev3dev2.sensor.virtual import *

# Create the sensors and motors objects
btn = Button()

lMotor = OUTPUT_A
rMotor = OUTPUT_B
tDrive = MoveTank(OUTPUT_A, OUTPUT_B)

cSensorL = ColorSensor(INPUT_1)
cSensorR = ColorSensor(INPUT_2)

uSensor = UltrasonicSensor(INPUT_3)


# Here is where your code starts


# Simple node class for the morse code tree
class Node:
    def __init__(self, c, dotnode=None, dashnode=None):
        self.char = c
        self.dotNode = dotnode
        self.dashNode = dashnode

    # Exceptions are raised if a null node is reached
    def dot(self):
        if (self.dotNode is None):
            raise Exception("Unexpected node access!")
        return self.dotNode

    def dash(self):
        if (self.dashNode is None):
            raise Exception("Unexpected node access!")
        return self.dashNode


global startNode


# Initialises all of the nodes in the standard morse code tree
def init():
    global startNode
    startNode = Node("",
                     Node("E",  # .
                          Node("I",  # ..
                               Node("S",  # ...
                                    Node("H",  # ....
                                         Node("5"),  # .....
                                         Node("4")),  # ....-
                                    Node("V",  # ...-
                                         None,
                                         Node("3"))),  # ...--
                               Node("U",  # ..-
                                    Node("F"),  # ..-.
                                    Node("",  # ..--
                                         None,
                                         Node("2")))),  # ..--.
                          Node("A",  # .-
                               Node("R",  # .-.
                                    Node("L"),  # .-..
                                    Node("",  # .-.-
                                         Node("+"))),  # .-.-.
                               Node("W",  # .--
                                    Node("P"),  # .--.
                                    Node("J",  # .---
                                         None,
                                         Node("1"))))),  # .----
                     Node("T",  # -
                          Node("N",  # -.
                               Node("D",  # -..
                                    Node("B",  # -...
                                         Node("6"),  # -....
                                         Node("=")),  # -...-
                                    Node("X",  # -..-
                                         Node("/"))),  # -..-.
                               Node("K",  # -.-
                                    Node("C"),  # -.-.
                                    Node("Y"))),  # -.--
                          Node("M",  # --
                               Node("G",  # --.
                                    Node("Z",  # --..
                                         Node("7")),  # --...
                                    Node("Q")),  # --.-
                               Node("O",  # ---
                                    Node("",  # ---.
                                         Node("8")),  # ---..
                                    Node("",  # ----
                                         Node("9"),  # ----.
                                         Node("0")  # -----
                                         )
                                    )
                               )
                          )
                     )


# Reads the Aggregated log data and prints the text to the console
def ReadAggregate(aData):
    curNode = startNode
    out = ""
    conCount = 0
    prevRead = -1
    for i in range(len(aData)):
        if (prevRead != aData[i]):
            if (prevRead == 0):
                if (conCount > 5 and conCount <= 15):
                    out += curNode.char
                    curNode = startNode
                elif (conCount > 15):
                    out += curNode.char
                    out += " "
                    curNode = startNode
            elif (prevRead == 1):
                if (conCount > 8):
                    curNode = curNode.dash()
                else:
                    curNode = curNode.dot()
            prevRead = aData[i]
            conCount = 0
        else:
            prevRead = aData[i]
            conCount += 1

    out += curNode.char

    print(out)


rSensorLog = []
lSensorLog = []
aSensorLog = []


# Check if sensor is reading the colour as Red, not White, etc.
def isRed(colorSensor):
    rgbOut = colorSensor.rgb
    if (rgbOut[0] > 245 and rgbOut[1] < 180 and rgbOut[2] < 180):
        return True
    return False


# Main Body
init()

# On startup, make sure we move off of the red starting line
while (isRed(cSensorL) or isRed(cSensorR)):
    tDrive.on(-10, -10)

tDrive.off()

time.sleep(0.5)

tDrive.on(10, 10)

# Writes the sensors' data to their own log arrays and, if an error is recieved by one sensor, the aggregate log
# stores the non-erroneous sensor's data
while (uSensor.distance_centimeters > 2):
    if (cSensorR.rgb[0] < 245):
        tDrive.on(2, 18)
        aSensorLog.append(int(isRed(cSensorL)))
        rSensorLog.append(-1)
        lSensorLog.append(int(isRed(cSensorL)))
    elif (cSensorL.rgb[0] < 245):
        tDrive.on(18, 2)
        aSensorLog.append(int(isRed(cSensorR)))
        rSensorLog.append(int(isRed(cSensorR)))
        lSensorLog.append(-1)
    else:
        tDrive.on(10, 10)
        aSensorLog.append(int(isRed(cSensorR)))
        rSensorLog.append(int(isRed(cSensorR)))
        lSensorLog.append(int(isRed(cSensorL)))

    time.sleep(0.1)  # Simple time step to allow for accurate logging of data

tDrive.off()

print("Left Log: " + str(lSensorLog))
print("Right Log: " + str(rSensorLog))
print("Aggregate Log: " + str(aSensorLog))

ReadAggregate(aSensorLog)
