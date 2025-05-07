"""A 1D diffusion Model."""
import numpy as np
import matplotlib.pyplot as plt


def calculate_stable_time_step(dx, diffusivity):
    """Calculate a stable time step for the model."""
    return 0.5*dx**2/diffusivity
    

def plot_profile(x,cake,color="r"):
    """ Display the cake profile."""
    plt.figure()
    plt.plot(x,cake,color)
    plt.xlabel("x")
    plt.ylabel("cake")
    plt.title("cake profile")



D=100
Lx=300


dx=0.5
x=np.arange(start=0, stop=Lx, step=dx)
nx=len(x)


C=np.zeros_like(x)
C_left=500
C_right=0
C[x<=Lx/2]=C_left
C[x>Lx/2]=C_right



plot_profile(x,C)


nt=5000
dt= calculate_stable_time_step(dx,D)


for t in range(0,nt):
    C[1:-1] += D *dt / dx ** 2 * (C[:-2]-2*C[1:-1]+C[2:])



plot_profile(x,C, color="b")






