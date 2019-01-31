# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 10:43:05 2019

@author: rui
"""
import SEMGrid
import wavepy
import datetime
import matplotlib.pyplot as plt

opt_baseline = {'filename': 'data/baselineTeste1.shp', 'x_plot': True, 'xc_plot': True}
opt_coastline = {'filename': 'data/coastlineTeste1.shp', 'shp_plot': True}
opt_shoreline = {'xc_plot': True, 'xc_color': 'blue'}
opt_beach_toe = {'filename': 'data/shorelineFill1.shp', 'xc_plot': True, 'xc_color': 'black'}

start_date: datetime = datetime.datetime(2019, 1, 1)
end_date = datetime.datetime(2020, 10, 1)
dt = datetime.timedelta(hours=10)
dt_plot = datetime.timedelta(days=5)

sem_grid = SEMGrid.SEMGrid(opt_baseline=opt_baseline, opt_coastline=opt_coastline, opt_shoreline=opt_shoreline,
                           opt_beach_toe=opt_beach_toe, dx=200, dt=dt.seconds, left_boundary='closed',
                           right_boundary='open')

offshore_wave = wavepy.Wave(H=0.75, T=8, dir=345)

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
    days = (current_date - start_date).days
    sem_grid.plot(days)
    plt.pause(0.01)
