"""A 1D diffusion Model."""
import numpy as np
import matplotlib.pyplot as plt
import sys


def calculate_stable_time_step(dx, diffusivity):
    """Calculate a stable time step for the model."""
    return 0.5*dx**2/diffusivity

def step_like(x,step_at=0):
    """Make a step function profile """
    y=np.empty_like(x,dtype=float)
    y[:step_at]=0.0
    y[step_at]=0.5
    y[step_at + 1 :]=1
    
    return y

def new_profile(x,form="step"):
    """ Make a new cake height profile, choosing a type."""
    match form:
        case "step":
            return step_like(x,step_at= len(x)//2)
        case _:
            raise ValueError (f"unknown profile type {form}")
        
    

def plot_profile(x,cake,color="r"):
    """ Display the cake profile."""
    plt.figure()
    plt.plot(x,cake,color)
    plt.xlabel("x")
    plt.ylabel("cake")
    plt.title("cake profile")


def run_diffusion_model():
    D=100
    Lx=300
    
    
    dx=0.5
    x=np.arange(start=0, stop=Lx, step=dx)
    nx=len(x)
    
    
    C= new_profile(x, form="step")
    
    
    
    plot_profile(x,C)
    
    
    nt=5000
    dt= calculate_stable_time_step(dx,D)
    
    
    for t in range(0,nt):
        C[1:-1] += D *dt / dx ** 2 * (C[:-2]-2*C[1:-1]+C[2:])
    
    
    
    plot_profile(x,C, color="b")
    
    return (C)

if __name__ == "__main__":
    cake=run_diffusion_model()
    np.savetxt(sys.stdout,cake,fmt="%.6f")







