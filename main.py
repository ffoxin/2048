#!/usr/bin/env python
# -*- coding: utf-8 -*-

from curses import wrapper

from game.field import GameField


def main(scr):
    g = GameField(scr)
    while True:
        g.print()
        try:
            g.handle_keyboard()
        except GameField.NoChanges:
            continue
        try:
            # g.test()
            g.step()
        except GameField.EndGame:
            break


if __name__ == '__main__':
    wrapper(main)
    print('Game over')
