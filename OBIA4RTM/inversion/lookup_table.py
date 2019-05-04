#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 06:52:00 2019

@author: lukas
"""
import itertools
import numpy as np
from OBIA4RTM.inversion.distributions import gaussian, uniform


class lookup_table:
    """
    class for creating and storing biophysical parameters
    in a lookup table like structure
    """
    
    def __init__(self, path_to_config):
        """
        setup the class
        """
        
        try:
            self.params = np.genfromtxt(path_to_config, delimiter = "\t")
        except (Exception) as ex:
            print("Could not read config file!")
            print(ex)
    # end __init__
    
    def generate_param_lut(self):
        """
        get the minima, maxima, number and distribution type of parameters
        to be inverted and stores them into a LUT accordingly
        """
        try:
            self.minima, self.maxima, self.num, self.dist, self.mean, self.std = self.params[:,0], self.params[:,1], self.params[:,2], self.params[:,3], self.params[:,4], self.params[:,5]
        except (ValueError) as err:
            print("Unable to read from config file - Please check!")
            print(err)
        
        # which parameters should be inverted?
        self.to_be_inv = np.where(self.num > 1)
        self.inv_params = self.to_be_inv[0].size
        # and which not?
        self.const_params = np.where(self.num == 1)
        
        # how many combinations?
        self.lut_size = 1
        for ii in range(self.inv_params):
            self.lut_size *= self.num[self.to_be_inv[0][ii]]
        # convert to int to avoid type errors
        self.lut_size = int(self.lut_size)
        
        # open the lookup table for the parameters
        self.lut_shape = (self.params.shape[0], int(self.lut_size))
        self.lut = np.ndarray(shape=self.lut_shape, dtype=np.float32)
        
        # insert the const values first
        for ii in range(self.const_params[0].size):
            self.lut[self.const_params[0][ii],:] = self.minima[self.const_params[0][ii]]
        
        # secondly, create a temporarily storage for the parameters to be inverted
        # (list of arrays)
        params_temp = []
        # check how parameters to be inverted should be distributed
        for ii in range(self.inv_params):
            
            # truncated Gaussian
            if (self.dist[self.to_be_inv[0][ii]] == 1):
                vals = gaussian(self.minima[self.to_be_inv[0][ii]],
                                self.maxima[self.to_be_inv[0][ii]],
                                int(self.num[self.to_be_inv[0][ii]]),
                                self.mean[self.to_be_inv[0][ii]],
                                self.std[self.to_be_inv[0][ii]]
                                )
                
            # uniform distribution
            elif (self.dist[self.to_be_inv[0][ii]] == 2):
                vals = uniform(self.minima[self.to_be_inv[0][ii]],
                               self.maxima[self.to_be_inv[0][ii]],
                               int(self.num[self.to_be_inv[0][ii]])
                               )
            # endif
            
            # append vals to list
            params_temp.append(vals)
            
        # endfor
        
        # now, the parameters to be inverted can be written to the LUT
        # drawing all possible combinations
        # therefore, itertools.product can be used
        products = list(itertools.product(*params_temp))
        
        
        # insert the found combinations into the LUT
        for jj in range(self.lut_size):
            
            for ii in range(self.inv_params):
                
                self.lut[self.to_be_inv[0][ii],jj] = products[jj][ii]
                
            # endfor ii (inv_params)
            
        # endfor jj (lut_size)
    
    # end generate_param_lut
    
# end class