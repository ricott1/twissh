import urwid
from hacknslassh.gui.scenes import IntroFrame

def test_intro():
    loop = urwid.MainLoop(IntroFrame(None, None))
    loop.run()

if __name__ == "__main__":
    test_intro()