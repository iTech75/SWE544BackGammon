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

    def test_parse_backgammon_notation_3(self):
        game, black, white = self.create_test_game()

        game.set_game_status("0/0|1b2|24w4|13/11")

        game.parse_backgammon_notation("1/off,1/off", black)
        self.assertEqual(game.gameStatus[25].color, "15/11", "black must win!")

    def test_gameplay(self):
        game, black, white = self.create_test_game()

        game.parse_backgammon_notation("8/2,6/2", black)
        game.parse_backgammon_notation("24/13", white)
        game.parse_backgammon_notation("6/1*", black)
        game.parse_backgammon_notation("bar/24*,24/22", white)

        self.assertEqual(game.gameStatus[3].color, "w", "point 3 must be white")
        self.assertEqual(game.gameStatus[3].count, 1, "point 3 must be 1 checker")
