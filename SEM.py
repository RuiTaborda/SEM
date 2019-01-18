# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 10:43:05 2019

@author: rui
"""
import SEM_Grid
import wavepy

sem_grid = SEM_Grid.SEM_Grid(filename_baseline = 'baseline2.shp', filename_coastline = 'coastline5.shp', 
                             filename_beach_toe = 'shoreline3.shp', dx = 100, dt = 60, left_boundary = 'open' , right_boundary = 'closed')
offshore_wave = wavepy.Wave(H = 2, T = 12, dir = 310)

sem_grid.propagate_waves(offshore_wave)




for i in range(100):
    sem_grid.propagate_waves(offshore_wave)
    n=sem_grid.nextstep()
    print(i)

offshore_wave = wavepy.Wave(H = 2, T = 12, dir = 330)

for i in range(1000):
    sem_grid.propagate_waves(offshore_wave)
    n=sem_grid.nextstep()
    print(i)

sem_grid.plot()
sem_grid.plot_Q()
sem_grid.plot_waves()
