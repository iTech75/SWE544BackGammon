from unittest import TestCase
import BGGame
import BGServer
import Player
import socket

__author__ = 'Tekin'


class TestBGGame(TestCase):
    def create_test_game(self):
        bgserver = BGServer.BGServer()
        black = Player.Player(bgserver, socket.socket(), ())
        white = Player.Player(bgserver, socket.socket(), ())
        game = BGGame.BGGame(bgserver, black, white)
        game.initilize()
        return game, black, white

    def test_parse_backgammon_notation(self):
        game, black, white = self.create_test_game()

        game.parse_backgammon_notation("8/7,6/5", black)
        game.parse_backgammon_notation("24/20*,24/20", white)

        self.assertEqual(game.gameStatus[7].count, 1, "point 7 count must be 1")
        self.assertEqual(game.gameStatus[0].color, "1/0", "bar must be 1/0")

    def test_create_game_status_string(self):
        game, black, white = self.create_test_game()
        game.parse_backgammon_notation("8/7,6/5", black)
        game.parse_backgammon_notation("24/20*,24/20", white)
        status = game.create_game_status_string()

        self.assertEqual(status, "1/0|5w2|6b4|7b1|8b2|12w5|13b5|17w3|19w5|24b2|0/0", "status string is wrong!")

    def test_parse_backgammon_notation_2(self):
        game, black, white = self.create_test_game()

        game.parse_backgammon_notation("8/5,6/5", black)
        game.parse_backgammon_notation("24/21,24/22", white)
        game.parse_backgammon_notation("8/4*,6/4", black)

        self.assertEqual(game.gameStatus[0].color, "0/1", "white bar must be 1")
        game.parse_backgammon_notation("bar/3,4/9", white)

        self.assertEqual(game.gameStatus[3].count, 1, "point 3 count must be 1 white")
        self.assertEqual(game.gameStatus[3].color, "w", "point 3 count must be 1 white")

        game.parse_backgammon_notation("", black)  # pass test

    def test_parse_backgammon_notation_3(self):
        game, black, white = self.create_test_game()

        game.set_game_status("0/0|1b2|24w4|13/11")

        game.parse_backgammon_notation("1/off,1/off", black)
        self.assertEqual(game.gameStatus[25].color, "15/11", "black must win!")
