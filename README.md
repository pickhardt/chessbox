Chess Box
=========

The Swiss army knife of chess scripts for Python. Can read PGNs, communicate with chess engines, draw chess positions, and more.

Example Code
============

```
games = Game.games_from_pgn(open("alekhine.pgn", "r"))
error_count = 0

for game in games:
  position = Position()
  try:
    for move in game.moves:
      position.move(move)

    print position.generate_fen()
  except:
    error_count += 1

print error_count
print len(games)
```