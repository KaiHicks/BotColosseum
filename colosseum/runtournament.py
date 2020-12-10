from .games import guessthatnumber as gtn

players = [
	'colosseum.games.guessthatnumber.linearbot',
	'colosseum.games.guessthatnumber.binarybot',
]
hoster = gtn.GTNHoster(players)

for _ in range(1000):
	hoster.start_game(100)

print(hoster.avg_points)