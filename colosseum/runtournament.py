from time import time

from progress.bar import FillingSquaresBar

from colosseum.games import dotsnboxes as dnb
from colosseum.games import guessthatnumber as gtn

game = 'guessthatnumber'

if game == 'guessthatnumber':
	players = [
		'colosseum.games.guessthatnumber.linearbot',
		'colosseum.games.guessthatnumber.binarybot',
		# 'colosseum.games.guessthatnumber.human',
	]
	hoster = gtn.GTNHoster(players)
	start_game_args = (100,)
elif game == 'dotsnboxes':
	players = [
		'colosseum.games.dotsnboxes.randombot',
		'colosseum.games.dotsnboxes.randombot',
	]
	hoster = dnb.DnBHoster(players)
	start_game_args = ()

n = 1000
print(f'Running {n} games...')
cum_time = 0
bar = FillingSquaresBar(
	'Running games...',
	suffix='%(percent)d%% [%(index)d/%(max)d] elapsed: %(elapsed)ds '
		'remaining: %(eta)ds'
)
for _ in bar.iter(range(n)):
	cum_time -= time()
	hoster.start_game(*start_game_args)
	cum_time += time()
print(f'{cum_time:0.3f} s of total runtime')
print(f'{cum_time/n:0.3f} s/game')
print(f'{n/cum_time:0.3f} game/s')