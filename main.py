import time
import segments

# PIN connections
NP_PIN = 0

# initiate the display Object from Segments class
display = segments.Segments(NP_PIN, addrOfset=0, ledPerSegment=3, ledPerDot=1, numDisplay=4)

# Set segment 0 to value 0 in blue
display.setSegment(0, 0, (0, 0, 255))
# Set segment 1 to value 5 in blue
display.setSegment(1, 5, (0, 0, 255))
# Set segment 0 to value E in blue
display.setSegment(2, "E", (0, 0, 255))
# Set segment 0 to off
display.setSegment(3, None)

time.sleep(3)

# set the first 2 segments to display 10 in red
display.setDoubleSegment(0, 10, (100, 0, 0))
# set the second 2 displays to display 42 in red
display.setDoubleSegment(2, 42, (100, 0, 0))

# set the dots on and white
display.setDots(True, (100, 100, 100))

time.sleep(3)
# set the dots off
display.setDots(False)

display.demo()
