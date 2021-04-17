import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty;

from typing import List, Union

from utils import readAnimalsCsvFile, writeAnimalsCsvFile


class Root(BoxLayout):
    # The UI widgets
    imageWidget       = ObjectProperty(None)    # The Image widget; need for: `self.image.source`
    isActiveWidget    = ObjectProperty(None)    # The checkbox widget
    imageNumberWidget = ObjectProperty(None)

    # Animal image list
    _currentIndex: int = 0
    _imageList: List[List[Union[bool,str]]]


    def __init__(self, **kwargs):
        """ Create the new Root widget, also loading the animals CSV file
            and moving to the first image
        """
        super(Root, self).__init__(**kwargs)

        # Read in the Animal CSV file
        self._imageList = readAnimalsCsvFile("./animals.final.csv")
        self.moveToImage(0)

        # Grab the keyboard
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use
            # to change the keyboard layout.
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)


    def toggleCurrentImageTag(self):
        """ Toggle the image tag """
        flippedTag = not (self._imageList[self._currentIndex][0])
        self._imageList[self._currentIndex][0] = flippedTag
        self.isActiveWidget.active = flippedTag

        # Immediately save the .csv file
        writeAnimalsCsvFile("./animals.final.csv", self._imageList)


    def onJumpToImage(self, value:str):
        """ Called when the user types in a number and presses enter """
        index = int(value)
        self.moveToImage(index)


    def moveToImage(self, index:int):
        """ Move to the next image """
        self._currentIndex = index
        self.imageWidget.source = self._imageList[self._currentIndex][1]

        # Update the image tag checkbox widget
        tagged = self._imageList[self._currentIndex][0]
        self.isActiveWidget.active = tagged

        # Also update the current index
        self.imageNumberWidget.text = str(self._currentIndex)


    def nextImage(self):
        """ Move to the next image """
        if self._currentIndex >= len(self._imageList)-1: return
        self._currentIndex += 1
        self.moveToImage(self._currentIndex)


    def previousImage(self):
        """ Move to the previous image """
        if self._currentIndex == 0: return
        self._currentIndex -= 1
        self.moveToImage(self._currentIndex)


    def _keyboard_closed(self):
        """ Keyboard closed - unbind the keyboard event """
        pass
        # print('My keyboard have been closed!')
        # self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        # self._keyboard = None


    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """ Keyboard key down """
        # Keycode is a tuple: an integer key code, then a string

        if keycode[1] == 'left':
            self.previousImage()
            return True

        if keycode[1] == 'right':
            self.nextImage()
            return True

        if keycode[1] in ('spacebar'):
            self.toggleCurrentImageTag()
            return True

        if keycode[1] == 'enter':
            # Jump to the image number in the text box on enter
            self.onJumpToImage( self.imageNumberWidget.text )
            return True

        # Return True to accept the key. Otherwise, it will be used by the system.
        return False

    def on_press_button(self):
        print('You pressed the button - code in the widget!')


class ImageValidationApp(App):
    def build(self):
        return Root()


if __name__ == '__main__':
    ImageValidationApp().run()
