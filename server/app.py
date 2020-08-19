import json
import random

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app, use_native_unicode='utf8')


class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.String(11), primary_key=True)
    name = db.Column(db.String(45), default='Anonymous Player', nullable=False)
    win_rate = db.Column(db.Float, default='0', nullable=False)


class Board(db.Model):
    __tablename__ = 'boards'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    total = db.Column(db.Integer, default=0, nullable=False)
    number = db.Column(db.Integer, default=0, nullable=False)
    card_pile = db.Column(db.String(2048))
    discard_pile = db.Column(db.String(2048))
    player_1 = db.Column(db.String(11))
    player_2 = db.Column(db.String(11))
    player_3 = db.Column(db.String(11))
    player_4 = db.Column(db.String(11))
    player_1_tiles = db.Column(db.String(512))
    player_2_tiles = db.Column(db.String(512))
    player_3_tiles = db.Column(db.String(512))
    player_4_tiles = db.Column(db.String(512))
    player_1_played_tiles = db.Column(db.String(512))
    player_2_played_tiles = db.Column(db.String(512))
    player_3_played_tiles = db.Column(db.String(512))
    player_4_played_tiles = db.Column(db.String(512))


def shuffle():
    card_pile, discard_pile = [], []
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
                card_pile.append('%s_%s' % (type, rank))
    random.shuffle(card_pile)
    return card_pile, discard_pile


def deal(card_pile, circle):
    player_tiles = {}
    start = 0
    for player in circle:
        player_tiles[player] = card_pile[start:(start + 16)]
        start = start + 16
    player_tiles[circle[0]].append(card_pile[start])
    card_pile = card_pile[(start + 1):]
    return card_pile, player_tiles


@app.route('/')
def hello_mahjong():
    return 'Hello, Mahjong!'


@app.route('/board', methods=['GET', 'POST'])
def do_board():
    input = {
        'id': int(request.form['id']),
    }
    board = Board.query.filter_by(id=input['id']).first()
    if board:
        if board.card_pile:
            card_pile = board.card_pile.split(',')
            len_card_pile = len(card_pile)
        else:
            len_card_pile = None

        if board.discard_pile:
            discard_pile = board.discard_pile.split(',')
        else:
            discard_pile = []

        players = []
        if board.player_1:
            players.append(board.player_1)
            if board.player_2:
                players.append(board.player_2)
                if board.player_3:
                    players.append(board.player_3)
                    if board.player_4:
                        players.append(board.player_4)

        output = {
            'total': board.total,
            'number': board.number,
            'len_card_pile': len_card_pile,
            'discard_pile': discard_pile,
            'players': players,
        }

    else:
        output = {}

    return json.dumps(output)


@app.route('/board/init', methods=['POST'])
def do_board_init():
    input = {
        'total': int(request.form['total']),
        'master': request.form['master'],
    }
    player_1 = Player.query.filter_by(id=input['master']).first()
    board = Board(total=input['total'], number=1, player_1=player_1.id)
    db.session.add(board)
    db.session.commit()

    output = {
        'id': board.id,
    }
    return json.dumps(output)


@app.route('/board/join', methods=['POST'])
def do_board_join():
    input = {
        'id': int(request.form['id']),
        'slave': request.form['slave'],
    }
    board = Board.query.filter_by(id=input['id']).first()

    if board.player_1 == input['slave']:
        result, position = 'REJECT', 1
    elif not board.player_2:
        Board.query.filter_by(id=input['id']).update({'player_2':input['slave']})
        db.session.commit()
        result, position = 'ACCEPT', 2
    elif board.player_2 == input['slave']:
        result, position = 'REJECT', 2
    elif not board.player_3:
        Board.query.filter_by(id=input['id']).update({'player_3':input['slave']})
        db.session.commit()
        result, position = 'ACCEPT', 3
    elif board.player_3 == input['slave']:
        result, position = 'REJECT', 3
    elif not board.player_4:
        Board.query.filter_by(id=input['id']).update({'player_4':input['slave']})
        db.session.commit()
        result, position = 'ACCEPT', 4
    elif board.player_4 == input['slave']:
        result, position = 'REJECT', 4
    else:
        result, position = 'REJECT', 0

    output = {
        'result': result,
        'position': position,
    }
    return json.dumps(output)


@app.route('/board/start', methods=['POST'])
def do_board_start():
    input = {
        'id': int(request.form['id']),
    }
    board = Board.query.filter_by(id=input['id']).first()
    banker = board.number % 4
    circle_map = [
        ['player_1', 'player_2', 'player_3', 'player_4'],
        ['player_2', 'player_3', 'player_4', 'player_1'],
        ['player_3', 'player_4', 'player_2', 'player_1'],
        ['player_4', 'player_1', 'player_2', 'player_3'],
    ]
    circle = circle_map[banker]
    card_pile, discard_pile = shuffle()
    card_pile, player_tiles = deal(card_pile, circle)
    update_data = {
        'card_pile': ','.join(card_pile),
        'player_1_tiles': ','.join(player_tiles['player_1']),
        'player_2_tiles': ','.join(player_tiles['player_2']),
        'player_3_tiles': ','.join(player_tiles['player_3']),
        'player_4_tiles': ','.join(player_tiles['player_4']),
    }
    Board.query.filter_by(id=input['id']).update(update_data)
    db.session.commit()

    output = {
        'result': 'START',
    }
    return json.dumps(output)
