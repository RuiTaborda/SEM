# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 18:29:01 2018

@author: rui
"""
import math
from scipy.constants import g, pi

class Wave:
    H = 2.1
    T = 9.3
    dir = 0
    h = 500
    dir_bottom =[]
    rho = 1025
    
    breaker_index = 0.78
    
    H_stat = 'Hs'
    
    # breaker iteration error
    b_error = 0.01
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def k(self):
        
        # You, Z. J. (2008). A close approximation of wave dispersion relation for direct calculation of wavelength in any coastal water depth. Applied Ocean Research, 30(2), 113-119.
        
        k0 = (2 * pi)**2 / (self.T**2 * g)
        if self.h > pi / k0: # deep water conditions
            return k0
        else:
            kh = k0 * self.h
            x0 = math.sqrt(kh) * (1 + 1/6 * kh + 1/30 * kh**2)        
            k = x0 / self.h * ((k0 * self.h + (x0 / math.cosh(x0))**2) / (x0 * math.tanh(x0) + (x0 / math.cosh(x0))**2))        
            return k
        
    def Hs(self):
        if self.H_stat == 'Hs':
            return self.H
        elif self.H_stat == 'Hrms':
            return self.H * math.sqrt(2)
    
    def Hrms(self):
        if self.H_stat == 'Hs':
            return self.H / math.sqrt(2)
        elif self.H_stat == 'Hrms':
            return self.H 
 
    
    def L(self):
        return 2* pi / self.k()
    
    def c(self):
        return self.L() / self.T
    
    def E(self):
        return self.rho * g * self.Hrms() ** 2 / 8
    
    def n(self):
        return 0.5 + self.k() * self.h / math.sinh(2 * self.k() * self.h)
    
    def cg(self):
        return self.c() * self.n()
    
    def P(self):
        return self.E() * self.cg()
    
    def alpha(self):
        a = -(self.dir - self.dir_bottom)
        return (a + 180) % 360 - 180
    
    def set_dir_bottom(self, angle):
        self.dir_bottom = angle
    
    def shoal(self, h):
        
        # get atual parameters
        cg0 = self.cg()
        c0 = self.c()
        alpha0 = self.alpha()
        
        if abs(alpha0) > 90:
            Ks = 0
            Kr = 0
        else:
        #change depth
            self.h = h
        
            Ks = math.sqrt(cg0 / self.cg())
        
            v = math.sin(math.radians(alpha0)) * self.c() / c0;
            if abs(v) > 1:
                Kr = 0
            else:
                alpha = math.degrees(math.asin(v))
               
                self.dir = -(alpha - self.dir_bottom)
            
                Kr = math.sqrt(math.cos(math.radians(alpha0)) / math.cos(math.radians(alpha)))
            
        self.H = self.H * Ks * Kr
        
        return Ks, Kr
        
    def break_it(self):  
        error = 2 * self.b_error     
        while abs(error) > self.b_error:
            H_old = self.H
            h = self.H / self.breaker_index
            self.shoal(h)
            error = self.H - H_old
		


