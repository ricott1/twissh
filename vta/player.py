"""This module contains a set of functions to use the video_to_ascii from cli"""

import video_engine as ve

def play(strategy=None):
    """
    Play or export a video from a file by default using ascii chars in terminal
    """
    engine = ve.VideoEngine()
    engine.load_video_from_device()
    if strategy is not None:
        engine.set_strategy(strategy)
    engine.play()
