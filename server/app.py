import json
import random
from collections import Counter

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


def check_meld(meld_0, meld_1, meld_2, meld_3=None):
    if (meld_0 == meld_1 and meld_1 == meld_2) or (meld_0 == meld_1 -1 and meld_1 == meld_2 - 1):
        return True
    else:
        return False


def check_type_ranks(pair, type, ranks, joker_count=0):
    # delete pair
    if type in ('season', 'gentleman'):
        return True, joker_count
    elif type in ('wind', 'dragon'):
        return True, joker_count
    else:
        while ranks and len(ranks) >= 3:
            meld_0 = int(ranks.pop())
            meld_1 = int(ranks.pop())
            meld_2 = int(ranks.pop())
            if check_meld(meld_0, meld_1, meld_2):
                continue
            elif joker_count > 0:
                joker_count = joker_count - 1
            else:
                return False, joker_count
        return True, joker_count


def check_win_with_pair(pair, collector, joker_count):
    for type, ranks in collector.items():
        result, joker_count = check_type_ranks(pair, type, ranks, joker_count)
        if result or joker_count > 0:
            continue
        else:
            return False
    return True


def check_win_with_pair_candicates(pair_candicates, collector, joker_count):
    for pair in pair_candicates:
        if pair[0] == 'joker' and pair[1] == 'joker':
            local_joker_count = joker_count - 2
            # delele none
            if check_win_with_pair(pair, collector, joker_count):
                return True
        elif pair[0] == 'joker' or pair[1] == 'joker':
            local_joker_count = joker_count - 1
            # delete one
            if check_win_with_pair(pair, collector, joker_count):
                return True
        else:
            local_joker_count = joker_count - 0
            # delete two
            if check_win_with_pair(pair, collector, joker_count):
                return True


def check_win(player_tiles):
    collector = {
        'season': [],
        'gentleman': [],
        'wind': [],
        'dragon': [],
        'dot': [],
        'bamboo': [],
        'character': [],
    }

    joker_count = 0
    for tile in player_tiles:
        if tile == 'joker':
            joker_count = joker_count + 1
        else:
            type, rank = tile.split('_')
            collector[type].append(rank)

    pair_candicates = []
    for type, ranks in collector.items():
        rank_counter = dict(Counter(ranks))
        for rank, count in rank_counter.items():
            if count >= 2:
                pair_candicates.append(['%s_%s' % (type, rank), '%s_%s' % (type, rank)])
        ranks.sort()
        ranks.reverse()

    return check_win_with_pair_candicates(pair_candicates, collector, joker_count)


@app.route('/')
def hello_mahjong():
    return 'Hello, Mahjong!'


@app.route('/board', methods=['GET', 'POST'])
def do_board():
    input = {
        'id': int(request.form['id']),
    }
    output = {}
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

    return json.dumps(output)


@app.route('/board/init', methods=['POST'])
def do_board_init():
    input = {
        'total': int(request.form['total']),
        'master': request.form['master'],
    }
    output = {
        'id': None,
    }

    board = Board(total=input['total'], number=0, player_1=player_1.id)
    output['id'] = board.id

    player_1 = Player.query.filter_by(id=input['master']).first()
    db.session.add(board)
    db.session.commit()

    return json.dumps(output)


@app.route('/board/join', methods=['POST'])
def do_board_join():
    input = {
        'id': int(request.form['id']),
        'slave': request.form['slave'],
    }
    output = {
        'result': None,
        'position': None,
    }

    board = Board.query.filter_by(id=input['id']).first()

    if board.player_1 == input['slave']:
        output['result'], output['position'] = 'REJECT', 1
    elif not board.player_2:
        Board.query.filter_by(id=input['id']).update({'player_2': input['slave']})
        db.session.commit()
        output['result'], output['position'] = 'ACCEPT', 2
    elif board.player_2 == input['slave']:
        output['result'], output['position'] = 'REJECT', 2
    elif not board.player_3:
        Board.query.filter_by(id=input['id']).update({'player_3': input['slave']})
        db.session.commit()
        output['result'], output['position'] = 'ACCEPT', 3
    elif board.player_3 == input['slave']:
        output['result'], output['position'] = 'REJECT', 3
    elif not board.player_4:
        Board.query.filter_by(id=input['id']).update({'player_4': input['slave']})
        db.session.commit()
        output['result'], output['position'] = 'ACCEPT', 4
    elif board.player_4 == input['slave']:
        output['result'], output['position'] = 'REJECT', 4
    else:
        output['result'], output['position'] = 'REJECT', 0

    return json.dumps(output)


@app.route('/board/start', methods=['POST'])
def do_board_start():
    input = {
        'id': int(request.form['id']),
    }
    output = {
        'result': 'START',
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
        'number': board.number + 1,
        'card_pile': ','.join(card_pile),
        'discard_pile': None,
        'player_1_tiles': ','.join(player_tiles['player_1']),
        'player_2_tiles': ','.join(player_tiles['player_2']),
        'player_3_tiles': ','.join(player_tiles['player_3']),
        'player_4_tiles': ','.join(player_tiles['player_4']),
        'player_1_played_tiles': None,
        'player_2_played_tiles': None,
        'player_3_played_tiles': None,
        'player_4_played_tiles': None,
    }
    Board.query.filter_by(id=input['id']).update(update_data)
    db.session.commit()

    return json.dumps(output)


@app.route('/board/restart', methods=['POST'])
def do_board_restart():
    input = {
        'id': int(request.form['id']),
    }
    output = {
        'result': 'RESTART',
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
        'number': board.number,
        'card_pile': ','.join(card_pile),
        'discard_pile': None,
        'player_1_tiles': ','.join(player_tiles['player_1']),
        'player_2_tiles': ','.join(player_tiles['player_2']),
        'player_3_tiles': ','.join(player_tiles['player_3']),
        'player_4_tiles': ','.join(player_tiles['player_4']),
        'player_1_played_tiles': None,
        'player_2_played_tiles': None,
        'player_3_played_tiles': None,
        'player_4_played_tiles': None,
    }
    Board.query.filter_by(id=input['id']).update(update_data)
    db.session.commit()

    return json.dumps(output)


@app.route('/board/play', methods=['POST'])
def do_board_play():
    input = {
        'id': int(request.form['id']),
        'player': request.form['player'],
        'tile': request.form['tile'],
    }
    output = {
        'result': 'PLAYED',
    }
    board = Board.query.filter_by(id=input['id']).first()
    discard_pile = board.discard_pile.split(',') if board.discard_pile else []

    update_data = None
    if board.player_1 == input['player']:
        player_tiles = board.player_1_tiles.split(',')
        player_played_tiles = board.player_1_played_tiles.split(',') if board.player_1_played_tiles else []
        if input['tile'] in player_tiles:
            player_tiles.remove(input['tile'])
            player_played_tiles.append(input['tile'])
            discard_pile.append(input['tile'])
            update_data = {
                'player_1_tiles': ','.join(player_tiles),
                'player_1_played_tiles': ','.join(player_played_tiles),
                'discard_pile': ','.join(discard_pile),
            }
        else:
            output['result'] = 'NO SUCH TILE'
    elif board.player_2 == input['player']:
        player_tiles = board.player_2_tiles.split(',')
        player_played_tiles = board.player_2_played_tiles.split(',') if board.player_2_played_tiles else []
        if input['tile'] in player_tiles:
            player_tiles.remove(input['tile'])
            player_played_tiles.append(input['tile'])
            discard_pile.append(input['tile'])
            update_data = {
                'player_2_tiles': ','.join(player_tiles),
                'player_2_played_tiles': ','.join(player_played_tiles),
                'discard_pile': ','.join(discard_pile),
            }
        else:
            output['result'] = 'NO SUCH TILE'
    elif board.player_3 == input['player']:
        player_tiles = board.player_3_tiles.split(',')
        player_played_tiles = board.player_3_played_tiles.split(',') if board.player_3_played_tiles else []
        if input['tile'] in player_tiles:
            player_tiles.remove(input['tile'])
            player_played_tiles.append(input['tile'])
            discard_pile.append(input['tile'])
            update_data = {
                'player_3_tiles': ','.join(player_tiles),
                'player_3_played_tiles': ','.join(player_played_tiles),
                'discard_pile': ','.join(discard_pile),
            }
        else:
            output['result'] = 'NO SUCH TILE'
    elif board.player_4 == input['player']:
        player_tiles = board.player_4_tiles.split(',')
        player_played_tiles = board.player_4_played_tiles.split(',') if board.player_4_played_tiles else []
        if input['tile'] in player_tiles:
            player_tiles.remove(input['tile'])
            player_played_tiles.append(input['tile'])
            discard_pile.append(input['tile'])
            update_data = {
                'player_4_tiles': ','.join(player_tiles),
                'player_4_played_tiles': ','.join(player_played_tiles),
                'discard_pile': ','.join(discard_pile),
            }
        else:
            output['result'] = 'NO SUCH TILE'
    else:
        output['result'] = 'NO SUCH PLAYER'

    if update_data:
        Board.query.filter_by(id=input['id']).update(update_data)
        db.session.commit()

    return json.dumps(output)


@app.route('/board/draw', methods=['POST'])
def do_board_draw():
    input = {
        'id': int(request.form['id']),
        'player': request.form['player'],
    }
    output = {
        'result': 'DREW',
        'tile': None,
    }

    board = Board.query.filter_by(id=input['id']).first()
    card_pile = board.card_pile.split(',') if board.card_pile else []

    update_data = None
    if board.player_1 == input['player']:
        player_tiles = board.player_1_tiles.split(',')
        output['tile'] = card_pile.pop()
        player_tiles.append(output['tile'])
        update_data = {
            'player_1_tiles': ','.join(player_tiles),
            'card_pile': ','.join(card_pile),
        }
    elif board.player_2 == input['player']:
        player_tiles = board.player_2_tiles.split(',')
        output['tile'] = card_pile.pop()
        player_tiles.append(output['tile'])
        update_data = {
            'player_2_tiles': ','.join(player_tiles),
            'card_pile': ','.join(card_pile),
        }
    elif board.player_3 == input['player']:
        player_tiles = board.player_3_tiles.split(',')
        output['tile'] = card_pile.pop()
        player_tiles.append(output['tile'])
        update_data = {
            'player_3_tiles': ','.join(player_tiles),
            'card_pile': ','.join(card_pile),
        }
    elif board.player_4 == input['player']:
        player_tiles = board.player_4_tiles.split(',')
        output['tile'] = card_pile.pop()
        player_tiles.append(output['tile'])
        update_data = {
            'player_4_tiles': ','.join(player_tiles),
            'card_pile': ','.join(card_pile),
        }
    else:
        output['result'] = 'NO SUCH PLAYER'

    if update_data:
        Board.query.filter_by(id=input['id']).update(update_data)
        db.session.commit()

    return json.dumps(output)

@app.route('/board/win', methods=['POST'])
def do_board_win():
    input = {
        'id': int(request.form['id']),
        'player': request.form['player'],
    }
    output = {
        'result': 'WIN',
    }

    board = Board.query.filter_by(id=input['id']).first()

    if board.player_1 == input['player']:
        player_tiles = board.player_1_tiles.split(',')
    elif board.player_2 == input['player']:
        player_tiles = board.player_2_tiles.split(',')
    elif board.player_3 == input['player']:
        player_tiles = board.player_3_tiles.split(',')
    elif board.player_4 == input['player']:
        player_tiles = board.player_4_tiles.split(',')
    else:
        output['result'] = 'NO SUCH PLAYER'

    if player_tiles:
        output['result'] = check_win(player_tiles)

    return json.dumps(output)
