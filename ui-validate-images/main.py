import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

class Root(BoxLayout):
    pass
    # source = StringProperty(None)

    def on_press_button(self):
        print('You pressed the button - code in the widget!')


class ImageValidationApp(App):
    def build(self):
        return Root()

    def on_press_button(self):
        print('You pressed the button!')


if __name__ == '__main__':
    ImageValidationApp().run()
