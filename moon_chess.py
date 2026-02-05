import tkinter as tk
from tkinter import messagebox
import random

class MoonChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Moon Chess")
        self.center_window(self.root, 400, 500)  # Center main window

        # core state
        self.board = [""] * 9
        self.buttons = []
        self.current_player = "X"
        self.game_over = False

        # placement order for per-player 3-piece rule
        self.placement_order = {"X": [], "O": []}

        # NEW: global placement history for max-5-on-board rule
        # stores tuples: (player, index)
        self.global_order = []

        self.flash_job = {"X": None, "O": None}

        # menu settings
        self.mode = "pvp"
        self.bot_difficulty = "easy"
        self.player_starts = True

        self.create_start_screen()

    #  WINDOW UTIL 
    def center_window(self, window, width, height):
        """Center the given window on the screen."""
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        window.geometry(f"{width}x{height}+{x}+{y}")

    #  UI SETUP 
    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_start_screen(self):
        self.clear_root()
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(expand=True)

        tk.Label(frame, text="Moon Chess", font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # Mode
        tk.Label(frame, text="Mode:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.mode_var = tk.StringVar(value="pvp")
        tk.Radiobutton(frame, text="Player vs Player", variable=self.mode_var, value="pvp").grid(row=2, column=0, columnspan=2, sticky="w")
        tk.Radiobutton(frame, text="Player vs Bot", variable=self.mode_var, value="pve").grid(row=3, column=0, columnspan=2, sticky="w")

        # Difficulty
        tk.Label(frame, text="Bot difficulty:", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="w", pady=(10, 0))
        self.diff_var = tk.StringVar(value="easy")
        tk.Radiobutton(frame, text="Easy (random)", variable=self.diff_var, value="easy").grid(row=5, column=0, columnspan=2, sticky="w")
        tk.Radiobutton(frame, text="Hard (smart)", variable=self.diff_var, value="hard").grid(row=6, column=0, columnspan=2, sticky="w")

        # Turn order
        tk.Label(frame, text="Who starts?", font=("Arial", 12, "bold")).grid(row=7, column=0, sticky="w", pady=(10, 0))
        self.start_var = tk.StringVar(value="player")
        tk.Radiobutton(frame, text="Player (X)", variable=self.start_var, value="player").grid(row=8, column=0, columnspan=2, sticky="w")
        tk.Radiobutton(frame, text="Opponent / Bot (O)", variable=self.start_var, value="opponent").grid(row=9, column=0, columnspan=2, sticky="w")

        # Buttons
        tk.Button(frame, text="View Rules", command=self.show_rules, font=("Arial", 11)).grid(row=10, column=0, pady=(10, 0))
        tk.Button(frame, text="Start Game", command=self.start_game, font=("Arial", 12, "bold")).grid(row=10, column=1, pady=(10, 0))

    def show_rules(self):
        rules_text = (
            "Moon Chess\n\n"

            "BOARD\n"
            "• The game is played on a 3×3 grid.\n"
            "• It is just like the original Tic-Tac-Toe Game.\n\n"

            "PER-PLAYER RULE (3 PIECES MAX)\n"
            "• Each player may have at most 3 pieces on the board.\n"
            "• If you already have 3 pieces and place another,\n"
            "  your oldest piece is removed.\n"
            "• Your oldest piece will flash before it disappears.\n"
            "• You may place your next piece on that flashing cell.\n\n"

            "GLOBAL RULE (5 PIECES MAX)\n"
            "• At most 5 total pieces (X or O) may be on the board.\n"
            "• If a move would create 6 pieces, the oldest piece\n"
            "  overall is removed automatically.\n"
            "• This global-oldest piece is shown in light gray.\n"
            "• The global-oldest piece cannot be clicked or overwritten.\n\n"

            "PLACEMENT RULES\n"
            "• You may place a piece only on an empty cell or\n"
            "  your own flashing oldest piece.\n"
            "• You may not place a piece on any other occupied cell.\n\n"

            "WIN CONDITION\n"
            "• Get 3 in a row horizontally, vertically, or diagonally.\n"
            "• Lines broken by piece removal do not count as wins."
        )

        messagebox.showinfo("Game Rules", rules_text)


    def create_game_screen(self):
        self.clear_root()

        self.status_label = tk.Label(self.root, text="Turn: X", font=("Arial", 14, "bold"))
        self.status_label.pack(pady=10)

        board_frame = tk.Frame(self.root)
        board_frame.pack()

        self.buttons = []
        for i in range(9):
            btn = tk.Button(
                board_frame,
                text="",
                font=("Arial", 24),
                width=4,
                height=2,
                command=lambda idx=i: self.handle_click(idx)
            )
            btn.grid(row=i // 3, column=i % 3, padx=5, pady=5)
            self.buttons.append(btn)

        tk.Button(self.root, text="Restart", command=self.show_restart_menu).pack(pady=10)

    #  GAME FLOW 
    def start_game(self):
        self.mode = self.mode_var.get()
        self.bot_difficulty = self.diff_var.get()
        self.player_starts = (self.start_var.get() == "player")

        self.start_game_from_existing_settings()

    def start_game_from_existing_settings(self):
        self.board = [""] * 9
        self.placement_order = {"X": [], "O": []}
        self.global_order = []  # NEW reset
        self.flash_job = {"X": None, "O": None}
        self.game_over = False

        self.current_player = "X" if self.player_starts else "O"
        self.create_game_screen()
        self.update_status()

        if self.mode == "pve" and self.current_player == "O":
            self.root.after(400, self.bot_move)
        else:
            self.start_flashing_if_needed("X")

    def get_removable_cells_for_move(self, player):
        """
        Only the per-player oldest (when player already has 3 pieces)
        is allowed to be clicked/overwritten.
        The GLOBAL oldest (for max-5 rule) is NOT clickable.
        """
        removable = set()

        # per-player 3-piece rule (clickable overwrite allowed)
        if len(self.placement_order[player]) == 3:
            removable.add(self.placement_order[player][0])

        return removable

    def handle_click(self, index):
        if self.game_over:
            return
        if self.mode == "pve" and self.current_player == "O":
            return

        removable = self.get_removable_cells_for_move(self.current_player)

        # allowed if empty, OR it is YOUR per-player oldest cell
        if self.board[index] != "" and index not in removable:
            return

        self.stop_flashing(self.current_player)
        self.place_piece(self.current_player, index)
        self.refresh_board()

        winner = self.check_winner(self.board)
        if winner or self.is_draw(self.board):
            self.end_game(winner)
            return

        self.switch_turns()

    def switch_turns(self):
        self.current_player = "O" if self.current_player == "X" else "X"
        self.update_status()

        if self.mode == "pve" and self.current_player == "O":
            self.root.after(400, self.bot_move)
        else:
            self.start_flashing_if_needed(self.current_player)

    #  FLASHING 
    def start_flashing_if_needed(self, player):
        if len(self.placement_order[player]) == 3:
            oldest_idx = self.placement_order[player][0]
            self.flash_piece(player, oldest_idx, True)

    def flash_piece(self, player, idx, to_colored):
        if self.game_over:
            return
        color = "gold" if player == "X" else "lightblue"
        btn = self.buttons[idx]

        if to_colored:
            btn.configure(bg=color)
        else:
            btn.configure(bg="SystemButtonFace")
            # when turning "off", global highlight might need to show again
            self.update_global_oldest_highlight()

        self.flash_job[player] = self.root.after(
            400, lambda: self.flash_piece(player, idx, not to_colored)
    )


    def stop_flashing(self, player):
        job = self.flash_job.get(player)
        if job:
            self.root.after_cancel(job)
            self.flash_job[player] = None

        # reset all colors
        for i in range(9):
            self.buttons[i].configure(bg="SystemButtonFace")

        # re-apply global oldest highlight if needed
        self.update_global_oldest_highlight()
    
    def update_global_oldest_highlight(self):
        """
        Visually mark the GLOBAL oldest piece (next to be removed when total would exceed 5).
        This is NOT clickable; it's only a cue.
        """
        if not self.buttons:
            return

        # First reset any previous global highlight (but keep per-player flashing intact)
        self.clear_global_oldest_highlight()

        # Only highlight when board is currently at the global limit (5 pieces)
        if self.count_pieces(self.board) < 5:
            return
        if not self.global_order:
            return

        oldest_player, oldest_idx = self.global_order[0]

        # Only highlight if that exact piece is still there
        if self.board[oldest_idx] == oldest_player:
            # Don't overwrite the per-player flashing color if it happens to be flashing
            # (If it is flashing, it already stands out enough.)
            if self.is_flashing_cell(oldest_idx):
                return

            self.buttons[oldest_idx].configure(bg="lightgray")


    def clear_global_oldest_highlight(self):
        """Remove only the global-oldest highlight (lightgray), without touching flashing jobs."""
        if not self.buttons:
            return
        for btn in self.buttons:
            if str(btn.cget("bg")) == "lightgray":
                btn.configure(bg="SystemButtonFace")


    def is_flashing_cell(self, idx):
        """
        Returns True if idx is currently the per-player oldest cell for X or O (thus flashing).
        We use this to avoid fighting over bg color.
        """
        for p in ("X", "O"):
            if len(self.placement_order[p]) == 3 and self.placement_order[p][0] == idx and self.flash_job[p] is not None:
                return True
        return False


    #  PLACEMENT + RULES 
    def remove_piece_at(self, idx):
        """
        Remove whatever piece is at idx from:
        - board
        - placement_order for that player
        - global_order
        """
        p = self.board[idx]
        if p == "":
            return

        self.board[idx] = ""

        # remove idx from that player's order (if present)
        if idx in self.placement_order[p]:
            self.placement_order[p].remove(idx)

        # remove first matching record from global order
        for k, (gp, gidx) in enumerate(self.global_order):
            if gp == p and gidx == idx:
                self.global_order.pop(k)
                break

    def enforce_global_limit_5(self):
        """Ensure total pieces on board <= 5 by removing oldest overall pieces."""
        while self.count_pieces(self.board) > 5 and self.global_order:
            oldest_player, oldest_idx = self.global_order.pop(0)
            # If that cell still has that player's piece, remove it.
            if self.board[oldest_idx] == oldest_player:
                self.board[oldest_idx] = ""
                if oldest_idx in self.placement_order[oldest_player]:
                    self.placement_order[oldest_player].remove(oldest_idx)

    def place_piece(self, player, index):
        # Only allow overwriting if it's the player's own oldest and they already have 3 pieces
        if self.board[index] != "":
            if len(self.placement_order[player]) == 3 and self.placement_order[player][0] == index:
                self.remove_piece_at(index)  # remove own oldest, then place
            else:
                return  # illegal attempt to place on occupied cell

        # Place new piece
        self.board[index] = player
        self.placement_order[player].append(index)
        self.global_order.append((player, index))

        # Per-player max 3
        if len(self.placement_order[player]) > 3:
            oldest_idx = self.placement_order[player].pop(0)
            # remove from board and from global order
            if self.board[oldest_idx] == player:
                self.board[oldest_idx] = ""
            for k, (gp, gidx) in enumerate(self.global_order):
                if gp == player and gidx == oldest_idx:
                    self.global_order.pop(k)
                    break

        # NEW: Global max 5
        self.enforce_global_limit_5()

        self.refresh_board()

    def refresh_board(self):
        for i, btn in enumerate(self.buttons):
            btn.config(text=self.board[i])
        self.update_global_oldest_highlight()

    #  RESTART MENU 
    def show_restart_menu(self):
        menu = tk.Toplevel(self.root)
        menu.title("Restart Game")
        menu.resizable(False, False)
        menu.transient(self.root)
        menu.lift()
        self.center_window(menu, 300, 160)

        tk.Label(menu, text="Restart Game Options", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Button(menu, text="Restart with Same Settings", width=25,
                  command=lambda: (menu.destroy(), self.start_game_from_existing_settings())).pack(pady=5)
        tk.Button(menu, text="Change Settings", width=25,
                  command=lambda: (menu.destroy(), self.create_start_screen())).pack(pady=5)
        tk.Button(menu, text="Cancel", width=25, command=menu.destroy).pack(pady=5)

    #  BOT LOGIC 
    def bot_move(self):
        if self.game_over:
            return
        self.start_flashing_if_needed("O")
        self.root.after(700, self.bot_make_move)

    def bot_make_move(self):
        self.stop_flashing("O")
        move = None
        if self.bot_difficulty == "easy":
            move = self.bot_move_easy()
        else:
            move = self.bot_move_hard()

        if move is not None:
            self.place_piece("O", move)

        winner = self.check_winner(self.board)
        if winner or self.is_draw(self.board):
            self.end_game(winner)
            return

        self.switch_turns()

    def bot_move_easy(self):
        # bot can place in empty cells OR in a removable cell for this move
        removable = self.get_removable_cells_for_move("O")
        candidates = [i for i in range(9) if (self.board[i] == "" or i in removable)]
        return random.choice(candidates) if candidates else None

    def bot_move_hard(self):
        # 1) Try to win
        for idx in self.bot_candidate_moves("O"):
            board_copy = self.simulate_board("O", idx)
            if self.check_winner(board_copy) == "O":
                return idx

        # 2) Block
        for idx in self.bot_candidate_moves("O"):
            board_copy = self.simulate_board("X", idx)
            if self.check_winner(board_copy) == "X":
                return idx

        # 3) Fallback
        candidates = self.bot_candidate_moves("O")
        return random.choice(candidates) if candidates else None

    def bot_candidate_moves(self, player):
        removable = self.get_removable_cells_for_move(player)  # ONLY per-player oldest
        return [i for i in range(9) if (self.board[i] == "" or i in removable)]

    def simulate_board(self, player, index):
        """
        Simulate placing `player` at `index` applying:
        - remove if occupied-but-removable
        - per-player max3
        - global max5
        Returns only board state for winner checking.
        """
        b = self.board.copy()
        po = {"X": self.placement_order["X"][:], "O": self.placement_order["O"][:]}
        go = self.global_order[:]  # list of (player, idx)

        def count_pieces_local(bb):
            return sum(1 for v in bb if v != "")

        def remove_piece_local(idx):
            p = b[idx]
            if p == "":
                return
            b[idx] = ""
            if idx in po[p]:
                po[p].remove(idx)
            for k, (gp, gidx) in enumerate(go):
                if gp == p and gidx == idx:
                    go.pop(k)
                    break

        # Determine removable for this simulated move
        removable = set()
        if len(po[player]) == 3:
            removable.add(po[player][0])

        # If occupied and removable -> remove first
        if b[index] != "" and index in removable:
            remove_piece_local(index)
        elif b[index] != "":
            # illegal move in simulation
            return b

        # place
        b[index] = player
        po[player].append(index)
        go.append((player, index))

        # per-player max3
        if len(po[player]) > 3:
            oldest_idx = po[player].pop(0)
            # remove from board and global
            if b[oldest_idx] == player:
                b[oldest_idx] = ""
            for k, (gp, gidx) in enumerate(go):
                if gp == player and gidx == oldest_idx:
                    go.pop(k)
                    break

        # global max5
        while count_pieces_local(b) > 5 and go:
            op, oidx = go.pop(0)
            if b[oidx] == op:
                b[oidx] = ""
                if oidx in po[op]:
                    po[op].remove(oidx)

        return b

    #  UTILITIES 
    def count_pieces(self, board):
        return sum(1 for v in board if v != "")

    def is_draw(self, board):
        # With rotating pieces and global removals, a full board is unlikely.
        # We'll keep your existing draw definition.
        return all(v != "" for v in board)

    def check_winner(self, board):
        wins = [
            (0,1,2),(3,4,5),(6,7,8),
            (0,3,6),(1,4,7),(2,5,8),
            (0,4,8),(2,4,6)
        ]
        for a,b,c in wins:
            if board[a] and board[a] == board[b] == board[c]:
                return board[a]
        return None

    def update_status(self, text=None):
        self.status_label.config(text=text or f"Turn: {self.current_player}")

    def end_game(self, winner):
        self.stop_flashing("X")
        self.stop_flashing("O")
        self.status_label.config(text=f"{winner} wins!" if winner else "Draw!")
        self.game_over = True
        self.root.after(800, self.show_restart_menu)  # Auto show restart menu


if __name__ == "__main__":
    root = tk.Tk()
    app = MoonChessApp(root)
    root.mainloop()
