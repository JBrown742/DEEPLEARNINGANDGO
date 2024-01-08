# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 11:03:26 2023

@author: jonathon Brown
"""
from dlgo.gotypes import Point

def is_point_an_eye(board, point, color): # Check if point is an eye (surrounded by friendlies)
    if board.get(point) is not None: # Initially check if the point is even an empty point
        return False
    for neighbour in point.neighbours(): #Check neighbouring points are friendly
        if board.is_on_grid(neighbour): #Check point is on grid 
            neighbour_color = board.get(neighbour) # Obtain neighbour color
            if neighbour_color != color: # If even a single neighbour is not friendly we return false (is not an eye)
                return False
            
    friendly_corners = 0
    off_board_corners = 0
    corners = [
            Point(point.row - 1, point.col - 1),
            Point(point.row - 1, point.col + 1),
            Point(point.row + 1, point.col - 1),
            Point(point.row + 1, point.col + 1),
        ]
    for corner in corners:
        if board.is_on_grid(corner):
            corner_color = board.get(corner)
            if corner_color == color:
                friendly_corners += 1
        else:
            off_board_corners += 1
    if off_board_corners > 0:
        return off_board_corners + friendly_corners == 4
    return friendly_corners >= 3