# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 17:32:24 2018

@author: rui
"""
import pandas
import geopandas as gpd
import numpy as np
from shapely import geometry
import matplotlib.pyplot as plt
from scipy.constants import pi
import beachpy
from sys import exit
from copy import deepcopy
import math


class SEM_Line:
    x = []   # cell boundaries
    y = []
    xc = []
    yc = []
    boundary_point_spec = 'om'
    boundary_point_marker_size = 5
    
    mid_point_spec = '+r'
    mid_point_marker_size = 10
    
    original_line_color = []
    original_line_plot = True
    
    transects_color = 'green'
    transects_plot = True
    
    
    filename = []
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
 
        if self.filename == []:
            return
        try:
            self.original_line = gpd.read_file(self.filename)
        except IOError:
            print('An error occured trying to read the file  -> ', self.filename)
 
    
    def compute_mid_cells(self):
        self.xc = (self.x[1:] + self.x[:-1]) / 2
        self.yc = (self.y[1:] + self.y[:-1]) / 2

    def build_transects(self, transect_length):
        self.trans_dir = self.normals_from_cell_boundaries()
        self.x_trans, self.y_trans = self.xycoords_from_distance(transect_length) 
        
        lines = []
        for xc, yc, x_trans, y_trans in zip(self.xc, self.yc, self.x_trans, self.y_trans):
            lines.append(geometry.LineString(((xc, yc), (x_trans, y_trans))))
        self.transects = gpd.GeoDataFrame(crs = self.original_line.crs, geometry=lines)
    
    def normals_from_cell_boundaries(self):
        dx = self.x[1:] - self.x[:-1]
        dy = self.y[1:] - self.y[:-1]
        return pi/2 + np.arctan2(dy, dx)
    
    def normals_from_cell_centers(self):
        dx = self.xc[1:] - self.xc[:-1]
        dy = self.yc[1:] - self.yc[:-1]
        normals = pi/2 + np.arctan2(dy, dx)
        
        return np.insert(normals, (0, -1), (normals[0], normals[-1]), axis = 0) #first and last cells have the same azimuth 
    
    def azimuth_from_normals_degress(self): #azimuth from shore_normals
        normals = self.normals_from_cell_centers()
        return np.mod(90 - np.rad2deg(normals), 360)
        
    def cell_lenght(self):
        dx = self.x[1:] - self.x[:-1]
        dy = self.y[1:] - self.y[:-1]
        return np.hypot(dx, dy)
    
    def create_grid(self, dx, transect_length): # adpated from https://stackoverflow.com/questions/34906124/interpolating-every-x-distance-along-multiline-in-shapely/35025274#35025274
        geom = self.original_line.geometry
        self.num_cells = int(round(geom.length / dx))
        points = [geom.interpolate(float(n) / self.num_cells, normalized=True) for n in range(self.num_cells + 1)]
        
        self.x = np.array([p.x for p in points])
        self.y = np.array([p.y for p in points])
        
        self.compute_mid_cells()
        self.build_transects(transect_length)
    
    def xycoords_from_distance(self, dist):
        xc = self.xc + dist * np.cos(self.trans_dir) 
        yc = self.yc + dist * np.sin(self.trans_dir) 
        return xc, yc

class SEM_Grid:
    filename_baseline = 'baseline.shp' # shapefile filename
    filename_coastline = 'coastline.shp' 
    filename_beach_toe = 'beach_toe.shp'

    beach_profile = []
    
    left_boundary = 'open'
    right_boundary = 'open'
    
    dt = 60 * 60 
    
    shoreline = SEM_Line()
    dx = 500   
    transect_length = 1000
    
    nearshore_depth = 10
    K = 0.39
    
    lineDir = False  # display line direction
    
    max_iter_qpot2qnet = 100 # maximum iterations used in transforming q potential in q net
  
  
  
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
 
        self.baseline = SEM_Line(filename = self.filename_baseline, original_line_plot = True, boundary_point_spec = 'om', original_line_color = 'green')
        self.coastline = SEM_Line(filename = self.filename_coastline, original_line_plot = True, boundary_point_spec = 'om', original_line_color = 'red')
        self.beach_toe = SEM_Line(filename = self.filename_beach_toe, original_line_plot = True, boundary_point_spec = 'xm', original_line_color = 'blue')
        self.create_computational_grid()
    
    
    
    def create_computational_grid(self):
        self.baseline.create_grid(self.dx, self.transect_length)
        self.coastline.xc, self.coastline.yc = self.transect_intersection(self.coastline.original_line, self.baseline.transects)
        self.beach_toe.xc, self.beach_toe.yc = self.transect_intersection(self.beach_toe.original_line, self.baseline.transects)
        
        b_w = self.dist(self.beach_toe, self.coastline)
        self.beach_width = b_w.flatten()
        
        self.beach_profile = [beachpy.BeachProfile(x_beachface_toe = beach_width) for beach_width in self.beach_width]
        self.compute_shoreline_from_profiles()
                
        
    @staticmethod
    def transect_intersection(line, transects):
        points = [line.intersection(transect) for transect in transects.geometry]
        xc = np.array([(point.x) for point in points])
        yc = np.array([(point.y) for point in points])
        return xc, yc
        
    @staticmethod
    def dist(line1, line2):
        return np.hypot(line1.xc-line2.xc, line1.yc-line2.yc)
        
    def compute_shoreline_from_profiles(self):
        dist_shoreline_to_coastline = np.array([profile.p_shoreline.x for profile in self.beach_profile])
        dist_shoreline_to_coastline.resize(dist_shoreline_to_coastline.size,1) # put in a compatible format
        dist_coastline_to_baseline = self.dist(self.coastline, self.baseline)
        self.shoreline.xc, self.shoreline.yc = self.baseline.xycoords_from_distance(dist_shoreline_to_coastline + dist_coastline_to_baseline)
     
    def compute_beachface_toe_from_profiles(self):
        dist_beachface_toe_to_coastline = np.array([profile.x_beachface_toe for profile in self.beach_profile])
        dist_beachface_toe_to_coastline.resize(dist_beachface_toe_to_coastline.size,1) # put in a compatible format
        dist_coastline_to_baseline = self.dist(self.coastline, self.baseline)
        self.beach_toe.xc, self.beach_toe.yc = self.baseline.xycoords_from_distance(dist_beachface_toe_to_coastline + dist_coastline_to_baseline)
     
        
    def propagate_waves(self, offshore_wave):
        
       
        nearshore_angle = self.baseline.azimuth_from_normals_degress()
        shoreline_angle = self.beach_toe.azimuth_from_normals_degress()
     
        
        self.offshore_waves = []
        self.nearshore_waves = []
        self.breaking_waves = []   
     
        for transect_boundary in range(nearshore_angle.size):
            self.offshore_waves.append(deepcopy(offshore_wave))
            self.offshore_waves[transect_boundary].set_dir_bottom(nearshore_angle[transect_boundary])
            
            self.nearshore_waves.append(deepcopy(self.offshore_waves[transect_boundary]))
            self.nearshore_waves[transect_boundary].shoal(self.nearshore_depth)
            
            self.breaking_waves.append(deepcopy(self.nearshore_waves[transect_boundary]))
            self.breaking_waves[transect_boundary].set_dir_bottom(shoreline_angle[transect_boundary])
            self.breaking_waves[transect_boundary].break_it()
            
    def Q_potential(self):
        Q = np.array([self.dt * 0.233 * self.K * wave.H**(5/2) * math.sin(np.deg2rad(wave.alpha()) * 2) for wave in self.breaking_waves]) # CEM Eq III-2-7b (Rosati et al., 2002)     
        
        if self.left_boundary == 'closed':
            Q[0] = 0
        elif self.left_boundary == 'open':
            Q[0] = Q[1]
        else:
            exit('SEM_Grid error: left boundary not defined')
            
                
        if self.right_boundary == 'closed':
            Q[-1] = 0
        elif self.right_boundary == 'open':
            Q[-2] = Q[-1]
        else:
            exit('SEM_Grid error: right boundary not defined')
            
        return Q
        
    def beach_volume(self):
       return  np.array([profile.volume() for profile in self.beach_profile]) 
    
    def Q_net(self):
        return self.q_net(self.Q_potential(), self.beach_volume())

    def nextstep(self):
        Q = self.Q_net()
        dv_cell = np.diff(Q) 
        dv_profile = dv_cell / self.baseline.cell_lenght().flatten() 
        self.update_profiles(-dv_profile)
    
    def update_profiles(self, dv):
        for dvol, profile in zip(dv, self.beach_profile):
            profile.update_volume(dvol) 
        self.compute_beachface_toe_from_profiles()
    
    @staticmethod
    def divergent_cells(q_pot):
        return (np.sign(q_pot[1:])-np.sign(q_pot[:-1])) == 2
  
    @staticmethod
    def recalculate_q(q_old, v, vnew):
        q_left = np.sign(q_old[:-1]) == -1
        q_right = np.sign(q_old[1:]) == 1
      
        vnew[vnew>0] = 0
        
        v_correction = vnew.copy()
        v_correction[v_correction > 0] = 0
        
        div_cells = SEM_Grid.divergent_cells(q_old)
        v_correction[div_cells] = vnew[div_cells]/2
        
        q_correction = q_old.copy()
        q_correction_left = q_correction[:-1].copy()
        q_correction_right = q_correction[1:].copy()
        
        q_correction_left[q_left] -=v_correction[q_left]
        q_correction_left[~q_left] = 0
        
        q_correction_right[q_right] +=v_correction[q_right]
        q_correction_right[~q_right] = 0
        
        
        q_corrected = np.concatenate(([q_old[0]], q_correction_right)) + np.concatenate((q_correction_left, [q_old[-1]]))
    
        q_corrected[0] = q_old[0]
        q_corrected[-1] = q_old[-1]
    
        return q_corrected
         
    
    @staticmethod
    def q_net(q_pot, v):
    
        div_cells = SEM_Grid.divergent_cells(q_pot)
        
        # at divergent cells potential transport if assumed to be equal at both sides 
        # this constrain should be only applicable at very specific locations  
        divergent_q = abs(np.array([q_pot[1:][div_cells],  q_pot[:-1][div_cells]])).min(0)
        q_pot[:-1][div_cells] = -divergent_q
        q_pot[1:][div_cells] = divergent_q
        
        for x in range(SEM_Grid.max_iter_qpot2qnet):
            dq = -np.diff(q_pot)
            vnew = v + dq
            
            if np.sum(vnew<0):
               q_pot = SEM_Grid.recalculate_q(q_pot, v, vnew) 
               
            else:
               break
               
        return q_pot

    
    def plot(self):
        fig, ax = plt.subplots()
        if self.baseline.original_line_plot:
            self.baseline.original_line.plot(ax=ax, color = self.baseline.original_line_color)
    
        plt.plot(self.baseline.x, self.baseline.y, self.baseline.boundary_point_spec, markersize = self.baseline.boundary_point_marker_size)
        plt.plot(self.baseline.xc, self.baseline.yc, self.baseline.mid_point_spec, markersize = self.baseline.mid_point_marker_size)
        
        for i, x, y in zip(range(self.baseline.xc.size), self.baseline.xc, self.baseline.yc):         
            ax.annotate('%s' %i, xy=(x,y), xytext=(5,0), textcoords='offset points')
    
        if self.baseline.transects_plot:
            self.baseline.transects.plot(ax=ax, color = self.baseline.transects_color)
     
    
        if self.coastline.original_line_plot:
            self.coastline.original_line.plot(ax=ax, color = self.coastline.original_line_color)
            
        if self.beach_toe.original_line_plot:
            self.beach_toe.original_line.plot(ax=ax, color = self.beach_toe.original_line_color)
     
        
        plt.plot(self.coastline.xc, self.coastline.yc, 'm', markersize = self.coastline.mid_point_marker_size)
        plt.plot(self.beach_toe.xc, self.beach_toe.yc, 'k', markersize = self.beach_toe.mid_point_marker_size)
        
        plt.plot(self.shoreline.xc, self.shoreline.yc, 'd', markersize = 5)
        
#        for i, x, y in zip(range(self.beach_toe.xc.size), self.beach_toe.xc, self.beach_toe.yc):         
#            ax.annotate('%s' %i, xy=(x,y), xytext=(5,0), textcoords='offset points')
#      
#        for i, x, y in zip(range(self.coastline.xc.size), self.coastline.xc, self.coastline.yc):         
#            ax.annotate('%s' %i, xy=(x,y), xytext=(5,0), textcoords='offset points')
        
        plt.axis('equal')
 
    def plot_waves(self):
        df = pandas.DataFrame({ 'H':     [wave.H for wave in self.breaking_waves],
                               'alpha': [wave.alpha() for wave in self.breaking_waves]})  
        fig, ax = plt.subplots()
        plt.plot(df['H'], '--r', label=r' $H_b$')
        plt.legend(loc='upper left')
        plt.xlabel('transect number')
        
        ax.twinx()
        plt.plot(df['alpha'], '--b', label=r'$\alpha_b$')
        plt.legend(loc='upper right')
        
      
    def plot_Q(self):
        
        fig, ax = plt.subplots()
        plt.plot(self.Q_net(), '-k', label=r' $Q_net$')
        plt.legend(loc='upper left')
        plt.xlabel('transect number')
        
        ax.twinx()
        plt.plot(self.Q_potential(), '--r', label=r' $Q_potential$')
        plt.legend(loc='upper right')
        
        
        
        
        