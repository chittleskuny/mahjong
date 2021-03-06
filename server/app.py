import json
import random

import mysql.connector

from collections import Counter

from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
CORS(app)
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
    banker = db.Column(db.Integer, default=0, nullable=False)
    turn = db.Column(db.Integer, default=0, nullable=False)
    player_1 = db.Column(db.String(11))
    player_2 = db.Column(db.String(11))
    player_3 = db.Column(db.String(11))
    player_4 = db.Column(db.String(11))
    player_1_tiles = db.Column(db.String(512))
    player_2_tiles = db.Column(db.String(512))
    player_3_tiles = db.Column(db.String(512))
    player_4_tiles = db.Column(db.String(512))
    player_1_fixed_tiles = db.Column(db.JSON)
    player_2_fixed_tiles = db.Column(db.JSON)
    player_3_fixed_tiles = db.Column(db.JSON)
    player_4_fixed_tiles = db.Column(db.JSON)
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


def deal(card_pile, banker):
    player_tiles = {}
    circle_map = [
        ['player_1', 'player_2', 'player_3', 'player_4'],
        ['player_2', 'player_3', 'player_4', 'player_1'],
        ['player_3', 'player_4', 'player_2', 'player_1'],
        ['player_4', 'player_1', 'player_2', 'player_3'],
    ]
    circle = circle_map[banker - 1]
    start = 0
    for player in circle:
        player_tiles[player] = card_pile[start:(start + 16)]
        player_tiles[player].sort()
        start = start + 16
    player_tiles[circle[0]].append(card_pile[start])
    card_pile = card_pile[(start + 1):]
    return card_pile, player_tiles


def flower(tiles):
    normals = []
    flowers = []
    for tile in tiles:
        type, rank = tile.split('_')
        if type in ('dot', 'bamboo', 'character'):
            normals.append(tile)
        else:
            flowers.append(tile)
    return normals, flowers


def check_333(mycursor, tiles):
    sql = "select combinations from mahjong.tiles_combinations_333 where tiles = '%s';" % tiles
    mycursor.execute(sql)
    combinations = mycursor.fetchall()
    print(combinations)
    if len(combinations) > 0:
        return True, combinations
    else:
        return False, None


def check_233(mycursor, tiles):
    sql = "select combinations from mahjong.tiles_combinations_233 where tiles = '%s';" % tiles

    mycursor.execute(sql)
    combinations = mycursor.fetchall()
    print(combinations)
    if len(combinations) > 0:
        return True, combinations
    else:
        return False, None


def check(player_tiles):
    collector = {
        'season': [], 'gentleman': [], 'wind': [], 'dragon': [],    # flowers
        'dot': [], 'bamboo': [], 'character': [],    # normals
    }

    joker_count = 0
    for tile in player_tiles:
        if tile == 'joker':
            joker_count = joker_count + 1
        else:
            type, rank = tile.split('_')
            collector[type].append(rank)

    mydb = mysql.connector.connect(host='localhost', port=3306, user='root', passwd='root', database='mahjong')
    mycursor = mydb.cursor()
    if joker_count == 0:
        r_dot, r_bamboo, r_character = len(collector['dot']) % 3, len(collector['bamboo']) % 3, len(collector['character']) % 3
        remainders = [str(r_dot), str(r_bamboo), str(r_character)]
        remainders.sort()
        if ''.join(remainders) != '002':
            return False

        f_dot, f_bamboo, f_character = False, False, False
        collector['dot'].sort()
        collector['bamboo'].sort()
        collector['character'].sort()
        t_dot, t_bamboo, t_character = ''.join(collector['dot']), ''.join(collector['bamboo']), ''.join(collector['character'])
        if r_dot == 0:
            f_dot, c_dot = check_333(mycursor, t_dot)
        else:
            f_dot, c_dot = check_233(mycursor, t_dot)
        if r_bamboo == 0:
            f_bamboo, c_bamboo = check_333(mycursor, t_bamboo)
        else:
            f_bamboo, c_bamboo = check_233(mycursor, t_bamboo)
        if r_character == 0:
            f_character, c_character = check_333(mycursor, t_character)
        else:
            f_character, c_character = check_233(mycursor, t_character)
        if f_dot and f_bamboo and f_character:
            return True
        else:
            return False
    else:
        return False


@app.route('/login', methods=['GET', 'POST'])
def do_login():
    input = {
        'id': int(request.form['id']),
    }
    output = {
        'board': 1,
    }
    print('[INPUT]  ' + str(input))
    print('[OUTPUT] ' + str(output))
    return json.dumps(output)


@app.route('/board', methods=['GET', 'POST'])
def do_board():
    input = {
        'id': int(request.form['id']),
        'player': request.form['player'] if 'player' in request.form else 0,
    }
    output = {}
    print('[INPUT]  ' + str(input))

    board = Board.query.filter_by(id=input['id']).first()
    if board:
        if board.card_pile:
            card_pile = board.card_pile.split(',')
            len_card_pile = len(card_pile)
        else:
            len_card_pile = None

        players = []
        player_fixed_tiles = {}
        player_played_tiles = {}
        my_tiles = []
        if board.player_1:
            players.append(board.player_1)
            player_fixed_tiles['player_1'] = json.loads(board.player_1_fixed_tiles) if board.player_1_fixed_tiles else {}
            player_played_tiles['player_1'] = board.player_1_played_tiles.split(',') if board.player_1_played_tiles else []
            if board.player_1 == input['player']:
                my_tiles = board.player_1_tiles.split(',')
            if board.player_2:
                players.append(board.player_2)
                player_fixed_tiles['player_2'] = json.loads(board.player_2_fixed_tiles) if board.player_2_fixed_tiles else {}
                player_played_tiles['player_2'] = board.player_2_played_tiles.split(',') if board.player_2_played_tiles else []
                if board.player_2 == input['player']:
                    my_tiles = board.player_2_tiles.split(',')
                if board.player_3:
                    players.append(board.player_3)
                    player_fixed_tiles['player_3'] = json.loads(board.player_3_fixed_tiles) if board.player_3_fixed_tiles else {}
                    player_played_tiles['player_3'] = board.player_3_played_tiles.split(',') if board.player_3_played_tiles else []
                    if board.player_3 == input['player']:
                        my_tiles = board.player_3_tiles.split(',')
                    if board.player_4:
                        players.append(board.player_4)
                        player_fixed_tiles['player_4'] = json.loads(board.player_4_fixed_tiles) if board.player_4_fixed_tiles else {}
                        player_played_tiles['player_4'] = board.player_4_played_tiles.split(',') if board.player_4_played_tiles else []
                        if board.player_4 == input['player']:
                            my_tiles = board.player_4_tiles.split(',')

        output = {
            'total': board.total,
            'number': board.number,
            'len_card_pile': len_card_pile,
            'banker': board.banker,
            'turn': board.turn,
            'players': players,
            'player_fixed_tiles': player_fixed_tiles,
            'player_played_tiles': player_played_tiles,
            'my_tiles': my_tiles,
        }

    print('[OUTPUT] ' + str(output))
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

    board = Board(
        total = input['total'],
        number = 0,
        banker = 0,
        turn = 0,
        player_1 = input['master'],
    )
    output['id'] = board.id

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
    banker = board.banker % 4 + 1 if board.banker else 1

    card_pile, discard_pile = shuffle()
    card_pile, player_tiles = deal(card_pile, banker)
    update_data = {
        'number': board.number + 1,
        'card_pile': ','.join(card_pile),
        'discard_pile': None,
        'banker': banker,
        'turn': banker,
        'player_1_tiles': ','.join(player_tiles['player_1']),
        'player_2_tiles': ','.join(player_tiles['player_2']),
        'player_3_tiles': ','.join(player_tiles['player_3']),
        'player_4_tiles': ','.join(player_tiles['player_4']),
        'player_1_fixed_tiles': json.dumps({}),
        'player_2_fixed_tiles': json.dumps({}),
        'player_3_fixed_tiles': json.dumps({}),
        'player_4_fixed_tiles': json.dumps({}),
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

    card_pile, discard_pile = shuffle()
    card_pile, player_tiles = deal(card_pile, board.banker)
    init_fixed_tiles = { 'flower': [], 'pong': [], 'exposed_kong': [], 'concealed_kong': [], 'chow': [], }
    update_data = {
        'number': board.number,
        'card_pile': ','.join(card_pile),
        'discard_pile': None,
        'turn': board.banker,
        'player_1_tiles': ','.join(player_tiles['player_1']),
        'player_2_tiles': ','.join(player_tiles['player_2']),
        'player_3_tiles': ','.join(player_tiles['player_3']),
        'player_4_tiles': ','.join(player_tiles['player_4']),
        'player_1_fixed_tiles': json.dumps(init_fixed_tiles),
        'player_2_fixed_tiles': json.dumps(init_fixed_tiles),
        'player_3_fixed_tiles': json.dumps(init_fixed_tiles),
        'player_4_fixed_tiles': json.dumps(init_fixed_tiles),
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

    position = None
    for i in range(1, 5):
        if getattr(board, 'player_%s' % i) == input['player']:
            position = i
            break
    else:
        output['result'] = 'NO SUCH PLAYER'


    if position:
        player_tiles = getattr(board, 'player_%s_tiles' % position).split(',')
        if input['tile'] in player_tiles:
            player_tiles.remove(input['tile'])
            player_played_tiles = getattr(board, 'player_%s_played_tiles' % position).split(',') if getattr(board, 'player_%s_played_tiles' % position) else []
            player_played_tiles.append(input['tile'])
            discard_pile = board.discard_pile.split(',') if board.discard_pile else []
            discard_pile.append(input['tile'])
            update_data = {
                'player_%s_tiles' % position: ','.join(player_tiles),
                'player_%s_played_tiles' % position: ','.join(player_played_tiles),
                'discard_pile': ','.join(discard_pile),
            }
            Board.query.filter_by(id=input['id']).update(update_data)
            db.session.commit()
        else:
            output['result'] = 'NO SUCH TILE'

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

    position = None
    for i in range(1, 5):
        if getattr(board, 'player_%s' % i) == input['player']:
            position = i
            break
    else:
        output['result'] = 'NO SUCH PLAYER'

    if position:
        card_pile = board.card_pile.split(',') if board.card_pile else []

        player_tiles = getattr(board, 'player_%s_tiles' % position).split(',')
        player_fixed_tiles = json.loads(getattr(board, 'player_%s_fixed_tiles' % position))

        normals, flowers = flower(player_tiles)
        if flowers:
            player_tiles = normals
            for f in flowers:
                player_fixed_tiles['flower'].append(f)
                output['tile'] = card_pile.pop()
                player_tiles.append(output['tile'])
        else:
            output['tile'] = card_pile.pop()
            player_tiles.append(output['tile'])
        player_tiles.sort()
        player_fixed_tiles['flower'].sort()

        update_data = {
            'player_%s_tiles' % position: ','.join(player_tiles),
            'player_%s_fixed_tiles' % position: json.dumps(player_fixed_tiles),
            'card_pile': ','.join(card_pile),
        }
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
        'result': False,
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
        output['result'] = check(player_tiles)

    return json.dumps(output)


@app.route('/board/pong', methods=['POST'])
def do_board_pong():
    input = {
        'id': int(request.form['id']),
        'player': request.form['player'],
    }
    output = {
        'result': 'PONG',
    }

    board = Board.query.filter_by(id=input['id']).first()
    position = None

    if board.player_1 == input['player']:
        position = 1
        player_tiles = board.player_1_tiles.split(',')
        player_fixed_tiles = board.player_1_fixed_tiles
    elif board.player_2 == input['player']:
        position = 2
        player_tiles = board.player_2_tiles.split(',')
        player_fixed_tiles = board.player_2_fixed_tiles
    elif board.player_3 == input['player']:
        position = 3
        player_tiles = board.player_3_tiles.split(',')
        player_fixed_tiles = board.player_3_fixed_tiles
    elif board.player_4 == input['player']:
        position = 4
        player_tiles = board.player_4_tiles.split(',')
        player_fixed_tiles = board.player_4_fixed_tiles
    else:
        pass

    if position:
        discard_pile = board.discard_pile.split(',')
        last = discard_pile.pop()
        player_tiles.append(last)

        update_data = {
            'turn': position,
            'discard_pile': ','.join(discard_pile),
            'player_%d_tiles' % position: ','.join(player_tiles),
        }
        Board.query.filter_by(id=input['id']).update(update_data)
        db.session.commit()

    return json.dumps(output)


@app.route('/board/kong', methods=['POST'])
def do_board_kong():
    input = {
        'id': int(request.form['id']),
        'player': request.form['player'],
    }
    output = {
        'result': 'KONG',
    }

    board = Board.query.filter_by(id=input['id']).first()
    position = None

    if board.player_1 == input['player']:
        position = 1
        player_tiles = board.player_1_tiles.split(',')
        player_fixed_tiles = board.player_1_fixed_tiles
    elif board.player_2 == input['player']:
        position = 2
        player_tiles = board.player_2_tiles.split(',')
        player_fixed_tiles = board.player_2_fixed_tiles
    elif board.player_3 == input['player']:
        position = 3
        player_tiles = board.player_3_tiles.split(',')
        player_fixed_tiles = board.player_3_fixed_tiles
    elif board.player_4 == input['player']:
        position = 4
        player_tiles = board.player_4_tiles.split(',')
        player_fixed_tiles = board.player_4_fixed_tiles
    else:
        pass

    if position:
        if position != board.turn:    # 'exposed'
            discard_pile = board.discard_pile.split(',')
            last = discard_pile.pop()
            player_tiles.remove(last)
            player_tiles.remove(last)
            player_tiles.remove(last)
            kong = [last, last, last, last]
            player_fixed_tiles['exposed_kong'].append(kong)

            update_data = {
                'turn': position,
                'discard_pile': ','.join(discard_pile),
                'player_%d_tiles' % position: ','.join(player_tiles),
                'player_%d_fixed_tiles' % position: player_fixed_tiles,
            }

        else:    # 'concealed'
            player_tiles_counter = dict(Counter(player_tiles))
            kong_candicates = []
            for tile, count in player_tiles_counter.items():
                if count == 4:
                    kong_candicates.append(count)
            # TODO -1
            player_tiles.remove(kong_candicates[0])
            player_tiles.remove(kong_candicates[0])
            player_tiles.remove(kong_candicates[0])
            player_tiles.remove(kong_candicates[0])
            kong = [kong_candicates[0], kong_candicates[0], kong_candicates[0], kong_candicates[0]]
            player_fixed_tiles['exposed_kong'].append(kong)

            update_data = {
                'turn': position,
                'discard_pile': ','.join(discard_pile),
                'player_%d_tiles' % position: ','.join(player_tiles),
                'player_%d_fixed_tiles' % position: player_fixed_tiles,
            }

        Board.query.filter_by(id=input['id']).update(update_data)
        db.session.commit()

    return json.dumps(output)


@app.route('/board/chow', methods=['POST'])
def do_board_chow():
    input = {
        'id': int(request.form['id']),
        'player': request.form['player'],
    }
    output = {
        'result': 'CHEW',
    }

    board = Board.query.filter_by(id=input['id']).first()
    position = None

    if board.player_1 == input['player']:
        position = 1
        player_tiles = board.player_1_tiles.split(',')
        player_fixed_tiles = board.player_1_fixed_tiles
    elif board.player_2 == input['player']:
        position = 2
        player_tiles = board.player_2_tiles.split(',')
        player_fixed_tiles = board.player_2_fixed_tiles
    elif board.player_3 == input['player']:
        position = 3
        player_tiles = board.player_3_tiles.split(',')
        player_fixed_tiles = board.player_3_fixed_tiles
    elif board.player_4 == input['player']:
        position = 4
        player_tiles = board.player_4_tiles.split(',')
        player_fixed_tiles = board.player_4_fixed_tiles
    else:
        pass

    if position:
        discard_pile = board.discard_pile.split(',')
        last = discard_pile.pop()
        player_tiles.append(last)

        # TODO

        update_data = {
            'turn': position,
            'discard_pile': ','.join(discard_pile),
            'player_%d_tiles' % position: ','.join(player_tiles),
        }
        Board.query.filter_by(id=input['id']).update(update_data)
        db.session.commit()

    return json.dumps(output)
