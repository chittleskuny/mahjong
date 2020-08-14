import json
import random

from flask import Flask
app = Flask(__name__)


class Board(object):
    card_pile, discard_pile = [], []

    players = ['player_1', 'player_2', 'player_3', 'player_4']
    player_tiles = {'player_1': [], 'player_2': [], 'player_3': [], 'player_4': []}

    def shuffle(self):
        self.card_pile, self.discard_pile = [], []
        card_pile_generator = {
            'season': {'ranks': ['spring', 'summer', 'autumn', 'winter'], 'repeat': 1, },
            'gentleman': {'ranks': ['plum', 'orchid', 'bamboo', 'chrysanthemum'], 'repeat': 1, },
            'wind': {'ranks': ['east', 'south', 'west', 'north'], 'repeat': 4, },
            'dragon': {'ranks': ['red', 'green', 'white'], 'repeat': 4, },
            'dot': {'ranks': [1, 2, 3, 4, 5, 6, 7, 8, 9], 'repeat': 4, },
            'bamboo': {'ranks': [1, 2, 3, 4, 5, 6, 7, 8, 9], 'repeat': 4, },
            'character': {'ranks': [1, 2, 3, 4, 5, 6, 7, 8, 9], 'repeat': 4, },
        }
        for type, ranks_repeat in card_pile_generator.items():
            for rank in ranks_repeat['ranks']:
                for repeat in range(ranks_repeat['repeat']):
                    self.card_pile.append('%s_%s' % (type, rank))
        random.shuffle(self.card_pile)

    def deal(self):
        start = 0
        for player in self.players:
            self.player_tiles[player] = self.card_pile[start:(start + 16)]
            start = start + 16
        self.player_tiles[self.players[0]].append(self.card_pile[start])
        self.card_pile = self.card_pile[(start + 1):]


@app.route('/')
def hello_mahjong():
    return 'Hello, Mahjong!'

@app.route('/board')
def hello_board():
    board = Board()
    board.shuffle()
    board.deal()
    data = {
        'len_card_pile': len(board.card_pile),
        'discard_pile': board.discard_pile,
        'players': board.players,
        'player_tiles': board.player_tiles,
    }
    return json.dumps(data)
