"""This module has a class for video processing"""


import render_strategy as re

class VideoEngine:
    """
    A class to encapsulate a video processing methods and persist variables across the process
    """

    def __init__(self, strategy="default"):
        strategy_object = re.STRATEGIES[strategy]
        self.render_strategy = strategy_object
        self.read_buffer = None

    def set_strategy(self, strategy):
        """
        Set a render strategy
        """
        strategy_object = re.STRATEGIES[strategy]
        self.render_strategy = strategy_object

    def load_video_from_device(self, id=0):
        """
        Load a video file into the engine and set a read buffer
        """
        import cv2
        cap = cv2.VideoCapture(id)
        self.read_buffer = cap

    def play(self, file=None):
        """
        Play the video captured using an specific render strategy
        """
        
        self.render_strategy.render(self.read_buffer)
