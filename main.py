from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation
from kivy.uix.label import Label
from copy import deepcopy

# Config.set('graphics', 'fullscreen', 'auto')
Config.set('kivy', 'window_icon', 'data/images/face-01.png')
Config.set('kivy', 'log_level', 'info')
Config.set('graphics', 'height', 720)
Config.set('graphics', 'width', 480)
# Config.set('kivy', 'log_level', 'critical')
Config.write()

game_size_hint = .8
map_id = 1
map_color = "red"


class DiceMazeGame(FloatLayout):
    def __init__(self, **kwargs):
        """ Constructs the float layout named DiceMazeGame."""

        super(DiceMazeGame, self).__init__(**kwargs)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        self.popup_closed = True
        self.undo_current_try = 0
        self.move_back_history = []
        self.map_color = map_color

        self.generate_map(map_id)
        self.generate_dice(map_id)

        self.game_resize(self, Window.width, Window.height)

        Window.bind(on_resize=self.game_resize)

    def game_resize(self, window, width_window, height_window):
        """
        Fetch window object, window width and window height.
        Resize game grid layout based on the largest side (side * game_size_hint).
        Calculates dice coordinates (x, y) and size.
        """

        # Game resizing
        ratio = self.cols / self.rows

        self.width_window = width_window
        self.height_window = height_window

        self.height_game = height_window * game_size_hint
        self.width_game = self.height_game * ratio

        if width_window <= self.width_game / game_size_hint:
            self.width_game = width_window * game_size_hint
            self.height_game = self.width_game / ratio

        self.ids.game_zone.size = (self.width_game, self.height_game)
        self.ids.game_zone.spacing = width_window / 100

        # Dice coordinates and size calculation
        total_height_spacing = (self.rows - 1) * self.ids.game_zone.spacing[1]
        total_width_spacing = (self.cols - 1) * self.ids.game_zone.spacing[0]

        self.margin_x = (self.width_window - self.width_game) / 2
        self.margin_y = (self.height_window - self.height_game) / 2

        self.dice_size = ((self.width_game - total_width_spacing) / self.cols, (self.height_game - total_height_spacing) / self.rows)
        self.ids.dice.size = self.dice_size

        self.col_width = (self.dice_size[0] + self.ids.game_zone.spacing[0])
        self.row_height = (self.dice_size[1] + self.ids.game_zone.spacing[1])

        self.dice_pos_x = self.margin_x + self.col_width * self.dice_tiles_dict['CURRENT'][0]
        self.dice_pos_y = self.margin_y + self.height_game - self.dice_size[1] - self.row_height * self.dice_tiles_dict['CURRENT'][1]

        self.ids.dice.pos = self.dice_pos_x, self.dice_pos_y

        self.ids.pause.size = self.dice_size if self.margin_y / 2 > self.dice_size[1] else (self.margin_y / 2, self.margin_y / 2)
        self.ids.undo.size = self.ids.pause.size

        self.ids.pause.pos = self.margin_x + self.width_game - self.ids.pause.size[0], self.height_window - self.ids.pause.size[1] - (self.margin_y - self.ids.pause.size[1]) / 2
        self.ids.undo.pos = self.ids.pause.pos[0] - self.ids.undo.size[0] * 2, self.ids.pause.pos[1]

        self.dice_move(None)
        self.print_info()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """
        Waits for keyboard inputs.
        Dice rolls and moves according to the key pressed.
        """
        if keycode[1] == "up":
            self.dice_move("up")
        elif keycode[1] == "down":
            self.dice_move("down")
        elif keycode[1] == "left":
            self.dice_move("left")
        elif keycode[1] == "right":
            self.dice_move("right")

        self.print_info()

    def generate_map(self, map):
        """
        Imports map from .txt file (between MAP START and MAP END) and makes an array.
        Adds images to the game grid layout according to the array.
        Adds Start and End tiles coordinates to dictionary.
        """

        def tile_type(row, col):
            """ Returns the name for each type of tile (start, end, unknown)"""
            if self.map_array[row][col][1] == 'S':
                return 'START'
            else:
                if self.map_array[row][col][1] == 'E':
                    return 'END'
                else:
                    return 'UNKNOWN'

        file = open('data/maps/map{}.txt'.format(map), 'r')

        self.dice_tiles_dict = {}
        self.map_array = []
        map_lines = False

        for line in file:
            if "MAP END" in line:
                map_lines = False
            elif map_lines:
                self.map_array.append(line.split('\n')[0].split(' '))
            elif "MAP START" in line:
                map_lines = True

        self.cols = len(self.map_array[0])
        self.rows = len(self.map_array)

        self.ids.game_zone.cols = self.cols
        self.ids.game_zone.rows = self.rows

        for i in range(self.rows):
            for j in range(self.cols):
                if self.map_array[i][j][1] != 'X':
                    self.dice_tiles_dict[tile_type(i, j)] = [j, i]
                if self.map_array[i][j][1] == 'E':
                    self.ids.game_zone.add_widget(Image(
                        source='data/images/{}/end-face-0{}.png'.format(self.map_color, self.map_array[i][j][0]),
                        allow_stretch=True))
                else:
                    self.ids.game_zone.add_widget(Image(
                        source='data/images/{}/face-0{}.png'.format(self.map_color, self.map_array[i][j][0]),
                        allow_stretch=True))

        self.dice_tiles_dict['CURRENT'] = deepcopy(self.dice_tiles_dict['START'])

        self.ids.pause_image.source = "data/images/{}/menu.png".format(self.map_color)
        self.ids.undo_image.source = "data/images/{}/undo.png".format(self.map_color)



    def generate_dice(self, map):
        """
        Generates all the faces using 3 entries (top/front/left).
        Fetches faces numbers from map.txt and sets them in face_dict.
        Calculates opposite faces with opp_face function (2 opp faces = 7).
        Checks for dice generation errors.
        Sets dice image background.
        """

        def opp_face(face):
            """Returns the opposite face."""
            if face in ("TOP", "BOTTOM"):
                return "TOP" if face == "BOTTOM" else "BOTTOM"
            elif face in ("FRONT", "BEHIND"):
                return "FRONT" if face == "BEHIND" else "BEHIND"
            elif face in ("LEFT", "RIGHT"):
                return "LEFT" if face == "RIGHT" else "RIGHT"

        file = open('data/maps/map{}.txt'.format(map), 'r')

        self.face_dict = {"TOP": None, "BOTTOM": None, "FRONT": None, "BEHIND": None, "RIGHT": None, "LEFT": None}

        for line in file:
            if line.split(" ")[0] in self.face_dict.keys():
                self.face_dict[line.split(" ")[0]] = int(line.split(" ")[1].rstrip())

        for face_name, face_number in self.face_dict.items():
            if face_number is not None:
                self.face_dict[opp_face(face_name)] = 7 - self.face_dict[face_name]

        dice_generation_error = False
        for face_number in self.face_dict.values():
            if face_number is None:
                dice_generation_error = True
        if dice_generation_error:
            print("Error with dice generation.")

        self.ids.dice.source = "data/images/{}/white-face-0{}.png".format(self.map_color, self.face_dict["TOP"])

    def dice_move(self, move):
        """
        Moves and rotates the dice according to keyboard inputs.
        Top face needs to correspond with next tile to move.
        Changes current position and rotates faces.
        Creates a history to undo last move.
        Calls dice_move for dice coordinates and starts animation.
        Shows popup when dice is stuck or win.
        """

        def tiles_around():
            """Calculates which tiles are around current position."""
            up, down, left, right = None, None, None, None

            if self.dice_tiles_dict['CURRENT'][1] > 0:
                up = int(self.map_array[self.dice_tiles_dict['CURRENT'][1] - 1][self.dice_tiles_dict['CURRENT'][0]][0])

            if self.dice_tiles_dict['CURRENT'][1] < self.rows - 1:
                down = int(self.map_array[self.dice_tiles_dict['CURRENT'][1] + 1][self.dice_tiles_dict['CURRENT'][0]][0])

            if self.dice_tiles_dict['CURRENT'][0] > 0:
                left = int(self.map_array[self.dice_tiles_dict['CURRENT'][1]][self.dice_tiles_dict['CURRENT'][0] - 1][0])

            if self.dice_tiles_dict['CURRENT'][0] < self.cols - 1:
                right = int(self.map_array[self.dice_tiles_dict['CURRENT'][1]][self.dice_tiles_dict['CURRENT'][0] + 1][0])

            return up, down, left, right

        # Updates current position and dice faces.
        # Keeps a history to undo move (move_back).
        up_tile, down_tile, left_tile, right_tile = tiles_around()
        undo = False
        undo_max_try = 3

        if move == "undo" and self.move_back_history and self.undo_current_try < undo_max_try:
            # pop() removes and returns last element in list
            move = self.move_back_history.pop()
            undo = True
            self.undo_current_try += 1

        if move == "up":
            if up_tile is not None and up_tile == self.face_dict['TOP'] or up_tile == 7 or undo:
                if not undo:
                    self.move_back_history.append("down")
                self.dice_tiles_dict['CURRENT'][1] -= 1
                self.face_dict["TOP"], self.face_dict["BOTTOM"], self.face_dict["FRONT"], self.face_dict["BEHIND"] = \
                    self.face_dict["FRONT"], \
                    self.face_dict["BEHIND"], \
                    self.face_dict["BOTTOM"], \
                    self.face_dict["TOP"]
        elif move == "down":
            if down_tile is not None and down_tile == self.face_dict['TOP'] or down_tile == 7 or undo:
                if not undo:
                    self.move_back_history.append("up")
                self.dice_tiles_dict['CURRENT'][1] += 1
                self.face_dict["TOP"], self.face_dict["BOTTOM"], self.face_dict["FRONT"], self.face_dict["BEHIND"] = \
                    self.face_dict["BEHIND"], \
                    self.face_dict["FRONT"], \
                    self.face_dict["TOP"], \
                    self.face_dict["BOTTOM"]
        elif move == "left":
            if left_tile is not None and left_tile == self.face_dict['TOP'] or left_tile == 7 or undo:
                if not undo:
                    self.move_back_history.append("right")
                self.dice_tiles_dict['CURRENT'][0] -= 1
                self.face_dict["TOP"], self.face_dict["BOTTOM"], self.face_dict["RIGHT"], self.face_dict["LEFT"] = \
                    self.face_dict["RIGHT"], \
                    self.face_dict["LEFT"], \
                    self.face_dict["BOTTOM"], \
                    self.face_dict["TOP"]
        elif move == "right":
            if right_tile is not None and right_tile == self.face_dict['TOP'] or right_tile == 7 or undo:
                if not undo:
                    self.move_back_history.append("left")
                self.dice_tiles_dict['CURRENT'][0] += 1
                self.face_dict["TOP"], self.face_dict["BOTTOM"], self.face_dict["RIGHT"], self.face_dict["LEFT"] = \
                    self.face_dict["LEFT"], \
                    self.face_dict["RIGHT"], \
                    self.face_dict["TOP"], \
                    self.face_dict["BOTTOM"]

        # Calculates new position and top face, animation to new position.
        self.dice_pos_x = self.margin_x + self.col_width * self.dice_tiles_dict['CURRENT'][0]
        self.dice_pos_y = self.margin_y + self.height_game - self.dice_size[1] - self.row_height * self.dice_tiles_dict['CURRENT'][1]

        self.ids.dice.source = "data/images/{}/white-face-0{}.png".format(self.map_color, self.face_dict["TOP"])
        self.ids.undo_try.text = str(undo_max_try - self.undo_current_try)

        move = Animation(x=self.dice_pos_x, y=self.dice_pos_y, duration=.2)
        move.start(self.ids.dice)

        # Popup opens when dice is stuck or player wins.
        up_tile, down_tile, left_tile, right_tile = tiles_around()

        popup = ModalView(size_hint=(.4, .4), auto_dismiss=False)

        if self.dice_tiles_dict['CURRENT'] == self.dice_tiles_dict['END'] and self.popup_closed:
            print("Gagné !")
            self.popup_closed = False
            popup.add_widget(Label(text="Congratulations, you won!"))
            popup.open()
        elif self.face_dict["TOP"] not in (up_tile, down_tile, left_tile, right_tile) and 7 not in (up_tile, down_tile, left_tile, right_tile) and self.popup_closed:
            print("Bloqué !")
            self.popup_closed = False
            popup.add_widget(Label(text="Are you stuck? You lost!"))
            popup.open()

    def print_info(self):
        """
        Prints info about:
        - dictionaries (faces, start/end)
        - window, game and dice size
        - dice position
        - move history (undo)
        - self variables
        """

        separation = "==============================================="

        print("INFO")
        print(separation)

        print("DICE FACES")
        for k, v in self.face_dict.items():
            print("{}{} => {}".format(" "*10,k, v))
        print(separation)

        print("DICE TILE POSITION")
        for k, v in self.dice_tiles_dict.items():
            print("{}{} => {}".format(" "*10,k, v))
        print(separation)

        print("MAP")
        for line in self.map_array:
            print("{}{}".format(" "*3, line))
        print(separation)

        print("WINDOW width || {}".format(self.width_window))
        print("WINDOW height || {}".format(self.height_window))
        print(separation)

        print("GAME width || {}".format(self.width_game))
        print("GAME height || {}".format(self.height_game))
        print(separation)

        print("DICE width || {}".format(self.dice_size[0]))
        print("DICE height || {}".format(self.dice_size[1]))
        print("DICE pos_x || {}".format(self.dice_pos_x))
        print("DICE pos_y || {}".format(self.dice_pos_y))
        print(separation)

        print("Undo history || {}".format(self.move_back_history))
        print(separation)

        # for key in sorted(self.__dict__):
        #     print("{}: {}".format(key, self.__dict__[key]))
        # print(separation)


class ScreenManagement(ScreenManager):
    pass


class GameScreen(Screen):
    """
    Overwrite kivy methods (on_pre_enter, on_leave)
    Adds DiceMazeGame to game screen each time it's entered.
    """
    def on_pre_enter(self):
        self.add_widget(DiceMazeGame())

    def on_leave(self):
        self.clear_widgets()


class MenuScreen(Screen):
    pass


class ResumeModal(ModalView):
    pass


class DiceMazeApp(App):
    def rgb(self, r, g, b):
        """Conversion from RGB values (0-255) to Kivy values (0-1)."""
        rate = 1 / 255
        return rate * r, rate * g, rate * b

    def show_popup(self):
        """Opens ResumeModal popup. Called from .kv"""
        p = ResumeModal()
        p.open()
        return p

    def build(self):
        return self.root


if __name__ == '__main__':
    DiceMazeApp().run()
