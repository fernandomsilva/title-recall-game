import os
import json
import random
import string
import tornado.ioloop
import tornado.web

room_code = None
players = []
isRoomOpen = False

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("Welcome")

	def post(self):
		json_obj = json.loads(self.request.body)
		self.write(str(json_obj))

class RoomGenerationHandler(tornado.web.RequestHandler):
	def get(self):
		global room_code
		global players
		global isRoomOpen

		if not isRoomOpen:
			room_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(ROOM_CODE_LENGTH))
			players = []
			isRoomOpen = True
		self.write('The Room Code is: ' + str(room_code))

class JoinRoomHandler(tornado.web.RequestHandler):
	def get(self):
		global players

		json_obj = None
		if isRoomOpen:
			json_obj = json.loads(self.request.body)

			if json_obj['nickname'] not in players:
				players[json_obj['nickname']] = {}

				self.write('SUCCESS!')

				# redirect player
			else:
				self.write('Nickname ' + json_obj['nickname'] + ' is already taken.')

		self.write('Data: ' + str(json_obj))

class StartGameHandler(tornado.web.RequestHandler):
	def get(self):
		global players
		global isRoomOpen

		if len(players) > 1 and isRoomOpen:
			isRoomOpen = False

			player_list = players.keys()
			random.shuffle(player_list)

			team = 0
			for i in range(0, len(player_list)):
				p = player_list[i]
				players[p]['team'] = team
				team = ((team + 1) % 2)

			starting_player = player_list[0]

		else:
			if len(players) <= 1:
				self.write('Game cannot be started with less than 2 players.')
			else:
				self.write('There is no game ready to start.')



def make_app():
	file_root = os.path.dirname(__file__)

	return tornado.web.Application([
		(r"/", MainHandler),
		(r"/generateroom", RoomGenerationHandler),
		(r"/joinroom", JoinRoomHandler),
		(r"/startgame", StartGameHandler),
		(r"/(.*)", tornado.web.StaticFileHandler, {"path": file_root, "default_filename": "index.html"})
	])

if __name__ == "__main__":
	ROOM_CODE_LENGTH = 6
	room_code = None
	players = {}
	isRoomOpen = False

	app = make_app()
	app.listen(8888)
	tornado.ioloop.IOLoop.current().start()