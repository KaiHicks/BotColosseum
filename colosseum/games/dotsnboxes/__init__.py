"""
-- Dots and Boxes --
An n x n grid of dots is drawn and two players take turns connecting adjacent 
dots. If the line that a player draws completes a square, said square (or box)
is considered captured by the player. The player is then awarded an extra turn.
When all adjacent dots have been connected, the number of boxes that each 
player captured is counted and the player with the highest number of captures 
wins. 
"""

__all__ = ['DnBHoster', 'DnBTracker']

from .hoster import DnBHoster
from .tracker import DnBTracker