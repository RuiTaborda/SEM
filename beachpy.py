# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 09:21:55 2018

@author: rui taborda
"""
from shapely import geometry
import sys
import matplotlib.pyplot as plt

class BeachProfile:
# =============================================================================
#     General definitions
# =============================================================================
    x_coastline = 0 # beach origin - constant
    
    
# =============================================================================
#     Sandy profile default parameters
# =============================================================================

    empty_profile = False    # True if there is no sand in the beach
    y_sandy_coastline= 3.7 #if berm_slope = 0, this corresponds to berm height
    
    
    # equilibrium height of sandy coastline
    

    berm_width = False
    berm_slope = 0.01
   
    x_beachface_toe = False
    beachface_slope = 0.11
    
    target_volume = False
    secant_iterations = False
    max_secant_iter = 10
  # =============================================================================
#     Rocky profile default parameters
# =============================================================================
    y_rocky_coastline= 0.
    platform_slope = 0.01
    
    
    
# =============================================================================
#     Domain parameters
# =============================================================================
    y_resolution = 1.
    
    
    
    
    
    sand_color = (0.7, 0.7, 0.5)    
    platform_color = (0.3, 0.3, 0.3)    
    
# =============================================================================
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
  
        self.p_sandy_coastline = geometry.Point(self.x_coastline, self.y_sandy_coastline)
        self.p_equilibrium_sandy_coastline =  self.p_sandy_coastline
        self.p_rocky_coastline = geometry.Point(self.x_coastline, self.y_rocky_coastline)
    
        self.upper_bound = self.y_sandy_coastline + 5
        #lower_bound = z_closure_depth
        self.lower_bound = -2
        self.left_bound = self.x_coastline
        self.right_bound = 300.
        self.p_lower_left_bound = geometry.Point(self.left_bound, self.lower_bound)
        self.p_lower_right_bound = geometry.Point(self.right_bound, self.lower_bound)
    
        self.domain_bounds = (self.left_bound, self.right_bound, self.lower_bound, self.upper_bound)
    
       
        self.build_rocky_profile()
        self.build_sandy_profile()
        
    def build_rocky_profile(self):
        x_platform_offshore_limit = self.right_bound
        y_platform_offshore_limit = self.y_rocky_coastline - self.platform_slope * (x_platform_offshore_limit - self.x_coastline)
        self.p_platform_offshore_limit = geometry.Point(x_platform_offshore_limit, y_platform_offshore_limit)
        
        point_list = [self.p_rocky_coastline, self.p_platform_offshore_limit]
        self.platform_profile = geometry.LineString([[p.x, p.y] for p in point_list])
        
        point_list.extend([self.p_lower_right_bound, self.p_lower_left_bound])
        self.platform_polygon = geometry.Polygon([[p.x, p.y] for p in point_list])
    
        
    def build_sandy_profile(self):
        if self.empty_profile:
            self.x_beachface_toe = 0
            self.build_sandy_profile_from_beachface_toe()
        elif self.x_beachface_toe:
            self.build_sandy_profile_from_beachface_toe()
        elif self.berm_width:
            self.build_sandy_profile_from_berm()
    
#       define beach sand profile
        point_list = [self.p_sandy_coastline, self.p_shoreline, self.p_beachface_toe]
        self.sandy_profile = geometry.LineString([[p.x, p.y] for p in point_list])
        
#        define beach sand polygon
        point_list.append(geometry.Point(self.left_bound, self.p_rocky_coastline.y))
        self.sandy_polygon = geometry.Polygon([[p.x, p.y] for p in point_list])
        
        
#       self.beach_polygon = self.sandy_polygon.difference(self.platform_polygon)
   
        
        
    def build_sandy_profile_from_berm(self):
#        define shoreline and beach toe position
        self.p_shoreline = geometry.Point(self.p_sandy_coastline.x + self.berm_width,
                                          self.p_sandy_coastline.y - self.berm_slope * self.berm_width)
        
        p_beachface_end = geometry.Point(self.right_bound, self.p_shoreline.y - self.beachface_slope * (self.right_bound - self.p_shoreline.x))
        l_beachface = geometry.LineString([self.p_shoreline, p_beachface_end])
        self.p_beachface_toe = self.platform_profile.intersection(l_beachface)
        
        self.x_beachface_toe = self.p_beachface_toe.x
                
        point_list = [self.p_sandy_coastline, self.p_shoreline, self.p_beachface_toe]
        self.sandy_profile = geometry.LineString([[p.x, p.y] for p in point_list])
        
#       define beach sand polygon
        point_list.append(geometry.Point(self.left_bound, self.p_rocky_coastline.y))
        self.sandy_polygon = geometry.Polygon([[p.x, p.y] for p in point_list])
    
    def build_sandy_profile_from_beachface_toe(self):
#        define shoreline and beach toe position
        vl_beachface_toe = geometry.LineString([(self.x_beachface_toe, self.upper_bound), (self.x_beachface_toe, self.lower_bound)])
        
        self.p_beachface_toe = self.platform_profile.intersection(vl_beachface_toe)
        
        self.berm_width = (self.p_beachface_toe.y - self.p_equilibrium_sandy_coastline.y +  (self.p_beachface_toe.x - self.p_equilibrium_sandy_coastline.x) * self.beachface_slope) / (self.beachface_slope - self.berm_slope)
        
        self.p_shoreline = geometry.Point(self.p_equilibrium_sandy_coastline.x + self.berm_width,
                                         self.p_equilibrium_sandy_coastline.y - self.berm_slope * self.berm_width)
        
        l_beachface = geometry.LineString([self.p_shoreline, self.p_beachface_toe])
        
        
        if self.berm_width < 0:
            vl_coastline = geometry.LineString([(self.p_sandy_coastline.x, self.upper_bound), (self.p_sandy_coastline.x, self.lower_bound)])
            self.p_sandy_coastline = l_beachface.intersection(vl_coastline)
            self.p_shoreline = self.p_sandy_coastline
            self.berm_width = 0
        else:
            self.p_sandy_coastline = self.p_equilibrium_sandy_coastline
        
#        
    def volume(self):
        return self.sandy_polygon.area
        
    def update_volume(self, volume_dif):
        self.target_volume = volume_dif + self.sandy_polygon.area
        if self.target_volume > 0:
            self.empty_profile = False
            solution, self.secant_iterations = self.secant(self.f, self.x_beachface_toe, self.x_beachface_toe + 10, 1e-5)
        else:
            self.empty_profile = True 
            self.build_sandy_profile()
            
        

# =============================================================================
# Implementation of the secant method for updating beach volume
# Code adapted from  http://hplgit.github.io/Programming-for-Computations/pub/p4c/._p4c-solarized-Python028.html
# =============================================================================
    def secant(self, f, x0, x1, eps):
        f_x0 = f(x0)
        f_x1 = f(x1)
        iteration_counter = 0
        while abs(f_x1) > eps and iteration_counter < self.max_secant_iter:
            try:
                denominator = float(f_x1 - f_x0)/(x1 - x0)
                x = x1 - float(f_x1)/denominator
            except ZeroDivisionError:
                sys.exit(1)     # Abort with error
            x0 = x1
            x1 = x
            f_x0 = f_x1
            f_x1 = f(x1)
            iteration_counter += 1
        # Here, either a solution is found, or too many iterations
        if abs(f_x1) > eps:
            iteration_counter = -1
        print(iteration_counter)
        return x, iteration_counter

    def f(self, x):
        self.x_beachface_toe = x;
        self.build_sandy_profile()
        return self.sandy_polygon.area - self.target_volume
        
    
    
# =============================================================================
# Profile representation
# =============================================================================
    
    def plot(self):
        plt.figure()
        
        if self.sandy_polygon.area >0 :
            x, y = self.sandy_polygon.exterior.xy
            plt.fill(x, y, color = self.sand_color) 
        
        if self.platform_polygon.area >0 :
            x, y = self.platform_polygon.exterior.xy
            plt.fill(x, y, color = self.platform_color) 
                   
        plt.show()
        plt.axis(self.domain_bounds)