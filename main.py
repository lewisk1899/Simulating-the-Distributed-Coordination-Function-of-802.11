# Lewis Koplon
# Simulating the Distributed Coordination Function of 802.11

import numpy as np


class Transmitter:
    def __init__(self, arrivals):
        self.buffer = []
        self.arrivals = arrivals
        self.backoff = 0
        self.contention_window_size = 4
        self.successes = 0
        self.difs = 4

    def generate_backoff(self):
        self.backoff = np.random.randint(0, self.contention_window_size - 1)

    def transmit_slot(self, arrival):
        self.t_slot = arrival + self.difs + self.backoff

    def gen_backoff(self, collisions):
        return np.random.randint(0, collisions * self.contention_window_size - 1)


class Simulation:
    def __init__(self, arrival_rate):
        self.arrival_rate = arrival_rate
        self.tx_a = None
        self.tx_c = None

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
        return [round(i / 10) for i in arrival_times]  # time of arrival is in slots

    def conversion(self, x):
        y = [0.0] * len(x)
        i = 1
        while i < len(x):
            y[i - 1] = sum(x[:i])
            i += 1
        y[len(x) - 1] = sum(x)
        return y


def run_CSMA_Top_A_simulation(arrival_rate):
    sim1 = Simulation(arrival_rate)
    a_arrivals = sim1.poisson_distributed_arrival_timings()
    c_arrivals = sim1.poisson_distributed_arrival_timings()
    print("A arrivals :", a_arrivals)
    sim1.tx_a = Transmitter(a_arrivals)  #
    print("C arrivals:", c_arrivals)
    sim1.tx_c = Transmitter(c_arrivals)  #

    clock = 0
    DIFS = 2
    SIFS = 2
    ACK = 2
    b_a = np.random.randint(0, 4)
    print(b_a)
    b_c = np.random.randint(0, 4)
    print(b_c)
    frame_size = 100
    success_a = 0
    success_c = 0
    collision_a = 0
    collision_c = 0
    collision = 0
    i = 0
    retry = 0
    print("Start:")
    run = True
    while run:
        print("Clock:", clock)
        if clock > 1000000:
            run = False
        if success_a == 0 and success_c == 0 and retry == 0:
            x_a = sim1.tx_a.arrivals[0]
            x_c = sim1.tx_c.arrivals[0]
            if (x_a > x_c):
                clock = x_c
            else:
                clock = x_a
        # if a has nothing to transmit c transmits
        if not success_a < len(sim1.tx_a.arrivals) and success_c < len(sim1.tx_c.arrivals):
            print("C arrived @", clock, " and contends with no one so it has a success @",
                  clock + DIFS + b_c)
            clock = clock + DIFS + b_c + frame_size + SIFS + ACK  # clock guaranteed to proceed to the end of transmission and wait for next arrival
            print("C's frame is finished transmitting @", clock)
            success_c += 1  # success for c
            sim1.tx_c.contention_window_size = 4
            if success_c < len(sim1.tx_c.arrivals):
                x_c = sim1.tx_c.arrivals[success_c]  # get the next arrival for comparison if there is one
        # if c has nothing to transmit a transmits
        elif success_a < len(sim1.tx_a.arrivals) and not success_c < len(sim1.tx_c.arrivals):
            print("A arrived @", clock, "and contends with no one so it has a success @",
                  clock + DIFS + b_a)
            clock = clock + DIFS + b_a + frame_size + SIFS + ACK
            print("A's frame is finished transmitting @", clock)
            success_a += 1
            sim1.tx_a.contention_window_size = 4
            if success_a < len(sim1.tx_a.arrivals):
                x_a = sim1.tx_a.arrivals[success_a]  # get the next arrival for comparison if there is one
        else:
            print("Contention between x_a:", x_a, "and x_c:", x_c)
            if clock <= x_c:
                if clock + b_a == x_c + b_c:  # collision
                    collision_a += 1
                    collision += 1
                    retry += 1  # how many times has this loop been entered
                    # expand collision windows
                    clock = clock + DIFS + b_a  # clock goes to the collision, and a new DIFS cycle shall start RTS collision
                    # increase contention window
                    sim1.tx_a.contention_window_size = 2 ** retry * 4
                    sim1.tx_c.contention_window_size = 2 ** retry * 4
                    # choose new backoffs
                    b_a = np.random.randint(0, sim1.tx_a.contention_window_size)  # new backoff
                    b_c = np.random.randint(0, sim1.tx_c.contention_window_size)
                    # these will seemingly arrive at the end of the collision
                    x_a = clock
                    x_c = clock
                    print("CRP")
                elif clock + b_a < x_c + b_c:  # a gets its cts off before c
                    success_a += 1
                    sim1.tx_a.contention_window_size = 4  # reset cw
                    retry = 0
                    print("A arrived @", clock, "and A transmitted @", clock + DIFS + b_a)
                    # advance clock
                    clock = clock + DIFS + b_a + frame_size + SIFS + ACK  # when c is done with its transmission the clock will have advanced to the end of that transmission
                    print("A's frame finished @", clock)
                    b_a = np.random.randint(0, sim1.tx_a.contention_window_size)  # new backoff
                    # how does b_c change
                    b_c = abs(b_c - b_a)
                    if success_a < len(sim1.tx_a.arrivals):
                        x_a = sim1.tx_a.arrivals[success_a]  # get the next arrival for comparison if there is one
                    if x_a < clock:
                        x_a = clock
                    if x_c < clock:
                        x_c = clock
                    clock = min(x_a, x_c)
                elif clock + b_a > x_c + b_c:  # c gets its cts off before a
                    success_c += 1
                    sim1.tx_c.contention_window_size = 4  # reset cw
                    retry = 0
                    print("C arrived @", clock, "and C transmitted @", clock + DIFS + b_c)
                    # advance clock
                    clock = clock + DIFS + b_c + frame_size + SIFS + ACK  # when c is done with its transmission the clock will have advanced to the end of that transmission
                    print("C's frame finished @", clock)
                    b_c = np.random.randint(0, sim1.tx_c.contention_window_size)  # new backoff
                    b_a = abs(b_a - b_c)
                    if success_c < len(sim1.tx_c.arrivals):
                        x_c = sim1.tx_c.arrivals[success_c]  # get the next arrival for comparison if there is one
                    if x_a < clock:
                        x_a = clock
                    if x_c < clock:
                        x_c = clock
                    clock = min(x_a, x_c)
            elif clock < x_a:
                if clock + b_c == x_a + b_a:  # collision
                    collision_c += 1
                    collision += 1
                    retry += 1  # how many times has this loop been entered
                    # expand collision windows
                    clock = clock + DIFS + b_c + frame_size + SIFS + ACK  # clock goes to the collision, and a new DIFS cycle shall start RTS collision
                    # increase contention window
                    sim1.tx_a.contention_window_size = 2 ** retry * 4
                    sim1.tx_c.contention_window_size = 2 ** retry * 4
                    # choose new backoffs
                    b_a = np.random.randint(0, sim1.tx_a.contention_window_size)  # new contenton window size
                    b_c = np.random.randint(0, sim1.tx_c.contention_window_size)
                    # these will seemingly arrive at the end of the collision
                    x_a = clock
                    x_c = clock
                    print("CRP")
                elif clock + b_c < x_a + b_a:  # c gets its cts off before a
                    success_c += 1
                    sim1.tx_c.contention_window_size = 4  # reset cw
                    retry = 0
                    print("C arrived @", clock, "and C transmitted @", clock + DIFS + b_c)
                    # advance clock
                    clock = clock + DIFS + b_c + frame_size + SIFS + ACK  # when c is done with its transmission the clock will have advanced to the end of that transmission
                    print("C's frame finished @", clock)
                    b_c = np.random.randint(0, sim1.tx_c.contention_window_size)  # new backoff
                    b_a = abs(b_a - b_c)
                    if success_c < len(sim1.tx_c.arrivals):
                        x_c = sim1.tx_c.arrivals[success_c]  # get the next arrival for comparison if there is one
                    # do we change the clock
                    if x_a < clock:
                        x_a = clock
                    if x_c < clock:
                        x_c = clock
                    clock = min(x_a, x_c)
                elif clock + b_c > x_a + b_a:  # a gets its cts off before c
                    success_a += 1
                    sim1.tx_a.contention_window_size = 4  # reset cw
                    retry = 0
                    print("A arrived @", clock, "and A transmitted @", clock + DIFS + b_a)
                    # advance clock
                    clock = clock + DIFS + b_c + frame_size + SIFS + ACK  # when c is done with its transmission the clock will have advanced to the end of that transmission
                    print("A's frame finished @", clock)
                    b_a = np.random.randint(0, sim1.tx_a.contention_window_size)  # new backoff
                    b_c = abs(b_a - b_a)
                    if success_a < len(sim1.tx_a.arrivals):
                        x_a = sim1.tx_a.arrivals[success_a]  # get the next arrival for comparison if there is one
                    if x_a < clock:
                        x_a = clock
                    if x_c < clock:
                        x_c = clock
                    clock = min(x_a, x_c)
    print("End:")
    print("Amount of Successful transmissions for TX A for hidden terminal problem:", success_a)
    print("Amount of collisions for TX A for hidden terminal problem:", collision_a)
    print("Amount of Successful transmissions for TX C for hidden terminal problem:", success_c)
    print("Amount of collisions for TX C for hidden terminal problem:", collision_c)
    print("Amount of Collisions:", collision)
    return success_a, success_c, collision_a, collision_c, collision

    # run = True
    # while run:
    #     print("Clock:", clock)
    #     if clock > 1000000:
    #         run = False
    #     if success_for_a == 0 and success_for_c == 0:
    #         x_a = sim1.tx_a.arrivals[0]
    #         x_c = sim1.tx_c.arrivals[0]
    #         if (x_a > x_c):
    #             clock = x_c
    #         else:
    #             clock = x_a
    #         i += 1
    #     print("Contention between x_a:", x_a, "and x_c:", x_c)
    #     if not success_for_a < len(sim1.tx_a.arrivals) and success_for_c < len(sim1.tx_c.arrivals):
    #         print("c arrived @:", x_c,"tramsmitted in slot", DIFS + b_c + clock)
    #         clock = clock + DIFS + b_c + frame_size + SIFS + ACK
    #         success_for_c += 1
    #         sim1.tx_c.contention_window_size = 4
    #         if success_for_c < len(sim1.tx_c.arrivals):
    #             x_c = sim1.tx_c.arrivals[success_for_c]  # get the next arrival for comparison
    #         else:
    #             x_c = x_c
    #     elif success_for_a < len(sim1.tx_a.arrivals) and not success_for_c < len(sim1.tx_c.arrivals):
    #         print("a arrived @:", x_a,"tramsmitted in slot", DIFS + b_a + clock)
    #         clock = clock + DIFS + b_a + frame_size + SIFS + ACK
    #         success_for_a += 1
    #         sim1.tx_a.contention_window_size = 4
    #         if success_for_a < len(sim1.tx_a.arrivals):
    #             x_a = sim1.tx_a.arrivals[success_for_a]  # get the next arrival for comparison
    #         else:
    #             x_a = x_a
    #     else:
    #
    #         if clock < x_a and clock < x_c:  # if there are two future events
    #             if x_a + b_a == x_c + b_c:  # collision
    #                 collision += 1
    #                 retry += 1
    #                 clock = x_a + b_a + frame_size + SIFS + ACK
    #                 sim1.tx_a.contention_window_size = 2 ** retry * 4
    #                 sim1.tx_c.contention_window_size = 2 ** retry * 4
    #                 b_a = np.random.randint(0, sim1.tx_a.contention_window_size)
    #                 b_c = np.random.randint(0, sim1.tx_c.contention_window_size)
    #                 print("collision")
    #             elif x_a + b_a < x_c + b_c:  # and if a gets to its back off first, a transmits first
    #                 retry = 0
    #                 print("a arrived @:", x_a, " transmitted in slot", x_a + b_a + DIFS + 1)
    #                 clock = x_a + b_a + 1 + DIFS + SIFS + ACK + frame_size # move event clock to the new difs period
    #                 success_for_a += 1 # a was successful
    #
    #                 sim1.tx_a.contention_window_size = 4
    #                 if x_c >= x_a + b_a: # countdown of backoff value for c has not even started before getting frozen
    #                     # freeze the backoff
    #                     pass
    #                 else:
    #                     b_c = x_a + b_a - x_c  # this should be the new backoff (freezing the backoff)
    #                 # generate new backoff for a
    #                 b_a = np.random.randint(0,4)
    #                 if success_for_a < len(sim1.tx_a.arrivals):
    #                     x_a = sim1.tx_a.arrivals[success_for_a]  # get the next arrival for comparison
    #                 else:
    #                     x_a = x_a
    #                 #where do we advance clock next
    #                 if(x_a < x_c):
    #                     clock = x_a
    #                 else:
    #                     clock = x_c
    #             else:  # and if c gets to its back off first, c transmits first
    #                 retry = 0
    #                 print("c arrived @:", x_c, " transmitted in slot", x_c + b_c + DIFS + 1)
    #                 clock = clock + b_c + DIFS + SIFS + ACK + frame_size
    #                 success_for_c += 1
    #                 sim1.tx_c.contention_window_size = 4
    #                 if x_c >= x_a + b_a: # countdown of backoff value for a has not even started before getting frozen
    #                     # Keep the same backoff
    #                     pass
    #                 else:
    #                     b_a = abs(x_c + b_c - x_a)  # calculating frozen backoff
    #                 # generate new backoff for c
    #                 b_c = np.random.randint(0, 4)
    #                 if success_for_c < len(sim1.tx_c.arrivals):
    #                     x_c = sim1.tx_c.arrivals[success_for_c]  # get the next arrival for comparison
    #                 else:
    #                     x_c = x_c
    #                 # where do we advance clock next
    #                 if (x_a < x_c):
    #                     clock = x_a
    #                 else:
    #                     clock = x_c
    #             # (x_a < clock and clock < x_c) or (x_c < clock and clock < x_a)
    #         elif (clock <= x_c) or (clock <= x_a):  # one event in the past one in the future
    #             if clock < x_c:
    #                 if clock + b_a == x_c + b_c:  # collision resolution
    #                     collision += 1
    #                     retry += 1
    #                     sim1.tx_a.contention_window_size = 2 ** retry * 4
    #                     sim1.tx_c.contention_window_size = 2 ** retry * 4
    #                     clock = clock + b_a + frame_size + SIFS + ACK
    #                     b_a = np.random.randint(0, sim1.tx_a.contention_window_size)
    #                     b_c = np.random.randint(0, sim1.tx_c.contention_window_size)
    #                     print("CRP")
    #                 elif clock + b_a < x_c + b_c:  # a transmits first
    #                     retry = 0
    #                     print("a arrived @:", x_a, " transmitted in slot", clock + b_a + DIFS + 1)
    #                     clock = clock + b_a + 1 + DIFS + SIFS + ACK + frame_size
    #                     success_for_a += 1
    #                     sim1.tx_a.contention_window_size = 4
    #                     if x_c + DIFS >= x_a + b_a:
    #                         # Keep the same backoff
    #                         pass
    #                     else:
    #                         b_c = x_a + b_a - x_c  # this should be the new backoff
    #                     # generate new backoff for a
    #                     b_a = np.random.randint(0, 4)
    #                     if(success_for_a < len(sim1.tx_a.arrivals)):
    #                         x_a = sim1.tx_a.arrivals[success_for_a]  # get the next arrival for comparison
    #                     else:
    #                         x_a = x_a
    #                     # where do we advance clock next
    #                     if (x_a < x_c):
    #                         clock = x_a
    #                     else:
    #                         clock = x_c
    #                 else:
    #                     retry = 0
    #                     print("c arrived @:", x_c, " transmitted in slot", x_c + b_c + DIFS + 1)
    #                     clock = clock + b_c + 1 + DIFS + SIFS + ACK + frame_size
    #                     success_for_c += 1
    #                     sim1.tx_c.contention_window_size = 4
    #                     if x_a >= x_c + b_c:
    #                         # Keep the same backoff
    #                         pass
    #                     else:
    #                         b_a = abs(x_c + b_c - x_a)  # this should be the new backoff
    #                     # generate new backoff for c
    #                     b_c = np.random.randint(0, 4)
    #                     if success_for_c < len(sim1.tx_c.arrivals):
    #                         x_c = sim1.tx_c.arrivals[success_for_c] # get the next arrival for comparison
    #                     else:
    #                         x_c = x_c
    #
    #                     # where do we advance clock next
    #                     if (x_a < x_c):
    #                         clock = x_a
    #                     else:
    #                         clock = x_c
    #             elif clock < x_a:
    #                 if clock + b_c == x_a + b_a:  # collision resolution
    #                     collision += 1
    #                     retry += 1
    #                     sim1.tx_a.contention_window_size = 2 ** retry * 4
    #                     sim1.tx_c.contention_window_size = 2 ** retry * 4
    #                     clock = clock + b_a + frame_size + SIFS + ACK
    #                     b_a = np.random.randint(0, sim1.tx_a.contention_window_size)
    #                     b_c = np.random.randint(0, sim1.tx_c.contention_window_size)
    #                     print("CRP")
    #                 elif x_c + b_c < x_a + b_a:  # a transmits first
    #                     retry = 0
    #                     print("c arrived @:", x_c, " transmitted in slot", clock + b_c + DIFS + 1)
    #                     clock = clock + b_c + 1 + DIFS + SIFS + ACK + frame_size
    #                     success_for_c += 1
    #                     sim1.tx_c.contention_window_size = 4
    #                     if x_a + DIFS >= x_c + b_c:
    #                         # Keep the same backoff
    #                         pass
    #                     else:
    #                         b_a = abs(x_c + b_c - x_a)  # this should be the new backoff
    #                     # generate new backoff for c
    #                     b_c = np.random.randint(0, 4)
    #                     if success_for_c < len(sim1.tx_c.arrivals):
    #                         x_c = sim1.tx_c.arrivals[success_for_c]  # get the next arrival for comparison
    #                     else:
    #                         x_c = x_c
    #                         # where do we advance clock next
    #                     if (x_a < x_c):
    #                         clock = x_a
    #                     else:
    #                         clock = x_c
    #                 else:
    #                     retry = 0
    #                     print("a arrived @:", x_a, " transmitted in slot", x_a + b_a + DIFS + 1)
    #                     clock = clock + b_a + 1 + DIFS + SIFS + ACK + frame_size
    #                     success_for_a += 1
    #                     sim1.tx_a.contention_window_size = 4
    #                     if x_c >= x_a + b_a:
    #                         # Keep the same backoff
    #                         pass
    #                     else:
    #                         b_c = abs(x_a + b_a - x_c)  # this should be the new backoff
    #                     # generate new backoff for a
    #                     b_a = np.random.randint(0, 4)
    #                     if success_for_a < len(sim1.tx_a.arrivals):
    #                         x_a = sim1.tx_a.arrivals[success_for_a]  # get the next arrival for comparison
    #                     else:
    #                         x_a = x_a
    #                         # where do we advance clock next
    #                     if (x_a < x_c):
    #                         clock = x_a
    #                     else:
    #                         clock = x_c
    #             else:
    #                 if b_c == b_a:  # collision resolution
    #                     collision += 1
    #                     retry += 1
    #                     sim1.tx_a.contention_window_size = 2 ** retry * 4
    #                     sim1.tx_c.contention_window_size = 2 ** retry * 4
    #                     clock = clock + b_a + frame_size + SIFS + ACK
    #                     b_a = np.random.randint(0, sim1.tx_a.contention_window_size)
    #                     b_c = np.random.randint(0, sim1.tx_c.contention_window_size)
    #                     print("CRP")
    #                 elif b_c < b_a:  # a transmits first
    #                     retry = 0
    #                     print("c arrived @:", x_c, " transmitted in slot", clock + b_c + DIFS + 1)
    #                     clock = clock + b_c + 1 + DIFS + SIFS + ACK + frame_size
    #                     success_for_c += 1
    #                     sim1.tx_c.contention_window_size = 4
    #                     if x_a + DIFS >= x_c + b_c:
    #                         # Keep the same backoff
    #                         pass
    #                     else:
    #                         b_a = abs(x_c + b_c - x_a)  # this should be the new backoff
    #                     # generate new backoff for c
    #                     b_c = np.random.randint(0, 4)
    #                     if success_for_c < len(sim1.tx_c.arrivals):
    #                         x_c = sim1.tx_c.arrivals[success_for_c]  # get the next arrival for comparison
    #                     else:
    #                         x_c = x_c
    #                         # where do we advance clock next
    #                     if (x_a < x_c):
    #                         clock = x_a
    #                     else:
    #                         clock = x_c
    #                 else:
    #                     retry = 0
    #                     print("a arrived @:", x_a, " transmitted in slot", x_a + b_a + DIFS + 1)
    #                     clock = clock + b_a + 1 + DIFS + SIFS + ACK + frame_size
    #                     success_for_a += 1
    #                     sim1.tx_a.contention_window_size = 4
    #                     if x_c >= x_a + b_a:
    #                         # Keep the same backoff
    #                         pass
    #                     else:
    #                         b_c = abs(x_a + b_a - x_c)  # this should be the new backoff
    #                     # generate new backoff for a
    #                     b_a = np.random.randint(0, 4)
    #                     if success_for_a < len(sim1.tx_a.arrivals):
    #                         x_a = sim1.tx_a.arrivals[success_for_a]  # get the next arrival for comparison
    #                     else:
    #                         x_a = x_a
    #                         # where do we advance clock next
    #                     if (x_a < x_c):
    #                         clock = x_a
    #                     else:
    #                         clock = x_c
    #         elif clock > x_a and clock > x_c:  # both are in the past
    #             if b_a == b_c:  # collision
    #                 collision += 1
    #                 retry += 1
    #                 sim1.tx_a.contention_window_size = 2 ** retry * 4
    #                 sim1.tx_c.contention_window_size = 2 ** retry * 4
    #                 clock = clock + b_a + frame_size + SIFS + ACK
    #                 b_a = np.random.randint(0, sim1.tx_a.contention_window_size) # new contenton window size
    #                 b_c = np.random.randint(0, sim1.tx_c.contention_window_size)
    #                 print("crp")
    #             elif b_a < b_c:  # a transmits
    #                 retry = 0
    #                 print("a arrived @:", x_a, " transmitted in slot", clock + b_a + DIFS + 1)
    #                 success_for_a += 1
    #                 sim1.tx_a.contention_window_size = 4
    #                 if x_c >= x_a + b_a:
    #                     # Keep the same backoff
    #                     pass
    #                 else:
    #                     b_c = abs(x_a + b_a - x_c)  # this should be the new backoff
    #
    #                 if success_for_a < len(sim1.tx_a.arrivals):
    #                     x_a = sim1.tx_a.arrivals[success_for_a]  # get the next arrival for comparison
    #                 else:
    #                     x_a = x_a
    #                 clock = clock + b_a + DIFS + 1 + DIFS + SIFS + frame_size
    #                 # generate new backoff for a
    #                 b_a = np.random.randint(0, 4)
    #             else:  # c transmits
    #                 retry = 0
    #                 print("c arrived @:", x_c, " transmitted in slot", clock + b_c + DIFS + 1)
    #                 success_for_c += 1
    #                 sim1.tx_c.contention_window_size = 4
    #                 if success_for_a < len(sim1.tx_a.arrivals):
    #                     x_c = sim1.tx_c.arrivals[success_for_a]  # get the next arrival for comparison
    #                 else:
    #                     x_a = x_a
    #                 clock = clock + b_c + DIFS + 1 + DIFS + SIFS + frame_size
    #                 # generate new backoff for c
    #                 b_c = np.random.randint(0, 4)
    # print("End:")
    # print("Amount of Successful transmissions for TX A for hidden terminal problem:", success_for_a)
    # print("Amount of Successful transmissions for TX C for hidden terminal problem:", success_for_c)
    # print("Amount of Collisions:", collision)
    # return success_for_a, success_for_c, collision


def run_CSMA_Top_B_simulation(arrival_rate):
    sim2 = Simulation(arrival_rate)
    sim2.tx_a = Transmitter(sim2.poisson_distributed_arrival_timings())
    sim2.tx_c = Transmitter(sim2.poisson_distributed_arrival_timings())

    clock = 0
    DIFS = 2
    SIFS = 1
    ACK = 2
    b_a = np.random.randint(0, 4)
    b_c = np.random.randint(0, 4)
    frame_size = 100
    success_a = 0
    success_c = 0
    collision_a = 0
    collision_c = 0
    collision = 0
    retry = 0
    print("Start:")
    run = True
    while run:
        print("Clock:", clock)
        if clock > 1000000:
            run = False
        if success_a == 0 and success_c == 0 and retry == 0:
            x_a = sim2.tx_a.arrivals[0]
            x_c = sim2.tx_c.arrivals[0]
            if (x_a > x_c):
                clock = x_c
            else:
                clock = x_a
        # if a has nothing to transmit c transmits
        if not success_a < len(sim2.tx_a.arrivals) and success_c < len(sim2.tx_c.arrivals):
            print("C arrived @", clock, " and contends with no one so it has a success @",
                  clock + DIFS + b_c)
            clock = clock + DIFS + b_c + frame_size + SIFS + ACK  # clock guaranteed to proceed to the end of transmission and wait for next arrival
            print("C's frame is finished transmitting @", clock)
            success_c += 1  # success for c
            sim2.tx_c.contention_window_size = 4
            if success_c < len(sim2.tx_c.arrivals):
                x_c = sim2.tx_c.arrivals[success_c]  # get the next arrival for comparison if there is one
        # if c has nothing to transmit a transmits
        elif success_a < len(sim2.tx_a.arrivals) and not success_c < len(sim2.tx_c.arrivals):
            print("A arrived @", clock, "and contends with no one so it has a success @",
                  clock + DIFS + b_a)
            clock = clock + DIFS + b_a + frame_size + SIFS + ACK
            print("A's frame is finished transmitting @", clock)
            success_a += 1
            sim2.tx_a.contention_window_size = 4
            if success_a < len(sim2.tx_a.arrivals):
                x_a = sim2.tx_a.arrivals[success_a]  # get the next arrival for comparison if there is one
        else:
            print("Contention between x_a:", x_a, "and x_c:", x_c)
            if clock <= x_c:
                if clock + b_a + 102 < x_c + b_c:  # collision
                    collision_a += 1
                    collision += 1
                    retry += 1  # how many times has this loop been entered
                    # expand collision windows
                    clock = clock + DIFS + b_a  # clock goes to the collision, and a new DIFS cycle shall start RTS collision
                    # increase contention window
                    sim2.tx_a.contention_window_size = 2 ** retry * 4
                    sim2.tx_c.contention_window_size = 2 ** retry * 4
                    # choose new backoffs
                    b_a = np.random.randint(0, sim2.tx_a.contention_window_size)  # new backoff
                    b_c = np.random.randint(0, sim2.tx_c.contention_window_size)
                    # these will seemingly arrive at the end of the collision
                    x_a = clock
                    x_c = clock
                    print("CRP")
                elif clock + b_a + 102 < x_c + b_c:  # a gets its cts off before c
                    success_a += 1
                    sim2.tx_a.contention_window_size = 4  # reset cw
                    retry = 0
                    print("A arrived @", clock, "and A transmitted @", clock + DIFS + b_a)
                    # advance clock
                    clock = clock + DIFS + b_a + frame_size + SIFS + ACK  # when c is done with its transmission the clock will have advanced to the end of that transmission
                    print("A's frame finished @", clock)
                    b_a = np.random.randint(0, sim2.tx_a.contention_window_size)  # new backoff
                    # how does b_c change
                    b_c = abs(b_c - b_a)
                    if success_a < len(sim2.tx_a.arrivals):
                        x_a = sim2.tx_a.arrivals[success_a]  # get the next arrival for comparison if there is one
                    if x_a < clock:
                        x_a = clock
                    if x_c < clock:
                        x_c = clock
                    clock = min(x_a, x_c)
                elif clock + b_a + 102 > x_c + b_c:  # c gets its cts off before a
                    success_c += 1
                    sim2.tx_c.contention_window_size = 4  # reset cw
                    retry = 0
                    print("C arrived @", clock, "and C transmitted @", clock + DIFS + b_c)
                    # advance clock
                    clock = clock + DIFS + b_c + frame_size + SIFS + ACK  # when c is done with its transmission the clock will have advanced to the end of that transmission
                    print("C's frame finished @", clock)
                    b_c = np.random.randint(0, sim2.tx_c.contention_window_size)  # new backoff
                    b_a = abs(b_a - b_c)
                    if success_c < len(sim2.tx_c.arrivals):
                        x_c = sim2.tx_c.arrivals[success_c]  # get the next arrival for comparison if there is one
                    if x_a < clock:
                        x_a = clock
                    if x_c < clock:
                        x_c = clock
                    clock = min(x_a, x_c)
            elif clock < x_a:
                if clock + b_c + 102 < x_a + b_a:  # collision
                    collision_c += 1
                    collision += 1
                    retry += 1  # how many times has this loop been entered
                    # expand collision windows
                    clock = clock + DIFS + b_c + frame_size + SIFS + ACK  # clock goes to the collision, and a new DIFS cycle shall start RTS collision
                    # increase contention window
                    sim2.tx_a.contention_window_size = 2 ** retry * 4
                    sim2.tx_c.contention_window_size = 2 ** retry * 4
                    # choose new backoffs
                    b_a = np.random.randint(0, sim2.tx_a.contention_window_size)  # new contenton window size
                    b_c = np.random.randint(0, sim2.tx_c.contention_window_size)
                    # these will seemingly arrive at the end of the collision
                    x_a = clock
                    x_c = clock
                    print("CRP")
                elif clock + b_c + 102 < x_a + b_a:  # c gets its cts off before a
                    success_c += 1
                    sim2.tx_c.contention_window_size = 4  # reset cw
                    retry = 0
                    print("C arrived @", clock, "and C transmitted @", clock + DIFS + b_c)
                    # advance clock
                    clock = clock + DIFS + b_c + frame_size + SIFS + ACK  # when c is done with its transmission the clock will have advanced to the end of that transmission
                    print("C's frame finished @", clock)
                    b_c = np.random.randint(0, sim2.tx_c.contention_window_size)  # new backoff
                    b_a = abs(b_a - b_c)
                    if success_c < len(sim2.tx_c.arrivals):
                        x_c = sim2.tx_c.arrivals[success_c]  # get the next arrival for comparison if there is one
                    # do we change the clock
                    if x_a < clock:
                        x_a = clock
                    if x_c < clock:
                        x_c = clock
                    clock = min(x_a, x_c)
                elif clock + b_c + 102 > x_a + b_a:  # a gets its cts off before c
                    success_a += 1
                    sim2.tx_a.contention_window_size = 4  # reset cw
                    retry = 0
                    print("A arrived @", clock, "and A transmitted @", clock + DIFS + b_a)
                    # advance clock
                    clock = clock + DIFS + b_c + frame_size + SIFS + ACK  # when c is done with its transmission the clock will have advanced to the end of that transmission
                    print("A's frame finished @", clock)
                    b_a = np.random.randint(0, sim2.tx_a.contention_window_size)  # new backoff
                    b_c = abs(b_a - b_a)
                    if success_a < len(sim2.tx_a.arrivals):
                        x_a = sim2.tx_a.arrivals[success_a]  # get the next arrival for comparison if there is one
                    if x_a < clock:
                        x_a = clock
                    if x_c < clock:
                        x_c = clock
                    clock = min(x_a, x_c)
    print("End:")
    print("Amount of Successful transmissions for TX A for hidden terminal problem:", success_a)
    print("Amount of collisions for TX C for hidden terminal problem:", collision_a)
    print("Amount of Successful transmissions for TX C for hidden terminal problem:", success_c)
    print("Amount of collisions for TX C for hidden terminal problem:", collision_c)
    print("Amount of Collisions:", collision)
    return success_a, success_c, collision_a, collision_c, collision


def run_VCS_Top_A_simulation(arrival_rate):
    sim3 = Simulation(arrival_rate)
    arrivals_a = sim3.poisson_distributed_arrival_timings()
    arrivals_c = sim3.poisson_distributed_arrival_timings()
    print(arrivals_a)
    print(arrivals_c)
    sim3.tx_a = Transmitter(arrivals_a)  # arrivals_a
    sim3.tx_c = Transmitter(arrivals_c)  # arrivals_c

    clock = 0
    success_a = 0
    success_c = 0
    collision_a = 0
    collision_c = 0
    collision = 0
    retry = 0

    b_a = np.random.randint(0, 4)
    b_c = np.random.randint(0, 4)

    CTS = 2
    RTS = 2
    DIFS = 2
    SIFS = 1
    ACK = 2
    frame_size = 100
    NAV_RTS = 2 * SIFS + CTS + frame_size + SIFS + ACK  # should only be using this for topology a
    NAV_CTS = SIFS + frame_size  # should only be using this for topology b
    print("Start:")
    run = True
    while run:
        print("Clock:", clock)
        if clock > 1000000:
            run = False
        if success_a == 0 and success_c == 0 and retry == 0:
            x_a = sim3.tx_a.arrivals[0]
            x_c = sim3.tx_c.arrivals[0]
            if (x_a > x_c):
                clock = x_c
            else:
                clock = x_a
        # if a has nothing to transmit c transmits
        if not success_a < len(sim3.tx_a.arrivals) and success_c < len(sim3.tx_c.arrivals):
            print("C arrived @", clock, " and contends with no one so it has a success @",
                  clock + DIFS + RTS + 2 * SIFS + CTS)
            clock = clock + DIFS + b_c + NAV_RTS  # clock guaranteed to proceed to the end of transmission and wait for next arrival
            print("C's frame is finished transmitting @", clock)
            success_c += 1  # success for c
            sim3.tx_c.contention_window_size = 4
            if success_c < len(sim3.tx_c.arrivals):
                x_c = sim3.tx_c.arrivals[success_c]  # get the next arrival for comparison if there is one
        # if c has nothing to transmit a transmits
        elif success_a < len(sim3.tx_a.arrivals) and not success_c < len(sim3.tx_c.arrivals):
            print("A arrived @", clock, "and contends with no one so it has a success @",
                  clock + DIFS + b_a + RTS + 2 * SIFS + CTS)
            clock = clock + DIFS + b_a + NAV_RTS
            print("A's frame is finished transmitting @", clock)
            success_a += 1
            sim3.tx_a.contention_window_size = 4
            if success_a < len(sim3.tx_a.arrivals):
                x_a = sim3.tx_a.arrivals[success_a]  # get the next arrival for comparison if there is one
        else:
            print("Contention between x_a:", x_a, "and x_c:", x_c)
            if clock <= x_c:
                if clock + b_a == x_c + b_c:  # collision
                    collision_a += 1
                    collision += 1
                    retry += 1  # how many times has this loop been entered
                    # expand collision windows
                    clock = clock + DIFS + b_a + RTS + SIFS + CTS  # clock goes to the collision, and a new DIFS cycle shall start RTS collision
                    # increase contention window
                    sim3.tx_a.contention_window_size = 2 ** retry * 4
                    sim3.tx_c.contention_window_size = 2 ** retry * 4
                    # choose new backoffs
                    b_a = np.random.randint(0, sim3.tx_a.contention_window_size)  # new backoff
                    b_c = np.random.randint(0, sim3.tx_c.contention_window_size)
                    # these will seemingly arrive at the end of the collision
                    x_a = clock
                    x_c = clock
                    print("CRP")
                elif clock + b_a < x_c + b_c:  # a gets its cts off before c
                    success_a += 1
                    sim3.tx_a.contention_window_size = 4  # reset cw
                    retry = 0
                    print("A arrived @", clock, "and A transmitted @", clock + DIFS + b_a + RTS + 2 * SIFS + CTS)
                    # advance clock
                    clock = clock + DIFS + b_a + RTS + NAV_RTS  # when c is done with its transmission the clock will have advanced to the end of that transmission
                    print("A's frame finished @", clock)
                    b_a = np.random.randint(0, sim3.tx_a.contention_window_size)  # new backoff
                    # how does b_c change
                    b_c = abs(b_c - b_a)
                    if success_a < len(sim3.tx_a.arrivals):
                        x_a = sim3.tx_a.arrivals[success_a]  # get the next arrival for comparison if there is one
                    if x_a < clock:
                        x_a = clock
                    if x_c < clock:
                        x_c = clock
                    clock = min(x_a, x_c)
                elif clock + b_a > x_c + b_c:  # c gets its cts off before a
                    success_c += 1
                    sim3.tx_c.contention_window_size = 4  # reset cw
                    retry = 0
                    print("C arrived @", clock, "and C transmitted @", clock + DIFS + b_c + RTS + 2 * SIFS + CTS)
                    # advance clock
                    clock = clock + DIFS + b_c + RTS + NAV_RTS  # when c is done with its transmission the clock will have advanced to the end of that transmission
                    print("C's frame finished @", clock)
                    b_c = np.random.randint(0, sim3.tx_c.contention_window_size)  # new backoff
                    b_a = abs(b_a - b_c)
                    if success_c < len(sim3.tx_c.arrivals):
                        x_c = sim3.tx_c.arrivals[success_c]  # get the next arrival for comparison if there is one
                    if x_a < clock:
                        x_a = clock
                    if x_c < clock:
                        x_c = clock
                    clock = min(x_a, x_c)
            elif clock < x_a:
                if clock + b_c == x_a + b_a:  # collision
                    collision_c += 1
                    collision += 1
                    retry += 1  # how many times has this loop been entered
                    # expand collision windows
                    clock = clock + DIFS + b_c + RTS + SIFS + CTS  # clock goes to the collision, and a new DIFS cycle shall start RTS collision
                    # increase contention window
                    sim3.tx_a.contention_window_size = 2 ** retry * 4
                    sim3.tx_c.contention_window_size = 2 ** retry * 4
                    # choose new backoffs
                    b_a = np.random.randint(0, sim3.tx_a.contention_window_size)  # new contenton window size
                    b_c = np.random.randint(0, sim3.tx_c.contention_window_size)
                    # these will seemingly arrive at the end of the collision
                    x_a = clock
                    x_c = clock
                    print("CRP")
                elif clock + b_c < x_a + b_a:  # c gets its cts off before a
                    success_c += 1
                    sim3.tx_c.contention_window_size = 4  # reset cw
                    retry = 0
                    print("C arrived @", clock, "and C transmitted @", clock + DIFS + b_c + RTS + 2 * SIFS + CTS)
                    # advance clock
                    clock = clock + DIFS + b_c + RTS + NAV_RTS  # when c is done with its transmission the clock will have advanced to the end of that transmission
                    print("C's frame finished @", clock)
                    b_c = np.random.randint(0, sim3.tx_c.contention_window_size)  # new backoff
                    b_a = abs(b_a - b_c)
                    if success_c < len(sim3.tx_c.arrivals):
                        x_c = sim3.tx_c.arrivals[success_c]  # get the next arrival for comparison if there is one
                    # do we change the clock
                    if x_a < clock:
                        x_a = clock
                    if x_c < clock:
                        x_c = clock
                    clock = min(x_a, x_c)
                elif clock + b_c > x_a + b_a:  # a gets its cts off before c
                    success_a += 1
                    sim3.tx_a.contention_window_size = 4  # reset cw
                    retry = 0
                    print("A arrived @", clock, "and A transmitted @", clock + DIFS + b_a + RTS + 2 * SIFS + CTS)
                    # advance clock
                    clock = clock + DIFS + b_c + RTS + NAV_RTS  # when c is done with its transmission the clock will have advanced to the end of that transmission
                    print("A's frame finished @", clock)
                    b_a = np.random.randint(0, sim3.tx_a.contention_window_size)  # new backoff
                    b_c = abs(b_a - b_a)
                    if success_a < len(sim3.tx_a.arrivals):
                        x_a = sim3.tx_a.arrivals[success_a]  # get the next arrival for comparison if there is one
                    if x_a < clock:
                        x_a = clock
                    if x_c < clock:
                        x_c = clock
                    clock = min(x_a, x_c)

    print("End:")
    print("Amount of Successful transmissions for TX A for hidden terminal problem:", success_a)
    print("Amount of collisions for TX C for hidden terminal problem:", collision_a)
    print("Amount of Successful transmissions for TX C for hidden terminal problem:", success_c)
    print("Amount of collisions for TX C for hidden terminal problem:", collision_c)
    print("Amount of Collisions:", collision)
    return success_a, success_c, collision_a, collision_c, collision


def run_VCS_Top_B_simulation(arrival_rate):
    sim4 = Simulation(arrival_rate)
    arrivals_a = sim4.poisson_distributed_arrival_timings()
    arrivals_c = sim4.poisson_distributed_arrival_timings()
    print(arrivals_a)
    print(arrivals_c)
    sim4.tx_a = Transmitter(arrivals_a)  # arrivals_a
    sim4.tx_c = Transmitter(arrivals_c)  # arrivals_c

    clock = 0
    success_a = 0
    success_c = 0
    collision_a = 0
    collision_c = 0
    collision = 0
    retry = 0

    b_a = np.random.randint(0, 4)
    b_c = np.random.randint(0, 4)

    CTS = 2
    RTS = 2
    DIFS = 2
    SIFS = 1
    ACK = 2

    frame_size = 100
    NAV_RTS = 2 * SIFS + CTS + frame_size + SIFS + ACK  # should only be using this for topology a
    NAV_CTS = SIFS + frame_size  # should only be using this for topology b
    print("Start:")
    run = True
    while run:
        print("Clock:", clock)
        if clock > 1000000:
            run = False
        if success_a == 0 and success_c == 0 and retry == 0:
            x_a = sim4.tx_a.arrivals[0]
            x_c = sim4.tx_c.arrivals[0]
            if (x_a > x_c):
                clock = x_c
            else:
                clock = x_a
        # if a has nothing to transmit c transmits
        if not success_a < len(sim4.tx_a.arrivals) and success_c < len(sim4.tx_c.arrivals):
            print("C arrived @", clock, " and contends with no one so it has a success @",
                  clock + DIFS + RTS + 2 * SIFS + CTS + b_c)
            clock = clock + DIFS + b_c + NAV_RTS  # clock guaranteed to proceed to the end of transmission and wait for next arrival
            print("C's frame is finished transmitting @", clock)
            success_c += 1  # success for c
            sim4.tx_c.contention_window_size = 4
            if success_c < len(sim4.tx_c.arrivals):
                x_c = sim4.tx_c.arrivals[success_c]  # get the next arrival for comparison if there is one
        # if c has nothing to transmit a transmits
        elif success_a < len(sim4.tx_a.arrivals) and not success_c < len(sim4.tx_c.arrivals):
            print("A arrived @", clock, "and contends with no one so it has a success @",
                  clock + DIFS + b_a + RTS + 2 * SIFS + CTS + b_a)
            clock = clock + DIFS + b_a + NAV_RTS
            print("A's frame is finished transmitting @", clock)
            success_a += 1
            sim4.tx_a.contention_window_size = 4
            if success_a < len(sim4.tx_a.arrivals):
                x_a = sim4.tx_a.arrivals[success_a]  # get the next arrival for comparison if there is one
        else:
            print("Contention between x_a:", x_a, "and x_c:", x_c)
            if clock <= x_c:
                if clock + b_a == x_c + b_c or clock + b_a + 1 == x_c + b_c or clock + b_a - 1 == x_c + b_c:  # collision
                    collision_a += 1
                    collision += 1
                    retry += 1  # how many times has this loop been entered
                    # expand collision windows
                    clock = clock + DIFS + b_a + RTS + SIFS + CTS  # clock goes to the collision, and a new DIFS cycle shall start RTS collision
                    # increase contention window
                    sim4.tx_a.contention_window_size = 2 ** retry * 4
                    sim4.tx_c.contention_window_size = 2 ** retry * 4
                    # choose new backoffs
                    b_a = np.random.randint(0, sim4.tx_a.contention_window_size)  # new backoff
                    b_c = np.random.randint(0, sim4.tx_c.contention_window_size)
                    # these will seemingly arrive at the end of the collision
                    x_a = clock
                    x_c = clock
                    print("CRP")
                elif clock + b_a < x_c + b_c:  # a gets its cts off before c
                    success_a += 1
                    sim4.tx_a.contention_window_size = 4  # reset cw
                    retry = 0
                    print("A arrived @", clock, "and A transmitted @", clock + DIFS + b_a + RTS + 2 * SIFS + CTS)
                    # advance clock
                    clock = clock + DIFS + b_a + RTS + NAV_RTS  # when c is done with its transmission the clock will have advanced to the end of that transmission
                    print("A's frame finished @", clock)
                    b_a = np.random.randint(0, sim4.tx_a.contention_window_size)  # new backoff
                    # how does b_c change
                    b_c = abs(b_c - b_a)
                    if success_a < len(sim4.tx_a.arrivals):
                        x_a = sim4.tx_a.arrivals[success_a]  # get the next arrival for comparison if there is one
                    if x_a < clock:
                        x_a = clock
                    if x_c < clock:
                        x_c = clock
                    clock = min(x_a, x_c)
                elif clock + b_a > x_c + b_c:  # c gets its cts off before a
                    success_c += 1
                    sim4.tx_c.contention_window_size = 4  # reset cw
                    retry = 0
                    print("C arrived @", clock, "and C transmitted @", clock + DIFS + b_c + RTS + 2 * SIFS + CTS)
                    # advance clock
                    clock = clock + DIFS + b_c + RTS + NAV_RTS  # when c is done with its transmission the clock will have advanced to the end of that transmission
                    print("C's frame finished @", clock)
                    b_c = np.random.randint(0, sim4.tx_c.contention_window_size)  # new backoff
                    b_a = abs(b_a - b_c)
                    if success_c < len(sim4.tx_c.arrivals):
                        x_c = sim4.tx_c.arrivals[success_c]  # get the next arrival for comparison if there is one
                    if x_a < clock:
                        x_a = clock
                    if x_c < clock:
                        x_c = clock
                    clock = min(x_a, x_c)
            elif clock < x_a:
                if clock + b_c == x_a + b_a or clock + b_c + 1 == x_a + b_a or clock + b_c - 1 == x_a + b_a:  # collision
                    collision_c += 1
                    collision += 1
                    retry += 1  # how many times has this loop been entered
                    # expand collision windows
                    clock = clock + DIFS + b_c + RTS + SIFS + CTS  # clock goes to the collision, and a new DIFS cycle shall start RTS collision
                    # increase contention window
                    sim4.tx_a.contention_window_size = 2 ** retry * 4
                    sim4.tx_c.contention_window_size = 2 ** retry * 4
                    # choose new backoffs
                    b_a = np.random.randint(0, sim4.tx_a.contention_window_size)  # new contenton window size
                    b_c = np.random.randint(0, sim4.tx_c.contention_window_size)
                    # these will seemingly arrive at the end of the collision
                    x_a = clock
                    x_c = clock
                    print("CRP")
                elif clock + b_c < x_a + b_a:  # c gets its cts off before a
                    success_c += 1
                    sim4.tx_c.contention_window_size = 4  # reset cw
                    retry = 0
                    print("C arrived @", clock, "and C transmitted @", clock + DIFS + b_c + RTS + 2 * SIFS + CTS)
                    # advance clock
                    clock = clock + DIFS + b_c + RTS + NAV_RTS  # when c is done with its transmission the clock will have advanced to the end of that transmission
                    print("C's frame finished @", clock)
                    b_c = np.random.randint(0, sim4.tx_c.contention_window_size)  # new backoff
                    b_a = abs(b_a - b_c)
                    if success_c < len(sim4.tx_c.arrivals):
                        x_c = sim4.tx_c.arrivals[success_c]  # get the next arrival for comparison if there is one
                    # do we change the clock
                    if x_a < clock:
                        x_a = clock
                    if x_c < clock:
                        x_c = clock
                    clock = min(x_a, x_c)
                elif clock + b_c > x_a + b_a:  # a gets its cts off before c
                    success_a += 1
                    sim4.tx_a.contention_window_size = 4  # reset cw
                    retry = 0
                    print("A arrived @", clock, "and A transmitted @", clock + DIFS + b_a + RTS + 2 * SIFS + CTS)
                    # advance clock
                    clock = clock + DIFS + b_c + RTS + NAV_RTS  # when c is done with its transmission the clock will have advanced to the end of that transmission
                    print("A's frame finished @", clock)
                    b_a = np.random.randint(0, sim4.tx_a.contention_window_size)  # new backoff
                    b_c = abs(b_a - b_a)
                    if success_a < len(sim4.tx_a.arrivals):
                        x_a = sim4.tx_a.arrivals[success_a]  # get the next arrival for comparison if there is one
                    if x_a < clock:
                        x_a = clock
                    if x_c < clock:
                        x_c = clock
                    clock = min(x_a, x_c)
    print("End:")
    print("Amount of Successful transmissions for TX A for hidden terminal problem:", success_a)
    print("Amount of collisions for TX C for hidden terminal problem:", collision_a)
    print("Amount of Successful transmissions for TX C for hidden terminal problem:", success_c)
    print("Amount of collisions for TX C for hidden terminal problem:", collision_c)
    print("Amount of Collisions:", collision)
    return success_a, success_c, collision_a, collision_c, collision


def main():
    # run_CSMA_Top_A_simulation(3)
    # # run_CSMA_Top_B_simulation(200)
    # # run_VCS_Top_B_simulation(1000)
    arrival_rates = [100, 200, 300, 500, 700, 1000]
    info1 = []
    info2 = []
    info3 = []
    info4 = []
    for _lambda in arrival_rates:
        info1.append(run_CSMA_Top_A_simulation(_lambda))
        info2.append(run_CSMA_Top_A_simulation(_lambda))
        info3.append(run_VCS_Top_A_simulation(_lambda))
        info4.append(run_VCS_Top_B_simulation(_lambda))
    print()
    i = 0
    print("CSMA Enabled: (Topology A)")
    for x in info1:
        print("For an arrival rate of", arrival_rates[i])
        print("We expect to see", x[0], "transmissions from A")
        print("and", x[2], "collisions from A")
        print("and", x[1], "transmissions from C")
        print("and", x[3], "collisions from C")
        print("and", x[4], "collisions on the medium")
        print()
        i += 1
    print()
    i = 0
    print("CSMA Enabled: (Topology B)")
    for x in info2:
        print("For an arrival rate of", arrival_rates[i])
        print("We expect to see", x[0], "transmissions from A")
        print("and", x[2], "collisions from A")
        print("and", x[1], "transmissions from C")
        print("and", x[3], "collisions from C")
        print("and", x[4], "collisions on the medium")
        print()
        i += 1
    print()
    print("VCS Enabled: (Topology A)")
    i = 0
    for x in info3:
        print("For an arrival rate of", arrival_rates[i])
        print("We expect to see", x[0], "transmissions from A")
        print("and", x[2], "collisions from A")
        print("and", x[1], "transmissions from C")
        print("and", x[3], "collisions from C")
        print("and", x[4], "collisions on the medium")
        print()
        i += 1
    print()
    print("VCS Enabled: (Topology B)")
    i = 0
    for x in info4:
        print("For an arrival rate of", arrival_rates[i])
        print("We expect to see", x[0], "transmissions from A")
        print("and", x[2], "collisions from A")
        print("and", x[1], "transmissions from C")
        print("and", x[3], "collisions from C")
        print("and", x[4], "collisions on the medium")
        print()
        i += 1
    print()


main()
