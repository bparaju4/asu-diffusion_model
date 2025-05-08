""" Tests for the diffusion model module. """
import pytest
import math
import numpy as np

from diffusion import calculate_stable_time_step
from diffusion import step_like
def test_time_step_is_float():
    time_step=calculate_stable_time_step(1,1)
    assert isinstance(time_step,float)

def test_time_step_with_zero_spacing():
    dt=calculate_stable_time_step(dx=0.0,diffusivity=1)
    assert dt==pytest.approx(0.0)
    assert math.isclose(dt,0.0)

def test_step_like_length():
    z=step_like(np.arange(100))
    assert len(z)==100
    
