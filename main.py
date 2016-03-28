from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation
from copy import deepcopy

# Config.set('graphics', 'fullscreen', 'auto')
Config.set('kivy', 'window_icon', 'data/images/face-01.png')
Config.set('kivy', 'log_level', 'info')
# Config.set('kivy', 'log_level', 'critical')
Config.write()

game_size_hint = .8
map_id = 1


class DiceMazeGame(FloatLayout):
    def __init__(self, **kwargs):
        """ Constructs the float layout named DiceMazeGame."""

        super(DiceMazeGame, self).__init__(**kwargs)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        self.generate_map(map_id)
        self.generate_dice(map_id)

        self.game_resize(self, Window.width, Window.height)

        Window.bind(on_resize=self.game_resize)

    def game_resize(self, window, width_window, height_window):
        """
        Fetch window object, window width and window height.
        Resize game grid layout based on the largest side (side * game_size_hint).
        """

        ratio = self.cols / self.rows

        self.width_window = width_window
        self.height_window = height_window

        self.height_game = height_window * game_size_hint
        self.width_game = self.height_game * ratio

        if width_window <= self.width_game / ratio:
            self.width_game = width_window * game_size_hint
            self.height_game = self.width_game / ratio

        self.ids.game_zone.size = (self.width_game, self.height_game)
        self.ids.game_zone.spacing = width_window / 100

        self.height_spacing = (self.rows - 1) * self.ids.game_zone.spacing[1]
        self.width_spacing = (self.cols - 1) * self.ids.game_zone.spacing[0]

        self.dice_move()
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
            self.dice_roll("up")
        elif keycode[1] == "down":
            self.dice_roll("down")
        elif keycode[1] == "left":
            self.dice_roll("left")
        elif keycode[1] == "right":
            self.dice_roll("right")

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
                self.ids.game_zone.add_widget(Image(source='data/images/face-0{}.png'.format(self.map_array[i][j][0])))
                if self.map_array[i][j][1] != 'X':
                    self.dice_tiles_dict[tile_type(i, j)] = [j, i]

        self.dice_tiles_dict['CURRENT'] = deepcopy(self.dice_tiles_dict['START'])

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

        self.ids.dice.source = "data/images/white_face-0{}.png".format(self.face_dict["TOP"])

    def dice_move(self, *args):
        """
        Calculates dice size and position.
        Changes dice image background.
        Starts the moving animation.
        """

        self.dice_size = ((self.width_game - self.width_spacing) / self.cols, (self.height_game - self.height_spacing) / self.rows)
        self.ids.dice.size = self.dice_size

        margin_x = (self.width_window - self.width_game) / 2
        margin_y = (self.height_window - self.height_game) / 2

        col_width = (self.dice_size[0] + self.ids.game_zone.spacing[0])
        row_height = (self.dice_size[1] + self.ids.game_zone.spacing[1])

        self.dice_pos_x = margin_x + col_width * self.dice_tiles_dict['CURRENT'][0]
        self.dice_pos_y = margin_y + self.height_game - self.dice_size[1] - row_height * self.dice_tiles_dict['CURRENT'][1]

        self.ids.dice.source = "data/images/white_face-0{}.png".format(self.face_dict["TOP"])

        move = Animation(x=self.dice_pos_x, y=self.dice_pos_y, duration=.2)
        move.start(self.ids.dice)

    def dice_roll(self, move):
        """
        Moves and rotates the dice according to keyboard inputs.
        Top face needs to correspond with next tile to move.
        Checks if the dice is stuck and can't move again.
        Checks if the dice is on the end tile, player wins.
        """

        def tiles_around():
            """Calculates what tiles are around the current position."""
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

        up_tile, down_tile, left_tile, right_tile = tiles_around()

        if move == "up":
            if up_tile is not None and up_tile == self.face_dict['TOP'] or up_tile == 7:
                self.dice_tiles_dict['CURRENT'][1] -= 1
                self.face_dict["TOP"], self.face_dict["BOTTOM"], self.face_dict["FRONT"], self.face_dict["BEHIND"] = \
                    self.face_dict["FRONT"], \
                    self.face_dict["BEHIND"], \
                    self.face_dict["BOTTOM"], \
                    self.face_dict["TOP"]
        elif move == "down":
            if down_tile is not None and down_tile == self.face_dict['TOP'] or down_tile == 7:
                self.dice_tiles_dict['CURRENT'][1] += 1
                self.face_dict["TOP"], self.face_dict["BOTTOM"], self.face_dict["FRONT"], self.face_dict["BEHIND"] = \
                    self.face_dict["BEHIND"], \
                    self.face_dict["FRONT"], \
                    self.face_dict["TOP"], \
                    self.face_dict["BOTTOM"]
        elif move == "left":
            if left_tile is not None and left_tile == self.face_dict['TOP'] or left_tile == 7:
                self.dice_tiles_dict['CURRENT'][0] -= 1
                self.face_dict["TOP"], self.face_dict["BOTTOM"], self.face_dict["RIGHT"], self.face_dict["LEFT"] = \
                    self.face_dict["RIGHT"], \
                    self.face_dict["LEFT"], \
                    self.face_dict["BOTTOM"], \
                    self.face_dict["TOP"]
        elif move == "right":
            if right_tile is not None and right_tile == self.face_dict['TOP'] or right_tile == 7:
                self.dice_tiles_dict['CURRENT'][0] += 1
                self.face_dict["TOP"], self.face_dict["BOTTOM"], self.face_dict["RIGHT"], self.face_dict["LEFT"] = \
                    self.face_dict["LEFT"], \
                    self.face_dict["RIGHT"], \
                    self.face_dict["TOP"], \
                    self.face_dict["BOTTOM"]

        self.dice_move()

        up_tile, down_tile, left_tile, right_tile = tiles_around()

        if self.dice_tiles_dict['CURRENT'] == self.dice_tiles_dict['END']:
            print("Gagné !")
        elif int(self.face_dict["TOP"]) not in (up_tile, down_tile, left_tile, right_tile):
            print("Bloqué !")

    def print_info(self):
        """
        Prints info about:
        - dictionaries (faces, start/end)
        - window, game and dice size
        - dice position
        - self variables
        """

        separation = "==============================================="

        print("INFO")
        print(separation)

        print("DICE FACES || {}".format(self.face_dict))
        print("DICE TILES || {}".format(self.dice_tiles_dict))
        print("MAP || {}".format(self.map_array))
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

        # for key in sorted(self.__dict__):
        #     print("{}: {}".format(key, self.__dict__[key]))
        # print(separation)


class ScreenManagement(ScreenManager):
    pass


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.add_widget(DiceMazeGame())


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

    def build(self):
        return self.root


if __name__ == '__main__':
    DiceMazeApp().run()
