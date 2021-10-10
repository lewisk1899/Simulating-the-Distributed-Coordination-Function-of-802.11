import math
import numpy as np

CW_0 = 4
CW_MAX = 1024

class Simulation:
    # a or b for topologies to be simulated, protocol will take string "csma with ca" or "vcs" as an input
    def __init__(self, _topology, _protocol, arrival_rate):
        # these are the variables of the parameters
        self.topology = _topology
        self.protocol = _protocol # find out which protocol will be used so the simulation will change parameters
        self.arrival_rate = arrival_rate

        # hard parameters of the simulation
        self.DIFS, self.ACK, self.RTS, self.CTS = 2
        self.SIFS = 1 # short interframe spacing is 2 slots long
        self.CW_0 = 4 #
        self.CW_MAX = 1024
        self.transmission_rate = 12 # 12 Mbps
        self.num_of_transmitters = 2 # for the purpose of this simulation the amount of transmitters will always be two

        # this is the type of stuff we are trying to measure
        self.num_of_collisions = 0
        self.num_of_successful_transmissions = 0

    def poisson_distributed_arrival_timings(self):
        frames_needed = self.arrival_rate * 10  # For instance, when λ = 200 frames per second, you will need approximately 2,000 frames to fill arrivals for 10 seconds. That means you need to draw 2,000 at random in (0, 1).
        uniform_number = np.random.uniform(0.0, 1.0, frames_needed)
        i = 0
        for u_num in uniform_number:  # converting the uniform distributed values to that of an exponentially distributed value
            x_num = -(1 / self.arrival_rate) * np.log(1 - u_num)  # X = (−1/λ)ln(1 − U).
            uniform_number[i] = x_num * 10 ** 6  # create a new array with the altered values
            i += 1
        arrival_times = self.conversion(
            uniform_number)  # convert the array to be of values at the current index added to the previous
        # i.e. [x1, x2, x3] will become [x1, x1 + x2, x1 + x2 + x3] and so on
        del uniform_number  # free up the memory
        return arrival_times  # time of arrival is in microseconds

    def conversion(self, x):
        y = [0.0] * len(x)
        i = 1
        while i < len(x):
            y[i - 1] = sum(x[:i])
            i += 1
        y[len(x) - 1] = sum(x)
        return y

    def csma_ca_protocol(self):

class Transmitter:
    def __init__(self):
        self.buffer = []
        self.arrivals = []
        self.back_off = 0
        self.contention_window_size = 4

    def update_contention_window(self, collision_status):
        # if failed transmission then increase the contention window size
        if(collision_status and self.contention_window_size < 1024):
            self.contention_window_size = 2*self.contention_window_size
        # failure of transmission but the contention window cannot grow any larger
        elif(collision_status and self.contention_window_size == 1024):
            self.contention_window_size = self.contention_window_size
        # successful transmission reset the contention window size
        else:
            self.contention_window_size = 4

    def get_back_off(self):
        return self.back_off
    # this function will be used when we are comparing back off counters and deciding when to freeze the transmitter
    def set_back_off(self, new_back_off):
        self.back_off = new_back_off



class medium:
    def __init__(self):
        self.occupied = False
        self.successful_arrivals = 0
        self.collisions = 0

# what happens around arrival,
        # what are the conditions for an arrival???

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
    _topology, _protocol, arrival_rate = "A", "CSMA_CA", 200
    simulation = Simulation(_topology, _protocol, arrival_rate)



main()
