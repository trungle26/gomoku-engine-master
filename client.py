import threading
import requests

class GameClient:
    def __init__(self, team_id):
        self.initialized = False
        self.team_id = team_id  # id team minh
        self.match_id = None  # id cua tran dau hien tai
        self.board = None  # trang thai ban co
        self.turn = None  # id cua team den luot di
        self.score1 = 0  # score team 1
        self.score2 = 0  # score team 2
        self.status = None  # trang thai tran dau (None, draw, or win)
        self.referee_url = "http://server-cua-thay.com"  # dia chi server
        self.init_thread = None  # thread for initialization stage
        self.play_thread = None  # thread for game playing stage

    def init_game(self):
        # send a request to initialize a new game and get a match id
        data = {
            "room_id": "",
            "init": True,
        }
        response = requests.post(self.referee_url, data=data)
        if response.status_code == 200:
            json_data = response.json()
            self.match_id = json_data["match_id"]
            print(f"Game dc khoi tao voi match id {self.match_id}")
            self.initialized = True

    def update_game(self):
        # send a request to get the latest game state from the referee server
        data = {
            "match_id": self.match_id,
            "team_id": self.team_id
        }
        response = requests.post(self.referee_url, data=data)
        if response.status_code == 200:
            json_data = response.json()
            self.board = json_data["board"]
            self.turn = json_data["turn"]
            self.score1 = json_data["score1"]
            self.score2 = json_data["score2"]
            self.status = json_data["status"]

    def make_move(self):
        # ham xu ly buoc di thuc hien o day
        move = AI_function(self.board)
        return move

    def send_move(self):
        # gui buoc di
        move = self.make_move()
        data = {
            "match_id": self.match_id,
            "board": move
        }
        response = requests.post(self.referee_url, data=data)
        if response.status_code == 200:
            print(f"Move sent successfully: {move}")

    def init_game_thread(self):
        try:
            while not self.match_id:
                # tao game lan dau
                print("Initializing game...")
                self.init_game()
        except Exception as e:
            print(f"Error in initialization stage: {e}")
        
    def play_game_thread(self):
        try:
            game_finished = False
            while game_finished == False:
                if not (self.status and (self.status != 'None')):
                    # kiem tra game ket thuc chua
                    print(f"Game status: {self.status}")
                    game_finished = True
                    break

                elif (self.turn == str(self.team_id)):
                    # check xem den luot minh di chua
                    print("Making move...")
                    self.send_move()

                # nhan tu server trong tai tra ve
                print("Updating game...")
                self.update_game()

        except Exception as e:
            print(f"Error in game playing stage: {e}")

    def play_game(self):
        self.init_thread = threading.Thread(target=self.init_game_thread)
        self.play_thread = threading.Thread(target=self.play_game_thread)

        self.init_thread.start()
        if self.initialized == True:
            self.play_thread.start()
