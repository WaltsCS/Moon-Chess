# Moon Chess
Modified Tic-Tac-Toe

# How to Run
1. Find the Python file with the name 'moon_chess.py'
2. Open the Python File
3. Run (either with or without debugging)

# 3-Piece Tic Tac Toe(Max 5 on Board) Rules:


# BOARD
- The game is played on a 3×3 grid.

# PER-PLAYER RULE (3 PIECES MAX)
- Each player may have at most 3 pieces on the board.
- If you already have 3 pieces and place another,
    your oldest piece is removed.
- Your oldest piece will flash before it disappears.
- You may place your next piece on that flashing cell.

# GLOBAL RULE (5 PIECES MAX)
- At most 5 total pieces (X + O) may be on the board.
- If a move would create 6 pieces, the oldest piece
    overall is removed automatically.
- This global-oldest piece is shown in light gray.
- The global-oldest piece cannot be clicked or overwritten.

# PLACEMENT RULES
- You may place a piece only on an empty cell or
    your own flashing oldest piece.
- You may not place a piece on any other occupied cell.

# WIN CONDITION
- Get 3 in a row horizontally, vertically, or diagonally.
- Lines broken by piece removal do not count as wins.