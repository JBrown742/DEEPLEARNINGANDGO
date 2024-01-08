# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 14:04:01 2023

@author: jonat
"""
import copy
from dlgo.gotypes import Player
from dlgo.gotypes import Point


class Move():
    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    @classmethod
    def play(cls, point):
        return Move(point=point)

    @classmethod
    def pass_turn(cls):
        return Move(is_pass=True)

    @classmethod
    def resign(cls):
        return Move(is_resign=True)

class GoString():
    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = set(stones)
        self.liberties = set(liberties)

    def remove_liberty(self, point):
        self.liberties.remove(point)

    def add_liberty(self, point):
        self.liberties.add(point)

    def merged_with(self, go_string):
        assert go_string.color == self.color
        combined_stones = self.stones | go_string.stones
        return GoString(self.color, combined_stones, (self.liberties | go_string.liberties) - combined_stones)

    @property
    def num_liberties(self):
        return len(self.liberties)

    def __eq__(self, other):
        return isinstance(other, GoString) and \
            self.color == other.color and \
            self.stones == other.stones and \
            self.liberties == other.liberties


class Board():
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}
        
    def is_on_grid(self, point):
        # Check whether the point is on the grid
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols
            
    def get(self, point):
        # get the string color associated to a point
        string = self._grid.get(point)
        if string is None:
            return None
        return string.color
    
    def get_go_string(self, point):
        # Get the actual string associated to a given point
        string = self._grid.get(point)
        if string is None:
            return None
        return string
        
    def place_stone(self, player, point): # Function for placing a stone on the board
        assert self.is_on_grid(point) # Assert point is on grid
        assert self._grid.get(point) is None # Assert no stone already there
        adjacent_same_color = []
        adjacent_opposite_color = []
        liberties = []
        for neighbour in point.neighbours(): # For each neighbour
            if not self.is_on_grid(neighbour): # If not a grid point continue
                continue
            neighbour_string = self._grid.get(neighbour) # Get string for nb
            if neighbour_string is None: # If neighbour is lonely
                liberties.append(neighbour) # Append neighbour to liberty list
            elif neighbour_string.color == player: # Check if string belongs to current player or opponent
                if neighbour_string not in adjacent_same_color:
                    # Since strings connected to multiple neighbours could be
                    # added already, check that this isn't the case then add.
                    adjacent_same_color.append(neighbour_string)
        new_string = GoString(player, [point], liberties) # New string with only current point for now
        for same_color_string in adjacent_same_color:
            # Iterate over all adjacent strings and merge them with new_string
            new_string = new_string.merged_with(same_color_string)
        for new_string_point in new_string.stones:
            # Now associate this now merged string with each grid point in the string
            self._grid[new_string_point] = new_string
        for other_color_string in adjacent_opposite_color:
            # Remove the point from liberties for other color
            other_color_string.remove_liberty(point)
        for other_color_string in adjacent_opposite_color:
            # If any adjacent color string now have zero liberties remove them
            if other_color_string.num_liberties == 0:
                self._remove_string(other_color_string)
        
        
    def _remove_string(self, string):
        for point in string.stones:
            # Iterate over each point in the captured string
            for neighbour in point.neighbours():
                # Get each associated neighbour string 
                neighbour_string = self._grid.get(neighbour)
                if neighbour_string is None:
                    continue
                if neighbour_string is not string: 
                    # This is true if the neighbour is one of the opposing
                    # stones. And in this case we add a liberty to that stone
                    neighbour_string.add_liberty(point)
            # remove stones
            self._grid[point] = None
    
    def __eq__(self, other):
        return isinstance(other, Board) and \
            self.num_rows == other.num_rows and \
            self.num_cols == other.num_cols and \
            self._grid == other._grid
            
class GameState():
    def __init__(self, board, next_player, previous, move):
        self.board = board # Current board
        self.next_player = next_player # next_player (which in this case happens to also be the player that made last move)
        self.previous_state = previous # previous game state
        self.last_move = move # previous move, paradoxically made by next_player
        
    def apply_move(self, move):
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            next_board.place_stone(self.next_player, move.point)
        else:
            next_board = self.board
        return GameState(next_board, self.next_player.other, self, move)
    
    @classmethod
    def new_game(cls, board_size):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)
    
    def is_over(self):
        if self.last_move is None:
            return False
        if self.last_move.is_resign:
            return True
        second_last_move = self.previous_state.last_move
        if second_last_move is None:
            return False
        return self.last_move.is_pass and second_last_move.is_pass
    
    def is_move_self_capture(self, player, move): # Check for self capture
        if not move.is_play: # Check move has not been passed
            return False
        next_board = copy.deepcopy(self.board) # copy board
        next_board.place_stone(player, move.point) # place stone
        new_string = next_board.get_go_string(move.point) # get the string for the point just player
        return new_string.num_liberties == 0 # Return true if the number of liberties for said string ==0.
    
    @property
    def situation(self):
        return (self.next_player, self.board)
    
    def does_move_violate_ko(self, player, move):
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        next_situation = (player.other, next_board)
        past_state = self.previous_state
        while past_state is not None:
            if past_state.situation == next_situation:
                return True
            past_state = past_state.previous_state
        return False
    
    def is_valid_move(self, move):
        if self.is_over():
            return False
        if move.is_pass or move.is_resign:
            return True
        return (
            self.board.get(move.point) is None and 
            not self.is_move_self_capture(self.next_player, move) and
            not self.does_move_violate_ko(self.next_player, move))
    
    
    