from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.modalview import ModalView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image

game_size_hint = .8
map_id = 1


class ResumeModal(ModalView):
    pass


class MenuScreen(Screen):
    pass


class DiceMazeGame(FloatLayout):
    @staticmethod
    def rgb(r, g, b):
        """Conversion from RGB values (0-255) to Kivy values (0-1)."""
        rate = 1 / 255
        return rate * r, rate * g, rate * b

    def game_resize(self, window, width_window, height_window):
        """
        Fetch window object, window width and window height.
        Resize game grid layout based on the largest side (side * game_size_hint).
        """

        ratio = self.cols / self.rows

        # print("===================== resize =====================")
        # print("width_window %s" % width_window)
        # print("height_window %s" % height_window)

        height_game = height_window * game_size_hint
        width_game = height_game * ratio

        if width_window <= width_game / ratio:
            width_game = width_window * game_size_hint
            height_game = width_game / ratio

        # print("width_game %s" % width_game)
        # print("height_game %s" % height_game)

        self.ids.game_zone.size = (width_game, height_game)
        self.ids.game_zone.spacing = width_window / 100

    def __init__(self, **kwargs):
        """ Constructs the float layout named DiceMazeGame."""

        super(DiceMazeGame, self).__init__(**kwargs)

        def generate_map(map_id):
            """
            Imports map from .txt file (between MAP START and MAP END) and makes an array.
            Adds images to the game grid layout according to the array.
            """

            f = open('data/maps/map{}.txt'.format(map_id), 'r')

            map_array = []
            map_lines = False

            for line in f:
                if "MAP END" in line:
                    map_lines = False
                if map_lines:
                    map_array.append(line.split('\n')[0].split(' '))
                if "MAP START" in line:
                    map_lines = True

            self.cols = len(map_array[0])
            self.rows = len(map_array)
            self.ids.game_zone.cols = self.cols
            self.ids.game_zone.rows = self.rows

            for i in range(len(map_array)):
                for j in range(len(map_array[0])):
                    self.ids.game_zone.add_widget(Image(source='data/images/face-0{}.png'.format(map_array[i][j][0])))

        def print_info():
            """Prints info about the game grid layout(size_hint, size, width, height) and the window."""
            print("size_hint %s" % self.ids.game_zone.size_hint)
            print("size %s" % self.ids.game_zone.size)
            print("width %s" % self.ids.game_zone.width)
            print("height %s" % self.ids.game_zone.height)
            print("window size {}".format(Window.size))

        def resume_popup():
            """
            Creates ModalView(popup), BoxLayout and Buttons.
            Adds buttons to the BoxLayout and adds the BoxLayout to the ModalView(popup).
            Binds pause button with the opening of the ModalView(popup).
            """

            popup = ResumeModal(id="popup", size_hint=(.4, .4), auto_dismiss=False)
            box = BoxLayout(orientation='vertical')

            btn1 = Button(text="Resume", on_press=popup.dismiss)
            btn2 = Button(text="Restart")
            btn3 = Button(text="Menu")

            # ============= NOT WORKING =============

            """How to convert kivy lang (on_press: app.root.current = "game") to python ?"""

            # btn2.bind(on_press=change_screen("game"))
            # btn3.bind(on_press=change_screen("menu"))

            # =======================================

            box.add_widget(btn1)
            box.add_widget(btn2)
            box.add_widget(btn3)

            popup.add_widget(box)
            self.ids.pause.bind(on_press=popup.open)
            # print(self.ids.keys())

        generate_map(map_id)
        print_info()
        resume_popup()

        self.game_resize(self, Window.width, Window.height)
        Window.bind(on_resize=self.game_resize)


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__()
        self.add_widget(DiceMazeGame())


class ScreenManagement(ScreenManager):
    pass


class DiceMazeApp(App):
    def build(self):
        return Builder.load_file("dicemaze.kv")


if __name__ == '__main__':
    DiceMazeApp().run()
