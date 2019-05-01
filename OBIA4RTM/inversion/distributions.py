#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 09:03:14 2019

@author: lukas
"""
from scipy.stats import truncnorm
import numpy as np


def gaussian(minimum, maximum, num, mean, std):
    """
    draws a truncated gaussian distribution between min and max
    """
    # calculate standardized boundaries for the truncated distribution
    lower, upper = (minimum - mean) / std, (maximum - mean) / std
    #rescale the distribution to mean and std
    tn = truncnorm(lower, upper, loc = mean, scale=std)
    truncated = tn.rvs(num)
    return truncated
# end gaussian


def uniform(minimum, maximum, num):
    """
    draws a uniform distribution between min and max
    """
    uni = np.random.uniform(low=minimum, high=maximum, size=num)
    return uni
# end uniform