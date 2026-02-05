import tkinter as tk
from tkinter import messagebox
import random

class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3-Piece Tic Tac Toe")
        self.center_window(self.root, 400, 500)  # Center main window

        # core state
        self.board = [""] * 9
        self.buttons = []
        self.current_player = "X"
        self.game_over = False

        # placement order for 3-piece rule
        self.placement_order = {"X": [], "O": []}
        self.flash_job = {"X": None, "O": None}

        # menu settings
        self.mode = "pvp"
        self.bot_difficulty = "easy"
        self.player_starts = True

        self.create_start_screen()

    # --------------------- WINDOW UTIL ---------------------
    def center_window(self, window, width, height):
        """Center the given window on the screen."""
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        window.geometry(f"{width}x{height}+{x}+{y}")

    # --------------------- UI SETUP ---------------------
    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_start_screen(self):
        self.clear_root()
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(expand=True)

        tk.Label(frame, text="3-Piece Tic Tac Toe", font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

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
            "3-Piece Tic Tac Toe Rules:\n\n"
            "• The game is played on a 3×3 grid.\n"
            "• Each player can only have 3 pieces on the board at once.\n"
            "• When a player already has 3 pieces and places another,\n"
            "  their oldest piece disappears.\n"
            "• You can also place your next piece on the flashing cell\n"
            "  (the one that will disappear next).\n"
            "• The goal remains the same: get 3 in a row horizontally,\n"
            "  vertically, or diagonally."
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

    # --------------------- GAME FLOW ---------------------
    def start_game(self):
        self.mode = self.mode_var.get()
        self.bot_difficulty = self.diff_var.get()
        self.player_starts = (self.start_var.get() == "player")

        self.start_game_from_existing_settings()

    def start_game_from_existing_settings(self):
        self.board = [""] * 9
        self.placement_order = {"X": [], "O": []}
        self.flash_job = {"X": None, "O": None}
        self.game_over = False

        self.current_player = "X" if self.player_starts else "O"
        self.create_game_screen()
        self.update_status()

        if self.mode == "pve" and self.current_player == "O":
            self.root.after(400, self.bot_move)
        else:
            self.start_flashing_if_needed("X")

    def handle_click(self, index):
        if self.game_over:
            return
        if self.mode == "pve" and self.current_player == "O":
            return

        allowed = False
        if self.board[index] == "":
            allowed = True
        elif len(self.placement_order[self.current_player]) == 3:
            oldest_idx = self.placement_order[self.current_player][0]
            if index == oldest_idx:
                allowed = True

        if not allowed:
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

    # --------------------- FLASHING ---------------------
    def start_flashing_if_needed(self, player):
        if len(self.placement_order[player]) == 3:
            oldest_idx = self.placement_order[player][0]
            self.flash_piece(player, oldest_idx, True)

    def flash_piece(self, player, idx, to_colored):
        if self.game_over:
            return
        color = "gold" if player == "X" else "lightblue"
        btn = self.buttons[idx]
        btn.configure(bg=color if to_colored else "SystemButtonFace")
        self.flash_job[player] = self.root.after(
            400, lambda: self.flash_piece(player, idx, not to_colored)
        )

    def stop_flashing(self, player):
        job = self.flash_job.get(player)
        if job:
            self.root.after_cancel(job)
            self.flash_job[player] = None
        for i in range(9):
            self.buttons[i].configure(bg="SystemButtonFace")

    # --------------------- PLACEMENT + 3-RULE ---------------------
    def place_piece(self, player, index):
        if len(self.placement_order[player]) == 3:
            oldest = self.placement_order[player][0]
            if oldest == index:
                self.board[oldest] = ""
                self.placement_order[player].pop(0)
        self.board[index] = player
        self.placement_order[player].append(index)
        if len(self.placement_order[player]) > 3:
            oldest = self.placement_order[player].pop(0)
            self.board[oldest] = ""
        self.refresh_board()

    def refresh_board(self):
        for i, btn in enumerate(self.buttons):
            btn.config(text=self.board[i])

    # --------------------- RESTART MENU ---------------------
    def show_restart_menu(self):
        menu = tk.Toplevel(self.root)
        menu.title("Restart Game")
        menu.resizable(False, False)
        menu.transient(self.root)
        menu.lift()
        self.center_window(menu, 300, 160)

        tk.Label(menu, text="Restart Game Options", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Button(menu, text="🔁 Restart with Same Settings", width=25,
                  command=lambda: (menu.destroy(), self.start_game_from_existing_settings())).pack(pady=5)
        tk.Button(menu, text="⚙️ Change Settings", width=25,
                  command=lambda: (menu.destroy(), self.create_start_screen())).pack(pady=5)
        tk.Button(menu, text="❌ Cancel", width=25, command=menu.destroy).pack(pady=5)

    # --------------------- BOT LOGIC ---------------------
    def bot_move(self):
        if self.game_over:
            return
        self.start_flashing_if_needed("O")
        self.root.after(700, self.bot_make_move)

    def bot_make_move(self):
        self.stop_flashing("O")
        move = None
        if self.bot_difficulty == "easy":
            empty = [i for i, v in enumerate(self.board) if v == ""]
            move = random.choice(empty) if empty else None
        else:
            move = self.bot_move_hard()
        if move is not None:
            self.place_piece("O", move)
        winner = self.check_winner(self.board)
        if winner or self.is_draw(self.board):
            self.end_game(winner)
            return
        self.switch_turns()

    def bot_move_hard(self):
        for idx in self.empty_cells():
            board_copy = self.simulate_board("O", idx)
            if self.check_winner(board_copy) == "O":
                return idx
        for idx in self.empty_cells():
            board_copy = self.simulate_board("X", idx)
            if self.check_winner(board_copy) == "X":
                return idx
        return random.choice(self.empty_cells()) if self.empty_cells() else None

    def simulate_board(self, player, index):
        b = self.board.copy()
        order = {"X": self.placement_order["X"][:], "O": self.placement_order["O"][:]}
        b[index] = player
        order[player].append(index)
        if len(order[player]) > 3:
            oldest = order[player].pop(0)
            b[oldest] = ""
        return b

    # --------------------- UTILITIES ---------------------
    def empty_cells(self):
        return [i for i, v in enumerate(self.board) if v == ""]

    def is_draw(self, board):
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
    app = TicTacToeApp(root)
    root.mainloop()
