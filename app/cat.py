#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from collections import deque

class Cat:
    def __init__(self, name, english_name, min_feed_interval, max_feed_hour, max_feed_8h, max_feed_day):
        self.name = name
        self.english_name = english_name
        self.min_feed_interval = min_feed_interval
        self.max_feed_hour = max_feed_hour
        self.max_feed_day = max_feed_day
        self.max_feed_8h = max_feed_8h
        self.feed_history = deque()

        self.filename = "output/feed_history_" + self.name + ".txt"
        try:
            with open(self.filename, "r") as f:
                for line in f:
                    self.feed_history.append(float(line))
            print("成功加载 "+ self.name + " 的历史记录。")
        except Exception as e:
            print("加载 "+ self.name + " 的历史记录失败。", e)

    
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
        try:
            with open(self.filename, "a") as f:
                f.write(str(now)+"\n")
        except Exception as e:
            print("写入 "+ self.name + " 的历史记录失败。", e)

        # 内存中不保留2天以前的记录
        while now - self.feed_history[0] > 2*24*3600:
            self.feed_history.popleft() #内存中不保留2天以前的记录
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
    
    