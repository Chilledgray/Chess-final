from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.core.text import LabelBase
import chess
import time

import mysql.connector as mc

Builder.load_file("menu.kv")
Builder.load_file("stats.kv")


con = mc.connect(host='localhost', user='root', password='root', database='chess',
                 autocommit=True, connection_timeout=10)
c = con.cursor()

FONT_PATH = r"C:\Users\gopal\OneDrive\Desktop\chess_merida_unicode-master\chess_merida_unicode.ttf"

LabelBase.register(name="ChessMerida", fn_regular=FONT_PATH)

PIECES = {
    'K': chr(0x2654), 'Q': chr(0x2655), 'R': chr(0x2656), 'B': chr(0x2657), 'N': chr(0x2658), 'P': chr(0x2659),
    'k': chr(0x265A), 'q': chr(0x265B), 'r': chr(0x265C), 'b': chr(0x265D), 'n': chr(0x265E), 'p': chr(0x265F),
}


def stat(p):
    try:
        c.execute(
            "insert into stats values ('{}',0,0,0,0)".format(p.title())
        )
        print(p, "is a New Player")

    except:
        print(f"{p} is a returning player")


class WidgetM(RelativeLayout):
    play = BooleanProperty(False)
    menu_widget = ObjectProperty()
    stats_widget = ObjectProperty()
    bars_widget = ObjectProperty()
    user_text = StringProperty()

    def play_start(self, white_name=None, black_name=None):
        if not white_name or not black_name:
            return

        self.play = True
        self.menu_widget.opacity = 0
        self.stats_widget.opacity = 0


        stat(white_name)
        stat(black_name)

    def show_stats(self):
        self.stats_widget.opacity = 1
        self.menu_widget.opacity = 0

        player_list = self.ids.stats_widget.ids.player_list
        player_list.clear_widgets()

        c.execute(
            "select * from stats"
        )
        players = c.fetchall()

        for name, total, wins, losses, draws in players:
            winrate = round((wins / total) * 100, 1) if total > 0 else 0

            player_list.add_widget(Label(text=name, color=(1,1,1,1),bold=True, halign='center', valign='middle',
                                         text_size=(None, None)))
            player_list.add_widget(
                Label(text=str(total), color=(1, 1, 1, 1), halign='center', valign='middle', text_size=(None, None)))
            player_list.add_widget(Label(text=str(wins), color=(1,1,1,1), halign='center', valign='middle',
                                         text_size=(None, None)))
            player_list.add_widget(Label(text=str(losses), color=(1,1,1,1), halign='center', valign='middle',
                                         text_size=(None, None)))
            player_list.add_widget(Label(text=str(draws), color=(1,1,1,1), halign='center', valign='middle',
                                         text_size=(None, None)))
            player_list.add_widget(
                Label(text=f"{winrate}%", bold=True, color=(1,1,1, 1), font_size='22sp', halign='center',
                      valign='middle', text_size=(None, None)))

    def bar_press(self):
        self.bars_widget.opacity = 1

    def get_player_name(self, popup):
        name = popup.ids.text_input.text.strip().lower()
        popup.dismiss()

        player_list = self.ids.stats_widget.ids.player_list
        player_list.clear_widgets()

        if name:
            c.execute(
                "select * from stats where player = '{}'".format(name)
            )
        else:
            c.execute(
                "select * from stats"
            )

        all_players = c.fetchall()

        for pname, total, wins, losses, draws in all_players:
            winrate = round((wins / total) * 100, 1) if total != 0 else 0
            player_list.add_widget(
                Label(text=pname.title(), bold=True, color=(0, 0, 0, 1), halign='center', valign='middle',
                      text_size=(None, None)))
            player_list.add_widget(Label(text=str(total), color=(0, 0, 0, 1), halign='center', valign='middle',
                                         text_size=(None, None)))
            player_list.add_widget(Label(text=str(wins), color=(0, 0, 0, 1), halign='center', valign='middle',
                                         text_size=(None, None)))
            player_list.add_widget(
                Label(text=str(losses), color=(0, 0, 0, 1), halign='center', valign='middle',
                      text_size=(None, None)))
            player_list.add_widget(
                Label(text=str(draws), color=(0, 0, 0, 1), halign='center', valign='middle',
                      text_size=(None, None)))
            player_list.add_widget(
                Label(text=f"{winrate}%", bold=True, color=(0, 0, 0, 1), font_size='22sp', halign='center',
                      valign='middle', text_size=(None, None)))

    def home(self):
        self.menu_widget.opacity = 1
        self.stats_widget.opacity = 0


class ChessBoard(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 8
        self.board = chess.Board()
        self.selected = None
        self.legal_targets = []
        self.buttons = {}
        self.build_board()

    def build_board(self):
        for sq in reversed(chess.SQUARES):
            btn = Button(
                background_normal='',
                font_name="ChessMerida",
                font_size='80sp',
                color=(0, 0, 0, 1),
                markup=True
            )

            f, r = chess.square_file(sq), chess.square_rank(sq)
            btn.background_color = (0.78, 0.70, 0.95, 1) if (f + r) % 2 == 0 else (0.98, 0.96, 0.94, 1)

            btn.bind(on_release=lambda b, s=sq: self.click(s))
            self.buttons[sq] = btn
            self.add_widget(btn)
        self.update_pieces()

    def update_pieces(self):
        for sq, btn in self.buttons.items():
            p = self.board.piece_at(sq)
            btn.text = PIECES.get(p.symbol(), " ") if p else " "

            if sq == self.selected:
                btn.background_color = (0.710, 0.118, 0.420, .7)
            elif sq in self.legal_targets:
                btn.background_color = (1.0, 0.6, 0.8, .7)
            else:
                f, r = chess.square_file(sq), chess.square_rank(sq)
                btn.background_color = (0.78, 0.70, 0.95, 1) if (f + r) % 2 == 0 else (0.98, 0.96, 0.94, 1)

    def click(self, sq):
        if self.selected is None:
            piece = self.board.piece_at(sq)
            if piece and piece.color == self.board.turn:
                self.selected = sq
                self.legal_targets = [m.to_square for m in self.board.legal_moves if m.from_square == sq]
        else:
            move = chess.Move(self.selected, sq)
            if self.board.piece_at(self.selected).piece_type == chess.PAWN and chess.square_rank(sq) in (0, 7):
                move.promotion = chess.QUEEN
            if move in self.board.legal_moves:
                self.board.push(move)

                self.game_over_check()

            self.selected = None
            self.legal_targets = []
        self.update_pieces()

    def game_over_check(self):
        if self.board.is_game_over():
            outcome = self.board.outcome()

            white_name = App.get_running_app().white_player.title()
            black_name = App.get_running_app().black_player.title()

            white_result = "draws"
            black_result = "draws"

            if outcome.winner is True:
                white_result = "wins"
                black_result = "losses"
            elif outcome.winner is False:
                white_result = "losses"
                black_result = "wins"
            else:
                white_sql = black_sql = "draws = draws + 1"

            c.execute(f"""
                UPDATE stats 
                SET total_games = total_games + 1,
                    {white_result} = {white_result} + 1
                WHERE player = '{white_name}'
            """)
            c.execute(f"""
                UPDATE stats 
                SET total_games = total_games + 1,
                    {black_result} = {black_result} + 1
                WHERE player = '{black_name}'
            """)

            app = App.get_running_app()

            app.widget_m.clear_widgets()

            app.widget_m.add_widget(app.widget_m.menu_widget)
            app.widget_m.add_widget(app.widget_m.stats_widget)
            app.widget_m.add_widget(app.widget_m.bars_widget)

            app.widget_m.menu_widget.opacity = 1
            app.widget_m.stats_widget.opacity = 0
            app.widget_m.bars_widget.opacity = 0
            app.widget_m.play = False

    def resign(self):
        app = App.get_running_app()
        root = app.widget_m

        if self.board.turn == chess.WHITE:
            white_sql = "losses = losses + 1"
            black_sql = "wins = wins + 1"
        else:
            white_sql = "wins = wins + 1"
            black_sql = "losses = losses + 1"

        white_name = app.white_player.title()
        black_name = app.black_player.title()

        c.execute(
            f"UPDATE stats SET total_games = total_games + 1, {white_sql} WHERE LOWER(player) = '{white_name.lower()}'")
        c.execute(
            f"UPDATE stats SET total_games = total_games + 1, {black_sql} WHERE LOWER(player) = '{black_name.lower()}'")

        root.clear_widgets()
        root.add_widget(root.menu_widget)
        root.add_widget(root.stats_widget)
        root.add_widget(root.bars_widget)
        root.menu_widget.opacity = 1
        root.stats_widget.opacity = 0
        root.bars_widget.opacity = 0
        root.play = False

    def draw(self):
        app = App.get_running_app()
        root = app.widget_m

        white_name = app.white_player.title()
        black_name = app.black_player.title()

        c.execute(
            f"UPDATE stats SET total_games = total_games + 1, draws = draws + 1 WHERE LOWER(player) = '{white_name.lower()}'")
        c.execute(
            f"UPDATE stats SET total_games = total_games + 1, draws = draws + 1 WHERE LOWER(player) = '{black_name.lower()}'")

        root.clear_widgets()
        root.add_widget(root.menu_widget)
        root.add_widget(root.stats_widget)
        root.add_widget(root.bars_widget)
        root.menu_widget.opacity = 1
        root.stats_widget.opacity = 0
        root.bars_widget.opacity = 0
        root.play = False


class Graphics(App):
    widget_m = ObjectProperty(None)

    def build(self):
        self.widget_m = WidgetM()
        return self.widget_m

    def start_game_with_names(self, white_name, black_name):
        if not white_name or not black_name:
            return

        self.white_player = white_name
        self.black_player = black_name

        self.widget_m.play_start(white_name, black_name)

        self.widget_m.clear_widgets()
        board = ChessBoard()
        self.widget_m.add_widget(board)


Graphics().run()
