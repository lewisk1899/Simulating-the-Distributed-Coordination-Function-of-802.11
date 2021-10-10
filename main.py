import math
import numpy as np

class Simulation:
    # a or b for topologies to be simulated, protocol will take string "csma with ca" or "vcs" as an input
    def __init__(self, protocol, topology, arrival_rate):
        # these are the variables of the simulation
        self.arrival_rate = arrival_rate
        self.topology = topology
        self.protocol = protocol
        # hard parameters of the simulation
        self.DIFS = 2
        self.ACK = 2
        self.RTS = 2
        self.CTS = 2
        self.SIFS = 1 # short interframe spacing is 2 slots long
        self.FRAME = 100
        self.CW_0 = 4 # initial contention window
        self.CW_MAX = 1024 # initial contention window max
        self.transmission_rate = 12 # 12 Mbps

        # empty placeholders for the transmitter objects
        self.transmitter_a = None
        self.transmitter_c = None
        self.transmitters = [self.transmitter_a, self.transmitter_c] # for the purpose of this simulation the amount of transmitters will always be two

        # this is the type of stuff we are trying to measure
        self.num_of_collisions = 0
        self.num_of_successful_transmissions = 0

    def poisson_distributed_arrival_timings(self):
        frames_needed = self.arrival_rate * 5  # For instance, when λ = 200 frames per second, you will need approximately 2,000 frames to fill arrivals for 10 seconds. That means you need to draw 2,000 at random in (0, 1).
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
        return [round(i/10) for i in arrival_times]  # time of arrival is in slots

    def conversion(self, x):
        y = [0.0] * len(x)
        i = 1
        while i < len(x):
            y[i - 1] = sum(x[:i])
            i += 1
        y[len(x) - 1] = sum(x)
        return y

    def set_transmitter_a(self, transmitter):
        self.transmitter_a = transmitter

    def set_transmitter_c(self, transmitter):
        self.transmitter_c = transmitter

    def csma_ca_protocol_topology_a(self):
        clock = 0
        collisions = 0
        while (len(self.transmitter_a.get_arrivals()) != 0 and len(self.transmitter_c.get_arrivals()) != 0):
            # frame has arrived at the buffer
            slot_num_for_a = self.transmitter_a.get_arrivals()[0]
            slot_num_for_c = self.transmitter_c.get_arrivals()[0]
            # these two statements are how we are going to compare who goes first
            x = self.transmitter_a.get_arrivals()[0] + self.DIFS + self.transmitter_a.select_back_off(collisions)
            y = self.transmitter_c.get_arrivals()[0] + self.DIFS + self.transmitter_c.select_back_off(collisions)
            if x < y:
                # generate a backoff value and transmit a frame
                print("frame arrived @ tx a, @slot: " , self.transmitter_a.get_arrivals()[0])
                print("a goes first @ slot number ", x)
                clock = x + self.FRAME + self.SIFS + self.ACK
                self.transmitter_a.set_arrivals(self.transmitter_a.get_arrivals()[1:])
            # station c is transmitting first
            elif x > y:
                self.transmitter_c.set_arrivals(self.transmitter_c.get_arrivals()[1:])
                print("frame arrived @ tx c, @slot:" , self.transmitter_c.get_arrivals()[0])
                print("c goes first @ slot number", y)
                clock = y + self.FRAME + self.SIFS + self.ACK
            # station a and c get their arrival so we must use their backoff values
            elif  x == y:
                collisions += 1
                print(collision)

    def csma_ca_protocol_topology_b(self):
        return None


    def csma_ca_with_vcs(self):
        return None

    def is_there_a_collision(self, protocol, topology):
        if self.protocol == "csma ca" and self.topology == "a":
            return None
        elif self.protocol == "csma ca" and self.topology == "b":
            return None
        elif self.protocol == "vcs" and self.topology == "a":
            return None
        elif self.protocol == "vcs" and self.topology == "b":
            return None


class Transmitter:
    def __init__(self, arrivals):
        self.buffer = []
        self.arrivals = arrivals # the list of arrival times when a frame is delivered from the application and ready to be transmitted
        self.back_off = 0
        self.contention_window_size = 4

    def update_contention_window(self, collision_status):
        # if failed transmission then increase the contention window size
        if collision_status and self.contention_window_size < 1024:
            self.contention_window_size = 2*self.contention_window_size
        # failure of transmission but the contention window cannot grow any larger
        elif collision_status and self.contention_window_size == 1024:
            self.contention_window_size = self.contention_window_size
        # successful transmission reset the contention window size
        else:
            self.contention_window_size = 4

    # adding a frame waiting at the buffer of the transmitter
    def add_to_buffer(self, arrival):
        self.buffer.append(arrival)

    # return the buffer
    def get_buffer(self):
        return self.buffer

    # getting the back off to use for comparison
    def get_back_off(self):
        return self.back_off

    def get_arrivals(self):
        return self.arrivals

    # decrementing
    def set_arrivals(self, arrivals):
        self.arrivals = arrivals

    # this function will be used when we are comparing back off counters and deciding when to freeze the transmitter
    def set_back_off(self, frozen_value):
        self.back_off = frozen_value

    # for picking the backoff value using a uniform distribution
    def select_back_off(self, collisions):
        self.back_off = np.random.randint(0, 2**collisions*self.contention_window_size - 1)
        return self.back_off

def test():
    x = [1,2,3]
    print(x[1:])

def main():
    _topology, _protocol, arrival_rate = "A", "CSMA_CA", 2
    simulation = Simulation(_topology, _protocol, arrival_rate)
    simulation.set_transmitter_a(Transmitter(simulation.poisson_distributed_arrival_timings())) # simulation of a setting transmitter a
    simulation.set_transmitter_c(Transmitter(simulation.poisson_distributed_arrival_timings())) # simulation of a setting transmitter c
    # up until here all the arrival times are generated and working, these numbers are good
    simulation.csma_ca_protocol_topology_a()
   # test()







main()
