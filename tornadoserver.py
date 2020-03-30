import os
import json
import random
import string
import tornado.ioloop
import tornado.web

room_code = None
players = []
isRoomOpen = False

class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        #print "setting headers!!!"
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def options(self):
        # no body
        self.set_status(204)
        self.finish()

	def get(self):
		self.write("Welcome")

	def post(self):
		json_obj = json.loads(self.request.body)
		self.write(str(json_obj))

class RoomGenerationHandler(BaseHandler):
	def get(self):
		global room_code
		global players
		global isRoomOpen
		global player_list

		if not isRoomOpen:
			room_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(ROOM_CODE_LENGTH))
			players = {}
			player_list = []
			isRoomOpen = True

		print('Room ' + room_code + ' Created')
		self.write('The Room Code is: ' + str(room_code))

class JoinRoomHandler(BaseHandler):
	def post(self):
		global players

		print(self.request.body)
		json_obj = None
		if isRoomOpen:
			json_obj = json.loads(self.request.body)

			#test if room code is correct

			if json_obj['nickname'] not in players:
				players[json_obj['nickname']] = {}

				print(json_obj['nickname'] + " joined!")
				self.write('SUCCESS!')

				# redirect player
			else:
				self.write('Nickname ' + json_obj['nickname'] + ' is already taken.')

		self.write('Data: ' + str(json_obj))

class SubmitDeckHandler(BaseHandler):
	def post(self):
		global isRoomOpen
		global players

		if not isRoomOpen:
			self.write('Game is not in setup')
		else:
			json_obj = json.loads(self.request.body)

			players[json_obj['nickname']]['deck'] = json_obj['deck']

			print('Player ' + str(json_obj['nickname']) + " submitted deck: " + str(json_obj['deck']))

			self.write('Player ' + str(json_obj['nickname']) + " submitted deck: " + str(json_obj['deck']))

class StartGameHandler(BaseHandler):
	def get(self):
		global players
		global isRoomOpen
		global teams
		global current_player
		global current_team

		if len(players) > 3 and isRoomOpen:
			not_ready_players = []
			for key in players:
				if 'deck' not in players[key]:
					not_ready_players.append(key)

			if len(not_ready_players) > 0:
				self.write("Players not ready: " + str(not_ready_players))
			else:
				isRoomOpen = False

				player_list = players.keys()
				random.shuffle(player_list)

				teams = {0: {'members': [], 'score': 0, 'acquired_cards': []}, 1: {'members': [], 'score': 0, 'acquired_cards': []}}
				team = 0
				for i in range(0, len(player_list)):
					p = player_list[i]
					players[p]['team'] = team
					teams[team]['members'].append(p)
					team = ((team + 1) % 2)

				for key in teams:
					random.shuffle(teams[key]['members'])

				current_team = random.randint(0, len(teams) - 1)
				current_player = random.randint(0, len(teams[current_team]['members']) - 1)

				print('---------------------')
				print('Game Started')
				print('Teams: ' + str(teams))
				print('Current Player: ' + str(teams[current_team]['members'][current_player]))
				print('---------------------')

				for key in teams:
					self.write('Team ' + str(key) + ": " + str(teams[key]['members']))
				self.write('First Clue giver: ' + str(teams[current_team]['members'][current_player]))

		else:
			if len(players) <= 3:
				print('Cannot start game with less than 3 players')
				self.write('Game cannot be started with less than 3 players.')
			else:
				print('Game is not ready to start')
				self.write('There is no game ready to start.')

class ListCurrentPlayersHandler(BaseHandler):
	def get(self):
		global players

		player_list = players.keys()

		self.write(str(player_list))

class StartRoundHandler(BaseHandler):
	def get(self):
		global players
		global teams
		global deck

		deck = []

		print(players)
		for name in players:
			deck.extend(players[name]['deck'])

		cards_to_remove = []
		for i in range(0, len(deck)-1):
			for j in range(i+1, len(deck)):
				if deck[i]['title'] == deck[j]['title']:
					cards_to_remove.append(i)
					break

		print('Duplicated cards: ' + str([deck[i] for i in cards_to_remove]))

		for i in reversed(cards_to_remove):
			deck.pop(i)

		random.shuffle(deck)

		print('Deck Size: ' + str(len(deck)))

		print('Round Started!')
		self.write('Round Started!')

class EndRoundHandler(BaseHandler):
	def get(self):
		global teams

		for team in teams:
			teams[team]['score'] += len(teams[team]['acquired_cards'])
			print('Team ' + str(team) + " acquired: " + str(teams[team]['acquired_cards']))
			print('Team ' + str(team) + " current score: " + str(teams[team]['score']))

			teams[team]['acquired_cards'] = []

		print('End Round')
		self.write('End Round')

class StartTurnHandler(BaseHandler):
	def get(self):
		global current_player
		global current_team
		global teams
		global deck

		current_team = (current_team + 1) % (len(teams))
		if current_team == 0:
			current_player = (current_player + 1) % (len(teams[current_team]['members']))

		random.shuffle(deck)

		print("Next player is " + str(teams[current_team]['members'][current_player]))
		print("Cards left in the deck: " + str(len(deck)))
		self.write("Next player is " + str(teams[current_team]['members'][current_player]))

class EndTurnHandler(BaseHandler):
	def post(self):
		global teams
		global current_team
		global deck

		json_obj = json.loads(self.request.body)

		teams[current_team]['acquired_cards'].extend(json_obj['correct'])

		for card in json_obj['correct']:
			for deckcard in deck:
				if deckcard['title'] == card['title']:
					deck.remove(deckcard)
					break

		print('End Turn')
		self.write('End Turn')

class GameStateHandler(BaseHandler):
	def post(self):
		json_obj = json.loads(self.request.body)

		print(json_obj)

		self.write('Game State')

def make_app():
	file_root = os.path.dirname(__file__)

	return tornado.web.Application([
		(r"/", BaseHandler),
		(r"/generateroom", RoomGenerationHandler),
		(r"/joinroom", JoinRoomHandler),
		(r"/submitdeck", SubmitDeckHandler),
		(r"/startgame", StartGameHandler),
		(r"/listplayers", ListCurrentPlayersHandler),
		(r"/startround", StartRoundHandler),
		(r"/endround", EndRoundHandler),
		(r"/startturn", StartTurnHandler),
		(r"/endturn", EndTurnHandler),
		(r"/gamestate", GameStateHandler),
		(r"/(.*)", tornado.web.StaticFileHandler, {"path": file_root, "default_filename": "index.html"})
	])

if __name__ == "__main__":
	ROOM_CODE_LENGTH = 6
	NUMBER_OF_CARDS_PER_PLAYER = 7
	room_code = None
	players = {}
	isRoomOpen = False
	player_list = []
	teams = {}
	current_player = None
	current_team = None
	deck = []

	app = make_app()
	app.listen(8888)
	tornado.ioloop.IOLoop.current().start()