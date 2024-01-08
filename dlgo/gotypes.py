# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 14:03:33 2023

@author: jonat
"""

import enum
from collections import namedtuple

__all__ = [
    'Player',
    'Point',
]

class Player(enum.Enum):
    black = 2
    white = 1
    
    @property
    def other(self):
        # Return color of next player
        return Player.black if self == Player.white else Player.white
    
class Point(namedtuple('Point', 'row col')):
    def neighbours(self):
        # return the neoghbouring intersections 
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
            ]
