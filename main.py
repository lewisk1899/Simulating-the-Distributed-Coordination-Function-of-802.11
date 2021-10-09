import math
import numpy as np

DIFS, ACK, RTS, CTS = 2
SIFS = 1
CW_0 = 4
CW_MAX = 1024


class medium:
    def __init__(self):
        self.occupied = False
        self.successful_arrivals = 0
        self.collisions = 0


class transmitter:
    def __init__(self):
        self.buffer = []


def poisson_distributed_arrival_timings(arrival_rate):
    frames_needed = arrival_rate * 10  # For instance, when λ = 200 frames per second, you will need approximately 2,000 frames to fill arrivals for 10 seconds. That means you need to draw 2,000 at random in (0, 1).
    uniform_number = np.random.uniform(0.0, 1.0, frames_needed)
    i = 0
    for u_num in uniform_number:  # converting the uniform distributed values to that of an exponentially distributed value
        x_num = -(1 / arrival_rate) * np.log(1 - u_num)  # X = (−1/λ)ln(1 − U).
        uniform_number[i] = x_num * 10 ** 6  # create a new array with the altered values
        i += 1
    arrival_times = conversion(
        uniform_number)  # convert the array to be of values at the current index added to the previous
    # i.e. [x1, x2, x3] will become [x1, x1 + x2, x1 + x2 + x3] and so on
    del uniform_number  # free up the memory
    return arrival_times  # time of arrival is in microseconds


def conversion(x):
    y = [0.0] * len(x)
    i = 1
    while (i < len(x)):
        y[i - 1] = sum(x[:i])
        i += 1
    y[len(x) - 1] = sum(x)
    return y


# what happens around arrival,
        # what are the conditions for an arrival???
def medium_analyzer():

def csma_ca_protocol(arrival_times_station_a, arrival_times_station_c):

    # what happens around transmission? what are the conditions for a transmission
        # conditions: ba < bc or bc < ba or ba = bc
    if(ba == bc):
        # they both transmit
    elif(bc < ba):
        # bc transmits
    else:
        # ba transmits


    # what happens at a collision, what causes a collision
        # what causes a collision


    # stations wait a DIFS time
    # chooses the initial backoff values
    backoff_a = np.random.uniform(0.0, CW_0 - 1, 1)
    backoff_c = np.random.uniform(0.0, CW_0 - 1, 1)
    # count down backoff values
    # send frame when backoff is 0

    # how do we interpret a collision

    print("nothing")


def main():
    arrival_times_station_a = poisson_distributed_arrival_timings(200)
    arrival_times_station_c = poisson_distributed_arrival_timings(200)


main()
