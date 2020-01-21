# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 20:48:13 2020

@author: noema
"""
import tkinter as tk
from math import log
from statistics import mean
import time

sample_size = 10
width = 460

class Graph(tk.Canvas):
    def __init__(self, master, width, height, max_x=10, max_y=100, bg='white',
                 refresh_rate = 15, window_size=7):
        super().__init__(master, width=width, height=height, bg=bg, 
                         highlightthickness=0)
        self.width = width
        self.height = height
        self.points = []
        self.all_points = []
        self.max_x = max_x
        self.max_y = max_y
        self.min_x = 0
        self.min_y = 0
        self.refresh_rate = refresh_rate
        self.window_size = window_size
        
        self.actions = []
        self.start_time = 0
        self.paused_time = 0  # time interval of pause
        self.pause_time = 0  # time of pause start
        self.keypresses = 0
        self.clicks = 0
        self.active = "inactive"
        self.cur_apm = 0
        self.max_apm = 0
        self.avg_apm = 0
        self.active_time = 0
        self.refreshing = 0

    def axis(self):
        ax = log(self.max_x - self.min_x, 10)
        ay = log(self.max_y - self.min_y, 10)
        div_x = int(10**(ax-1) * (self.max_x - self.min_x) // 10**ax+1)
        div_y = int(10**(ay-1) * (self.max_y - self.min_y) // 10**ay+1)
        
        nb_points_x = int((self.max_x - self.min_x) // div_x)
        nb_points_y = int((self.max_y - self.min_y) // div_y)
        color = "#CCCCFF"
        for i in range(1, nb_points_x):
            x = int(i * div_x / (self.max_x - self.min_x) * self.width)
            self.create_line(x, self.height, x, self.height-5, 
                             fill=color)
            
            if i%2 == 1:
                self.create_text(x, self.height-8, text="{}".format(int(self.min_x + i*div_x)),
                             font='Arial 7', fill=color)
    
        for i in range(1, nb_points_y):
            y = int((i * div_y) / (self.max_y - self.min_y) * self.height)
            self.create_line(0, self.height - y, 5, self.height - y,
                             fill=color)
            
            #TODO: sec_to_hms
            if i%2 == 1:
                self.create_text(7, self.height - y, text="{}".format(int(self.min_y + i*div_y)),
                             font='Arial 7', fill=color, anchor='w')
            
    def draw_point(self, pts, i, redraw_axis=True):        
        if i > 0:
            x0 = int((pts[i-1][0] - self.min_x) / (self.max_x - self.min_x) * self.width)
            y0 = int((pts[i-1][1] - self.min_y) / (self.max_y - self.min_y) * self.height)
            y0 = self.height - y0
            
            x1 = int((pts[i][0] - self.min_x) / (self.max_x - self.min_x) * self.width)
            y1 = int((pts[i][1] - self.min_y) / (self.max_y - self.min_y) * self.height)
            y1 = self.height - y1
            self.create_line(x0, y0, x1, y1, fill='#6666FF', width=5)
            self.create_polygon(x0, self.height, 
                                x0, y0, 
                                x1, y1, 
                                x1, self.height, fill="#272770")
        if redraw_axis:
            self.axis()

    def add_point(self, x, y):
        self.points.append((x, y))
        self.all_points.append((x, y))
        
    def display(self):
        self.delete("all")
        
        if self.points:
            # adjusting axis scales (after discarding old points)
            m = max([p[1] for p in self.points])
            if m < self.max_y//2:
                self.max_y = max(self.max_y//2, 10)
            
            if self.points[-1][1] > max(self.max_y - 10, 10):
                self.max_y *= 2
        
            self.max_x = max(self.points[-1][0], 5)
            self.min_x = max(self.max_x - self.window_size, 0)
            
            
            # discarding old points that went out of the graph window
            i = 0
            while i < len(self.points) and self.points[i][0] < self.min_x:
                i += 1
            self.points = self.points[i:]
            
            for i in range(len(self.points)):
                self.draw_point(self.points, i, redraw_axis=False)
        
        self.axis()
    
    def add_action(self, action_time):
        self.actions.append(action_time - self.start_time - self.paused_time)
        
    def refresh(self):
        self.refreshing += 1
        if self.active == "active":
            self.after(1000//self.refresh_rate, self.refresh)
            t = time.time() - self.start_time - self.paused_time
            
            # discarding actions older than [sample_size] seconds
            if self.actions:
                i = 0
                while i < len(self.actions) and t - self.actions[i] > sample_size:
                    i += 1
                self.actions = self.actions[i:]
            
            # checking inactive time (you are considered inactive if you haven't
            # done any action in the last 3 seconds)
            i = 0
            while i < len(self.actions) and t - self.actions[i] > 3:
                i += 1
                
            if self.actions[i:]: 
                self.active_time += 1/self.refresh_rate
                
            print(self.actions)
            self.cur_apm = 60 / sample_size * len(self.actions)
            
            if self.cur_apm > self.max_apm:
                self.max_apm = self.cur_apm
                
            n = len(self.all_points)
            self.avg_apm = round((n * self.avg_apm + self.cur_apm) / (n+1), 2)

            self.add_point(t, self.cur_apm)
            self.display()
        self.refreshing -= 1
        
    def play(self):
        if self.active == "inactive":
            self.start_time = int(time.time())
        elif self.active == "paused":
            self.paused_time += time.time() - self.pause_time
        self.active = "active"
        self.refresh()

    def pause(self):
        self.pause_time = time.time()
        self.delete("all")
        self.active = "paused"
        self.min_x = 0
        self.min_y = 0
        self.max_x = max(max([p[0] for p in self.all_points]), 10)
        self.max_y = max(max([p[1] for p in self.all_points]), 10) + 10
        
        p = [self.all_points[i] for i in range(len(self.all_points))]
        while len(p) > 4*width//5:
            p = [p[i] for i in range(len(p)) if i%2 == 0]
        for i in range(len(p)):
            self.draw_point(p, i, redraw_axis=False)
        self.axis()

    def reset(self):
        self.active = "inactive"
        self.paused_time = 0
        
        self.min_x = 0
        self.max_x = 10
        self.min_y = 0
        self.max_y = 10
        self.keypresses = 0
        self.start_time = 0
        self.pause_time = 0  # time at which it pause began
        self.keypresses = 0
        self.clicks = 0
        self.cur_apm = 0
        self.max_apm = 0
        self.avg_apm = 0
        self.active_time = 0
        self.refreshing = 0
        self.actions = []
        self.points = []
        self.all_points = []
        self.delete("all")
        self.display()