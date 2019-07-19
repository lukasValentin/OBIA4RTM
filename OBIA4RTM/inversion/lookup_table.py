#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 06:52:00 2019

This module is part of OBIA4RTM.

Copyright (c) 2019 Lukas Graf

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

@author: Lukas Graf, graflukas@web.de
"""
import itertools
import numpy as np
from OBIA4RTM.inversion.distributions import gaussian, uniform


class lookup_table:
    """
    class for creating and storing biophysical parameters
    in a lookup table like structure
    """
    def __init__(self):
        """
        class constructor
        """
        self.const_params = None
        self.dist = None
        self.inv_params = None
        self.lut = None
        self.lut_shape = None
        self.lut_size = None
        self.maxima = None
        self.mean = None
        self.minima = None
        self.num = None
        self.std = None
        self.to_be_inv = None


    def generate_param_lut(self, params):
        """
        get the minima, maxima, number and distribution type of parameters
        to be inverted and prepares them for storing in a LUT accordingly
        
        Parameters
        ----------
        params : numpy array
            Array containing the ProSAIL parameters extracted from cfg file
        """
        try:
            self.minima, self.maxima, self.num, self.dist, self.mean, self.std = params[:,0], params[:,1], params[:,2], params[:,3], params[:,4], params[:,5]
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
        self.lut_shape = (params.shape[0], int(self.lut_size))
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
