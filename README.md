Quantum Chess is like normal chess, but the game state can be placed into a superposition by either:
1) Moving a piece: When a piece is moved, a new branch is made for every possible move that piece could have made from their square.
2) Moving to a square: When a destination square is chosen, a new branch is made for every possible move where a piece could land on that square.
The ramifications of this are very interesting.

Read more here: https://www.cemetech.net/forum/viewtopic.php?p=307260

I probably could have a better naming scheme for these files but whatever.

**quantum_chess.py**

This library contains the `QuantumChessGame` class and some rudimentary ASCII visualization functions. Game logic is handled by the `chess` library on PyPi. https://pypi.org/project/chess/

Intantiating a new Quantum Chess game from a standard starting position:
```
import quantum_chess as ch
game = ch.QuantumChessGame()
```

**Qchess.py**

This is a (not very featureful) interface that allows you to play a game of Quantum Chess against another human player.

**many_worlds_solitaire.py**

This is an (also not very featureful) interface that allows you to play a game of Quantum Chess against a computer who can simultaneously play all their moves at once. I'm not sure where I'll go with this, but I'm intrigued by a deterministic chess-based solitaire. It's fun to play around with.
