# -*- coding: utf-8 -*-
from datetime import datetime

import os
import curses


class GameField:
    class GameException(Exception):
        pass

    class EndGame(GameException):
        pass

    class NoChanges(GameException):
        pass

    def __init__(self, scr):
        full_height, full_width = scr.getmaxyx()
        height = 9
        width = 21
        top = (full_height - height) // 2
        left = (full_width - width) // 2

        self.scr = scr.subwin(height, width, top, left)
        self.dbg = scr.subpad(full_height, left, 0, 0)
        self.dbg.scrollok(1)

        self.height, self.width = self.scr.getmaxyx()
        self.data = [0] * 16

    def dprint(self, string):
        ts = datetime.now().time()
        self.dbg.addstr('[{}] {}\n'.format(ts, string))

    @staticmethod
    def __num_to_str(number):
        if number == 0:
            return ' ' * 4
        else:
            if number < 10:
                return '  {} '.format(number)
            elif number < 100:
                return ' {} '.format(number)
            elif number < 1000:
                return ' {}'.format(number)
            else:
                return '{}'.format(number)

    def print(self):
        self.scr.clear()
        self.scr.border()

        for i in range(2, self.height - 1, 2):
            self.scr.addch(i, 0, curses.ACS_LTEE)
            self.scr.addch(i, self.width - 1, curses.ACS_RTEE)
            self.scr.hline(i, 1, curses.ACS_HLINE, self.width - 2)

        for i in range(5, self.width - 1, 5):
            self.scr.addch(0, i, curses.ACS_TTEE)
            self.scr.addch(self.height - 1, i, curses.ACS_BTEE)
            self.scr.vline(1, i, curses.ACS_VLINE, self.height - 2)
            for k in range(2, self.height - 1, 2):
                self.scr.addch(k, i, curses.ACS_SSSS)

        for i in range(16):
            ypos = (i // 4) * 2 + 1
            xpos = (i % 4) * 5 + 1
            # self.dprint('Print {}:{} - {}'.format(ypos, xpos, self.data[i]))
            self.scr.addstr(ypos, xpos, '{}'.format(self.__num_to_str(self.data[i])))

        self.scr.refresh()
        self.dbg.refresh()

    def __rotate(self, deg):
        if deg % 90 != 0:
            return
        rotate_count = deg // 90
        for i in range(rotate_count):
            data = [0] * 16
            for row in range(4):
                for col in range(4):
                    data[row * 4 + col] = self.data[(3 - col) * 4 + row]
            self.data = data

    def __sum_up(self):
        self.__squash_up()

        for col in range(4):
            for row in range(3, 0, -1):
                current = row * 4 + col
                upper = current - 4
                if self.data[current] == self.data[upper]:
                    self.data[upper] *= 2
                    self.data[current] = 0
                    for i in range(row, 3):
                        current = i * 4 + col
                        self.data[current] = self.data[current + 4]
                    self.data[12 + col] = 0

    def __squash_up(self):
        for col in range(4):
            for s_up in range(3):
                for row in range(3):
                    upper = row * 4 + col
                    current = upper + 4
                    if self.data[upper] == 0 and self.data[current] != 0:
                        self.data[upper] = self.data[current]
                        self.data[current] = 0

    def __read_key(self):
        ch = self.scr.getch()
        if ch != 27:
            return
        ch = self.scr.getch()
        if ch != 91:
            return

        return self.scr.getch()

    def handle_keyboard(self):
        ch = self.__read_key()
        data = self.data
        self.__process_board(ch)
        if any(data) and data == self.data:
            raise self.NoChanges()

    def test(self):
        self.data[0] = 2
        self.data[1] = 2
        self.data[2] = 2
        self.data[3] = 2
        self.print()
        self.__read_key()

        self.__test_step(65)
        self.__test_step(66)
        self.__test_step(65)
        self.__test_step(67)
        self.__test_step(68)

        raise self.EndGame()

    def __test_step(self, key):
        self.__process_board(key)
        self.print()
        self.__read_key()

    def __process_board(self, ch):
        if ch == 65:
            self.dprint('Key UP')
            self.__sum_up()
        elif ch == 66:
            self.dprint('Key DOWN')
            self.__rotate(180)
            self.__sum_up()
            self.__rotate(180)
        elif ch == 67:
            self.dprint('Key RIGHT')
            self.__rotate(270)
            self.__sum_up()
            self.__rotate(90)
        elif ch == 68:
            self.dprint('Key LEFT')
            self.__rotate(90)
            self.__sum_up()
            self.__rotate(270)

    @staticmethod
    def __get_random():
        return os.urandom(1)[0] % 16

    def __get_next_cell(self):
        if all(self.data):
            raise self.EndGame()

        steps = self.__get_random()
        self.dprint('Randomed {}'.format(steps))
        next_cell = 0
        while True:
            if self.data[next_cell] == 0:
                if steps == 0:
                    return next_cell
                steps -= 1

            next_cell += 1
            next_cell %= 16

    def step(self):
        next_cell = self.__get_next_cell()
        self.data[next_cell] = 2
