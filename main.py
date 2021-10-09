import math
import numpy as np

def poisson_distributed_arrival_timings(arrival_rate):
    frames_needed = arrival_rate*10 # For instance, when λ = 200 frames per second, you will need approximately 2,000 frames to fill arrivals for 10 seconds. That means you need to draw 2,000 at random in (0, 1).
    uniform_number = np.random.uniform(0.0, 1.0, frames_needed)
    print(frames_needed)

    i = 0
    for u_num in uniform_number:
        x_num = -(1/arrival_rate)*np.log(1-u_num) # X = (−1/λ)ln(1 − U).
        uniform_number[i] = x_num*10**6 # create a new array with the altered values
        i+=1

    print(uniform_number)
    arrival_times = conversion(uniform_number)
    del(uniform_number)
    return arrival_times

def conversion(x):
    y = [0.0]*len(x)
    i = 1
    while(i < len(x)):
        y[i-1] = sum(x[:i])
        i += 1
    y[len(x)-1] = sum(x)
    return y

def main():
    arrival_times_station_a = poisson_distributed_arrival_timings(200)
    arrival_times_station_c = poisson_distributed_arrival_timings(200)

main()

