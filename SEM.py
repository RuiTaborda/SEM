# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 10:43:05 2019

@author: rui
"""
import SEM_Grid
import wavepy
import datetime
import matplotlib.pyplot as plt


opt_baseline  = {'filename': 'baseline2.shp', 'x_plot': True,  'xc_plot': True}
opt_coastline = {'filename': 'coastline5.shp', 'shp_plot': True}
opt_shoreline = {'xc_plot': True, 'xc_color' : 'blue'}
opt_beach_toe = {'filename': 'shoreline3.shp', 'xc_plot': True, 'xc_color' : 'black'}

start_date = datetime.datetime(2019, 1, 1)
end_date = datetime.datetime(2019, 5, 5)
dt = datetime.timedelta(hours = 1)
dt_plot = datetime.timedelta(days = 1)

sem_grid = SEM_Grid.SEM_Grid(opt_baseline = opt_baseline, opt_coastline = opt_coastline, opt_shoreline = opt_shoreline,
                             opt_beach_toe = opt_beach_toe, dx = 50, dt = dt.seconds, left_boundary = 'closed' , right_boundary = 'closed')

offshore_wave = wavepy.Wave(H = 2, T = 12, dir = 330)

vol = []

current_date = start_date
plot_date = start_date

        
while current_date < end_date:
    
    while current_date <= plot_date:
        sem_grid.nextstep(offshore_wave)
        current_date += dt
        print(current_date.strftime('%H:%M:%S - %d/%m/%Y'))

    plot_date += dt_plot
    plt.clf()
    sem_grid.plot()
    plt.pause(0.01)
    




