"""
A Tkinter UI that allows me to scroll through the images and select regions on the images
that should be tagged by the solution.
"""
import os
import tkinter as tk
from tkinter import filedialog
from typing import Union
import threading

import model
import dataAccessLayer as dal

# To understand weak references, please see:
# https://docs.python.org/3.8/c-api/weakref.html
# and: https://www.geeksforgeeks.org/weak-references-in-python/

ROOT_TITLE = "Image data annotator"

# The number of seconds until it automatically moves to the next image
NEXT_IMAGE_SECONDS = 0.50


class DataAnnotatorUI():
    """ The Tkinter UI class
        Here I have tried to focus as much as possible on just the UI layer,
        without any business or image logic.
    """

    def __init__(self):
        # Setup the root window (title, initial size, etc.)
        self._root = tk.Tk()
        self.root.title(ROOT_TITLE)
        self.root.geometry('%sx%s' % (500, 500))
        # _rootWindow.resizable(False,False)
        self.root.minsize(500, 500)
        self.root.configure(background='grey')
        self.root.bind("<KeyRelease>", self._onKeyUp)           # type: ignore

        # Setup the main menu for the root window
        self.menubar = tk.Menu(self.root)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open folder...", command=self.promptUserForFolderToProcess)
        self.filemenu.add_command(label="Save annotations", command=self._saveAnnotations )

        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.root.config(menu=self.menubar)

        # Create the image _canvas
        self._canvas = tk.Canvas(self.root, borderwidth=0, highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)
        self._canvas.bind('<Button-1>', self._onMouseDown)      # type: ignore
        self._canvas.bind('<B1-Motion>', self._onMouseDrag)     # type: ignore
        self._canvas.bind("<Configure>", self._onCanvasResize)  # type: ignore


    @property
    def root(self) -> tk.Tk:
        """ The root Tk window """
        return self._root
    _root: tk.Tk


    @property
    def current(self) -> Union[model.AnnotatedImage,None]:
        """ The current annotated image view model"""
        if self._manager is None: return None
        return self._manager.current


    def mainloop(self):
        """ Tinker speak for start the main message loop/pump to run the application.
        """
        self.root.mainloop()


    # ##############################################################################################
    # region Image and image folder related members
    # ##############################################################################################

    def promptUserForFolderToProcess(self):
        '''The function that processes the main "File|Open folder" menu item.
           This function then starts processing the images in that folder
        '''
        # https://docs.python.org/3.9/library/dialog.html#native-load-save-dialogs and
        # https://stackoverflow.com/questions/51192795/how-can-i-show-all-files-via-filedialog-askdirectory
        fileName:str = filedialog.askopenfilename(  # type: ignore
                          parent=self.root,
                          title="Select any file in the folder to process...")
        if not fileName: return
        folder:str = os.path.dirname(fileName)
        if not folder: return
        self.openFolder(folder)


    def _saveAnnotations(self):
        """ Save the image annotations processed so far
        """
        if self._manager is not None:
            dal.saveAnnotatedImagesToJson(self._manager)


    def openJsonSaveFile(self, file:str):
        """ Process all the images in the given file name
        """
        # If we don't do this, then any old rectangles hang around on the screen
        self._removeImageRegionRectangles()

        # Create annotated image objects for all the images in the selected file
        self._manager = dal.loadImageListFromJsonFile(file, self._canvasSize)
        if self._manager:
            numImages = len(self._manager)
            print("Found: ", numImages, " images")
            self.moveToImage(self._manager.currentIndex)


    def openFolder(self, folder:str):
        """ Starts processing the images in the given folder
            by using the business model to scan the entire folder and find
            all the images that we need to process.
        """
        # If we don't do this, then any old rectangles hang around on the screen
        self._removeImageRegionRectangles()

        # Create annotated image objects for all the images in the selected folder
        self._manager = dal.loadDirectory(folder, self._canvasSize)
        numImages = len(self._manager)
        print("Found: ", numImages, " images")
        self.moveToImage(self._manager.currentIndex)


    def moveToNextImage(self):
        """ Move to the next image
        """
        assert self._manager
        self.moveToImage( self._manager.currentIndex + 1 )


    def moveToImage(self, index:int):
        """ Open the image with the given index
            (into our ordered collection of annotated images that we received from the model layer)
        """
        assert self._manager
        if not self._manager.isValidIndex(index): return

        # First, we need to remove the saved image regions for our current image
        self._removeImageRegionRectangles()

        # Scale the image so it fits while retaining the correct aspect ratio
        # Only scale if we haven't already previously scaled the image (which is slow)
        # Store it back in our domain logic layer for faster access
        self._manager.moveToImage(index)

        # Update our on-screen image to the new image
        self._updateImage()

        # With a new image, we may have new active regions
        # (and we need to remove the old ones)
        self._redrawAllRectangles()

        # Update the window title
        current = self._manager.currentIndex
        total = len(self._manager)
        tagged = "*" if self._manager.current.isTagged else " "
        newTitle = f"{ROOT_TITLE} - {tagged}{current+1} of {total}"
        self.root.title(newTitle)

    # endregion



    # ##############################################################################################
    # region Event handlers
    # ##############################################################################################

    def _onKeyUp(self, event:tk.Event) -> None: # type: ignore
        # Check pre-conditions
        if self._manager is None: return

        # Move "left" 1 image in the collection
        if event.keysym == "Left":
            self._stopAutoMoveTimer()
            self.moveToImage( self._manager.currentIndex - 1 )
            return

        # Move "right" 1 image in the collection
        if event.keysym == "Right":
            self._stopAutoMoveTimer()
            self.moveToNextImage()
            self._saveAnnotations()
            return

        # Move "left" to previously tagged image
        if event.keysym == "d":
            self._stopAutoMoveTimer()
            previousTaggedIndex = self._manager.scanForTaggedIndex(-1)
            if previousTaggedIndex is not None:
                self.moveToImage( previousTaggedIndex )
                self._saveAnnotations()
            return

        # Move "right" to the next tagged image
        if event.keysym == "f":
            self._stopAutoMoveTimer()
            nextTaggedIndex = self._manager.scanForTaggedIndex(+1)
            if nextTaggedIndex is not None:
                self.moveToImage( nextTaggedIndex )
                self._saveAnnotations()
            return

        # Jump to the very first image
        if event.keysym == "Home":
            self._stopAutoMoveTimer()
            self.moveToImage(0)
            return

        # Jump to the very last processed image
        if event.keysym == "End":
            self._stopAutoMoveTimer()
            self.moveToImage(self._manager.maxViewed)
            return

        # Auto-move through the images, without having to continuously press "right"
        if event.keysym == "space":
            if self._autoMoveTimer is None:
                self._startAutoMoveTimer()
            else:
                self._stopAutoMoveTimer()

        # Escape - remove current active rectangle selection
        if event.keysym == "Escape":
            self._stopAutoMoveTimer()
            self._removeActiveImageRegionRectangle()
            self._manager.activeRegion = None
            return

        # Save the current active region
        if event.char in ["s"]:
            self._stopAutoMoveTimer()
            self._removeImageRegionRectangles()     # Clear out existing canvas IDs
            self._manager.addActiveRegion()         # Add our current active region
            self._redrawAllRectangles()             # Now we can redraw them
            if self._manager:                       # Save the new region
                self._saveAnnotations()
            return


    def _onMouseDown(self, event:tk.Event) -> None:     # type: ignore
        """Called when the user clicks on the image canvas.
           Used to capture the starting screen coordinates of the selection rectangle
        """
        if self._manager is None: return
        newRegion = model.Region2d(event.x, event.y, 1, 1)
        self._manager.updateActiveScreenRegion(newRegion)


    def _onMouseDrag(self, event:tk.Event) -> None:     # type: ignore
        """ Called when the user drags the mouse, selecting a rectangular region of the image
            (kind of the entire point of the app)
        """
        if self._manager is None: return

        activeRegion = self._manager.activeRegion
        if activeRegion is None:
            newRegion = model.Region2d(event.x, event.y, 1, 1)

        else:
            # We already have a rectangle, and we're dragging it
            currentRect = activeRegion.screenRegion
            x = currentRect.x
            y = currentRect.y
            w = event.x - currentRect.x
            h = event.y - currentRect.y
            newRegion = model.Region2d(x,y,w,h)

        # Update the active region in the view model layer
        activeRegion = self._manager.updateActiveScreenRegion(newRegion)
        self._drawRegion(activeRegion, "blue")


    def _onCanvasResize(self, event:tk.Event) -> None:  # type: ignore
        """ Called when our image canvas Tk widget is resized.
            When that happens, we need to also resize the image (keeping the aspect ratio)
            and resize the current region selection (if there is one) on the screen
        """
        # Store the new _canvas size
        self._canvasSize = model.Size2d(event.width, event.height)

        # Pre-condition checks
        if self._manager is None: return

        # Update our on-screen image to the new image
        self._manager.onWindowResized(self._canvasSize)

        # Redraw the image with the newly scaled image
        self._updateImage()

        # Scale the on-screen rectangle(s) to the new displayed image scale
        self._redrawAllRectangles()

    # endregion


    # ##############################################################################################
    # region private helper methods
    # ##############################################################################################

    def _redrawAllRectangles(self):
        """ Draws the active region and the image regions
        """
        # Draw all the active regions
        for region in self._manager.regions:
            self._drawRegion(region, "pink")

        # Now (re)draw the active rectangle (if there is one)
        activeRegion = self._manager.activeRegion
        if activeRegion:
            self._drawRegion(activeRegion, "blue")


    def _removeImageRegionRectangles(self):
        """ Remove the annotated image regions we currently have
        """
        # Draw all the active regions
        if self._manager is None: return
        if self.current is None: return
        for region in self._manager.regions:
            self._canvas.delete(region.canvasRectId)
            region.canvasRectId = 0

        # Also remove the active region rectangle
        self._removeActiveImageRegionRectangle()


    def _removeActiveImageRegionRectangle(self):
        """ Remove the current activate regions the user has currently drawn but not saved
        """
        # Also remove the active region rectangle
        activeRegion = self._manager.activeRegion
        if activeRegion:
            self._canvas.delete(activeRegion.canvasRectId)
            activeRegion.canvasRectId = 0


    def _drawRegion(self, region: model.ScaledRegion2d, colour: str = "pink"):
        """ Draw the given region view-model (which must have a `screenRegion` and `canvasRectId`
            property) on the screen with the given colour.
        """
        # Grab the screen coordinates we need to draw the selection rectangle
        x1 = region.screenRegion.x
        y1 = region.screenRegion.y
        x2 = region.screenRegion.right_x
        y2 = region.screenRegion.bottom_y

        if region.canvasRectId == 0:
            # Create selection rectangle (invisible since corner points are equal).
            region.canvasRectId = self._canvas.create_rectangle(x1, y1, x2, y2, # type: ignore
                                                    width=5, dash=(4,4), fill='', outline=colour)
        else:
            # Just update the existing canvas rectangle
            self._canvas.coords(region.canvasRectId, x1, y1, x2, y2) # type: ignore


    def _updateImage(self):
        """ Sets or updates the image on the TK Canvas"""
        assert self._manager.current

        tkImage = self._manager.current.tkScaledImage
        if self._canvasImageId == 0:
            # No canvas image exists yet, so we'll need to create a new one
            # and remember the ID we get back
            self._canvasImageId = self._canvas.create_image(0, 0, image=tkImage, anchor=tk.NW)
        else:
            # We already have an image on the canvas
            # so we simply update the existing image to our newly scaled image object
            self._canvas.itemconfig(self._canvasImageId, image=tkImage)

    # endregion


    # ##############################################################################################
    # region Data members
    # ##############################################################################################

    def _startAutoMoveTimer(self):
        """ Start the auto-movement timer
        """
        if self._autoMoveTimer: return

        def moveToNextImageAndRestartTimer():
            """ A simple helper function that will keep moving us to the next image
                every second by recursively calling _startAutoMoveTimer()
            """
            # First, ensure that we are supposed to run (seems not to cancel properly)
            if self._autoMoveTimer is None: return

            # Try and move to the next image (check if we got to the end)
            try:
                canMove = self.moveToNextImage()
                if canMove is False: return
            except Exception:
                print("Failed to move to the next image")
                return  # Do NOT start another timer if we're hitting errors!

            # Okay, now we can move to the next image and restart the timer
            self._autoMoveTimer = None
            self._startAutoMoveTimer()

        self._autoMoveTimer = threading.Timer(NEXT_IMAGE_SECONDS, moveToNextImageAndRestartTimer )
        self._autoMoveTimer.start()


    def _stopAutoMoveTimer(self):
        """ Stop the auto-movement timer
        """
        if self._autoMoveTimer is None: return
        self._autoMoveTimer.cancel()
        self._autoMoveTimer = None

    # endregion


    # ##############################################################################################
    # region Data members
    # ##############################################################################################

    # The collection of annotated images we need to process for our test set
    _manager: Union[model.AnnotatedImagesManager,None] = None

    # The Canvas object that we use to show the image
    _canvas: tk.Canvas

    # The Canvas ID that we use to update the image on the canvas
    _canvasImageId:int = 0

    # The Canvas ID that we use to update the selection rectangle on the canvas
    _canvasRectId:int = 0

    # The current of the canvas
    _canvasSize: model.Size2d = model.Size2d(500,500)

    # The threading timer used to automatically move to the next image
    # without me getting carpel tunnel by pressing "Right" over and over
    _autoMoveTimer: Union[threading.Timer, None] = None

    # endregion


# cspell: disable-next-line
JSON_FILE = r"D:\dev\workspaces-ai\animal-ai\animals.json"
#TEST_FOLDER = r"D:\data\NRSI\2263B_Turtle-Nest-Mound\2263B_TM Week 2_2020_06_05\NRSI_2263B-TM14-2020-06-03_SEH\100STLTH"
if __name__ == '__main__':
    app = DataAnnotatorUI()
    app.openJsonSaveFile(JSON_FILE)
    #app.openFolder(TEST_FOLDER)
    app.mainloop()
