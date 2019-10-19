#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 09:03:14 2019

This module is part of OBIA4RTM.

@author: Lukas Graf, graflukas@web.de
"""
from scipy.stats import truncnorm
import numpy as np


def gaussian(minimum, maximum, num, mean, std):
    """
    draws a truncated gaussian distribution between min and max

    Parameters
    ----------
    minimum : float
        lower bound of the truncated Gaussian distribution
    maximum : float
        upper bound of the truncated Gaussian distribution
    num : Integer
        number of samples to be drawn
    mean : float
        centre of the truncated Gaussian distribution
    std : flaot
        standard deviation, controlls the width of the distribution betweem
        min and max

    Returns
    -------
    truncated : np.array
        Array with values drawn from the truncated Gaussian distribution
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

    Parameters
    ----------
    minimum : float
        lower bound of the uniform distribution
    maximum : float
        upper bound of the uniform distribution
    num : Integer
        number of samples to be drawn

    Returns
    -------
    uni : np.array
        Array with values drawn from the uniform distribution
    """
    uni = np.random.uniform(low=minimum, high=maximum, size=num)
    return uni
