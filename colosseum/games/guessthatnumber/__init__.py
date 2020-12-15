"""
A simple guess-that-number game. Players take turns guessing a secret number 
between lower and upper (normally 0 and 100). After a guess, all players are 
informed of the guess as well as if the secret number was lower or higher. The 
game ends when some player guesses the secret number correctly. That player is
the winner. 
"""

__all__ = ['GTNTracker', 'GTNHoster']

from .hoster import GTNHoster
from .tracker import GTNTracker