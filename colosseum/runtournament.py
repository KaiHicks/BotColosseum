from time import time

from progress.bar import FillingSquaresBar

from .games import guessthatnumber as gtn

players = [
	'colosseum.games.guessthatnumber.linearbot',
	'colosseum.games.guessthatnumber.binarybot',
	# 'colosseum.games.guessthatnumber.human',
]
hoster = gtn.GTNHoster(players)

n = 10000
print(f'Running {n} games...')
cum_time = 0
bar = FillingSquaresBar(
	'Running games...',
	suffix='%(percent)d%% [%(index)d/%(max)d] elapsed: %(elapsed)ds '
		'remaining: %(eta)ds'
)
for _ in bar.iter(range(n)):
	cum_time -= time()
	hoster.start_game(100)
	cum_time += time()
print(f'{cum_time:0.3f} s of total runtime')
print(f'{cum_time/n:0.3f} s/game')
print(f'{n/cum_time:0.3f} game/s')