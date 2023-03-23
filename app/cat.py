#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from collections import deque

class Cat:
    def __init__(self, name, min_feed_interval, max_feed_hour, max_feed_8h, max_feed_day):
        self.name = name
        self.min_feed_interval = min_feed_interval
        self.max_feed_hour = max_feed_hour
        self.max_feed_day = max_feed_day
        self.max_feed_8h = max_feed_8h
        self.feed_history = deque()
    
    def appear(self):
        now = time.time()
        
        # 刚喂过
        if len(self.feed_history)>0 and now - self.feed_history[0] < self.min_feed_interval:
            return False
        
        # 这个小时已经吃了很多了
        if self.feed_count_hour() >= self.max_feed_hour:
            return False
        
        # 这8个小时已经吃了很多了
        if self.feed_count_8h() >= self.max_feed_8h:
            return False
        
        # 今天已经吃了很多了
        if self.feed_count_day() >= self.max_feed_day:
            return False
        
        # 喂一点   
        self.feed_history.append(now)
        while now - self.feed_history[0] > 2*24*3600:
            self.feed_history.popleft() #不保留2天以前的记录
        return True

    def feed_count_hour(self):
        count = 0
        now = time.time()
        for item in self.feed_history:
            if now - item <= 3600:
                count += 1
        return count
    
    def feed_count_8h(self):
        count = 0
        now = time.time()
        for item in self.feed_history:
            if now - item <= 3600 * 8:
                count += 1
        return count
    
    def feed_count_day(self):
        count = 0
        now = time.time()
        for item in self.feed_history:
            if now - item <= 3600 * 24:
                count += 1
        return count
    
