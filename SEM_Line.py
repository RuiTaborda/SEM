# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 17:32:24 2018

@author: rui
"""

import geopandas as gpd
from shapely import geometry
import matplotlib.pyplot as plt

class SEM_Line:
    filename_baseline = 'baseline.shp' # shapefile filename
    lineType = 'baseline'
    distance = 1000
    
    
    boundary_point_spec = 'xm' # plot grid point specification
    boundary_point_marker_size = 5
    
    original_line_plot = True
    original_line_color = 'green'
    
    
    lineDir = False  # display line direction
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        

        try:
            self.original_line = gpd.read_file(self.filename_baseline)
            self.create_grid(self.distance)
        except IOError:
            print('An error occured trying to read the baseline file', self.filename_baseline)
            
    def create_grid(self, distance): # adpated from https://stackoverflow.com/questions/34906124/interpolating-every-x-distance-along-multiline-in-shapely/35025274#35025274
        geom = self.original_line.geometry
        self.num_cells = int(round(geom.length / distance))
        points = [geom.interpolate(float(n) / self.num_cells, normalized=True) for n in range(self.num_cells + 1)]
        self.cell_boundary = geometry.LineString([[p.x, p.y] for p in points])
    
    def plot(self):
        
        if self.original_line_plot:
            self.original_line.plot(color = self.original_line_color)
        
        x, y = self.cell_boundary.xy
        plt.plot(x, y, self.boundary_point_spec, markersize = self.boundary_point_marker_size)
        plt.axis('equal')
 
    