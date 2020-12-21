"""This module contains a CLI interface"""

import player
from PIL import Image
import cv2, sys, os

def image_to_byte_array(image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr

def main():
    import argparse

    CLI_DESC = "It is a simple python package to play videos in the terminal using colored characters as pixels or other usefull outputs"
    EPILOG = ("\033[1;37mThanks for trying video-to-ascii!\033[0m")

    PARSER = argparse.ArgumentParser(prog='video-to-ascii', description=CLI_DESC, epilog=EPILOG)
    PARSER.add_argument('--strategy', default='filled-ascii', type=str, dest='strategy', 
        choices=["ascii-color", "just-ascii", "filled-ascii"], help='choose an strategy to render the output', action='store')
    ARGS = PARSER.parse_args()

    # try:
    #     player.play(strategy=ARGS.strategy)
    # except (KeyboardInterrupt):
    #     pass

    img = cv2.imread('./tutti.jpg')
    # img.show()
    import video_engine as ve
    strategy=ARGS.strategy
    engine = ve.VideoEngine()
    if strategy is not None:
        engine.set_strategy(strategy)
    s = engine.render_strategy
    try:
        # _ret, frame = img.read()
        frame = img
        rows, cols = os.popen('stty size', 'r').read().split()
        # sys.stdout.write('\u001b[0;0H')
        # scale each frame according to terminal dimensions
        resized_frame = s.resize_frame(frame, (cols, rows))
        # convert frame pixels to colored string
        msg = s.convert_frame_pixels_to_ascii(resized_frame, (cols, rows)) 
        print(msg)
        # sys.stdout.write(msg) # Print the final string
        # sys.stdout.write("echo -en '\033[2J' \n")
    except (KeyboardInterrupt):
        pass

if __name__ == '__main__':
    main()
