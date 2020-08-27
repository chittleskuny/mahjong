import time
import logging

import mysql.connector

from itertools import combinations, permutations
from collections import Counter


time_str = time.strftime('%Y%m%d_%H%M%S', time.localtime())

logger = logging.getLogger()
format = '%(asctime)s %(levelname)s %(filename)s[%(lineno)d] %(message)s'
logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
sh.setFormatter(logging.Formatter(format))
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)

fh = logging.FileHandler('%s.log' % time_str)
fh.setFormatter(logging.Formatter(format))
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


def combine(rest):
    to_return = []
    if len(rest) == 3:
        to_return.append([tuple(rest)])
    else:
        s = set(combinations(rest, 3))
        for i_s in s:
            meld_0, meld_1, meld_2 = int(i_s[0]), int(i_s[1]), int(i_s[2])
            rest_copy = rest.copy()
            rest_copy.remove(i_s[0])
            rest_copy.remove(i_s[1])
            rest_copy.remove(i_s[2])
            s_rest = combine(rest_copy)
            for i_s_rest in s_rest:
                first_meld = i_s_rest[0]
                rest_meld_0, rest_meld_1, rest_meld_2 = int(first_meld[0]), int(first_meld[1]), int(first_meld[2])
                if (meld_0 > rest_meld_0) \
                        or (meld_0 == rest_meld_0 and meld_1 > rest_meld_1) \
                        or (meld_0 == rest_meld_0 and meld_1 == rest_meld_1 and meld_2 > rest_meld_2):
                    continue
                to_return.append([i_s] + i_s_rest)
    return to_return


def check_333(melds):
    for meld in melds:
        meld_0, meld_1, meld_2 = int(meld[0]), int(meld[1]), int(meld[2])
        delta_01 = meld_1 - meld_0
        delta_12 = meld_2 - meld_1
        if delta_01 != delta_12 or delta_01 > 1:
            return False
    return True


def do_tiles_win_333():
    mydb = mysql.connector.connect(host="localhost", port=3306, user="root", passwd="root", database="mahjong")
    mycursor = mydb.cursor()

    sql = "select tiles from mahjong.tiles_win_333 where length(tiles) = 12;"
    logging.debug(sql)
    mycursor.execute(sql)

    all_tiles = mycursor.fetchall()
    for tiles in all_tiles:
        tiles_str = tiles[0]
        tiles_list = list(tiles_str)
        c = combine(tiles_list)
        for m in c:
            m_str_list = []
            for i_m in m:
                m_str_list.append(''.join(i_m))
            m_str = ','.join(m_str_list)
            if check_333(m):
                logging.debug(tiles_str + ' + ' + m_str)
                sql = "update mahjong.tiles_win_333 set win = 1 where tiles = '%s';" % tiles_str
                mycursor.execute(sql)
                sql = "insert into mahjong.tiles_win_combinations_333(tiles, combinations) values ('%s', '%s');" % (tiles_str, m_str)
                mycursor.execute(sql)
                mydb.commit()
            else:
                logging.debug(tiles_str + ' - ' + m_str)


def generate_all_list():
    all_list = []
    cur_dict = {}
    for i_1 in range(5):
        cur_dict['1'] = []
        for j_1 in range(i_1):
            cur_dict['1'].append(1)
        for i_2 in range(5):
            cur_dict['2'] = []
            for j_2 in range(i_2):
                cur_dict['2'].append(2)
            for i_3 in range(5):
                cur_dict['3'] = []
                for j_3 in range(i_3):
                    cur_dict['3'].append(3)
                for i_4 in range(5):
                    cur_dict['4'] = []
                    for j_4 in range(i_4):
                        cur_dict['4'].append(4)
                    for i_5 in range(5):
                        cur_dict['5'] = []
                        for j_5 in range(i_5):
                            cur_dict['5'].append(5)
                        for i_6 in range(5):
                            cur_dict['6'] = []
                            for j_6 in range(i_6):
                                cur_dict['6'].append(6)
                            for i_7 in range(5):
                                cur_dict['7'] = []
                                for j_7 in range(i_7):
                                    cur_dict['7'].append(7)
                                for i_8 in range(5):
                                    cur_dict['8'] = []
                                    for j_8 in range(i_8):
                                        cur_dict['8'].append(8)
                                    for i_9 in range(5):
                                        cur_dict['9'] = []
                                        for j_9 in range(i_9):
                                            cur_dict['9'].append(9)

                                        cur_list = cur_dict['1'] + cur_dict['2'] + cur_dict['3'] + cur_dict['4'] + cur_dict['5'] + cur_dict['6'] + cur_dict['7'] + cur_dict['8'] + cur_dict['9']
                                        # logging.debug(cur_list)

                                        if 1 <= len(cur_list) and len(cur_list) <= 32:
                                            all_list.append(cur_list)

    all_list.sort()
    print(len(all_list))

    mydb = mysql.connector.connect(host='localhost', port=3306, user='root', passwd='root', database='mahjong')
    mycursor = mydb.cursor()

    for cur_list in all_list:
        # logging.debug(cur_list)
        value = ''.join(list(map(str, cur_list)))
        # logging.debug(value)
        if len(cur_list) % 3 == 2:
            pass
        elif len(cur_list) % 3 == 1:
            pass
        else:
            table = 'tiles_win_333'
            sql = "insert into %s(tiles) values ('%s');" % (table, value)
            logging.debug(sql)
            mycursor.execute(sql)

    mydb.commit()


if __name__ == '__main__':
    start = time.time()

    # generate_all_list()
    do_tiles_win_333()

    stop = time.time()
    print(stop - start)
