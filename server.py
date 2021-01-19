# encoding: utf-8

import os, uuid, time
import urwid
from urwid.raw_display import Screen

from zope.interface import Interface, Attribute, implementer
from twisted.application.service import Application
from twisted.application.internet import TCPServer
from twisted.cred.portal import Portal
from twisted.conch.interfaces import IConchUser, ISession
from twisted.conch.insults.insults import TerminalProtocol, ServerProtocol
from twisted.conch.manhole_ssh import (ConchFactory, TerminalRealm, TerminalUser, TerminalSession, TerminalSessionTransport)
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.conch.ssh.keys import EncryptedKeyError, Key
from twisted.cred import error as credError
from twisted.python.components import Componentized, Adapter
from twisted.internet.task import LoopingCall
from twisted.internet import reactor, defer
from datetime import datetime

from rpg_game.gui import GUI
from rpg_game.gui import PALETTE
from rpg_game.master import Master 
from rpg_game.constants import UPDATE_TIMESTEP 



class IUrwidMind(Interface):
    ui = Attribute('')
    terminalProtocol = Attribute('')
    terminal = Attribute('')
    avatar = Attribute('The avatar')

    def push(data):
        """Push data"""

    def draw():
        """Refresh the UI"""

    def on_update():
        """Update cycle"""

class UrwidUi(object):

    def __init__(self, urwid_mind):
        self.mind = urwid_mind
        self.toplevel = GUI(self, self.mind)
        self.palette = PALETTE
        self.redraw = False
        self.screen = TwistedScreen(self.mind.terminalProtocol)
        self.loop = self.create_urwid_mainloop()
        
    def on_update(self):
        self.redraw = False
        self.toplevel.on_update()

    def create_urwid_mainloop(self):
        evl = urwid.TwistedEventLoop(manage_reactor=False)
        loop = urwid.MainLoop(self.toplevel, screen=self.screen,
                              event_loop=evl,
                              unhandled_input=self.mind.unhandled_key,
                              palette=self.palette)
        self.screen.loop = loop
        loop.run()  
        return loop

    def disconnect(self):
        self.toplevel.disconnect()

    def restart(self):
        self.toplevel.restart()

class UnhandledKeyHandler(object):

    def __init__(self, mind):
        self.mind = mind

    def push(self, key):
        if isinstance(key, tuple):
            pass
        else:
            mind_handler = getattr(self, 'key_%s' % key.replace(' ', '_'), None)
            if mind_handler is None:
                screen_handler = self.mind.ui.toplevel.handle_input
                if screen_handler is None:
                    return
                else:
                    return screen_handler(key)
            else:
                return mind_handler(key)

    def key_ctrl_c(self, key):
        self.mind.disconnect()

    def key_ctrl_p(self, key):
        self.mind.restart_ui()

implementer(IUrwidMind)
class UrwidMind(Adapter):
    unhandled_key_factory = UnhandledKeyHandler

    def __init__(self, original, master):
        super().__init__(original)
        self.master = master
        self.ui = None

    @property
    def avatar(self):
        return IConchUser(self.original)

    @property
    def player(self):
        if self.avatar.uuid in self.master.players:
            return self.master.players[self.avatar.uuid]
        return None

    @property
    def screen_size(self):
        return self.ui.screen.get_cols_rows()

    def set_terminalProtocol(self, terminalProtocol):
        self.terminalProtocol = terminalProtocol
        self.terminal = terminalProtocol.terminal
        self.unhandled_key_handler = self.unhandled_key_factory(self)
        self.unhandled_key = self.unhandled_key_handler.push
        self.ui = UrwidUi(self)
        self.draw()

    def push(self, data):
        if self.ui:
            self.ui.redraw = True
            self.ui.screen.push(data)
            # self.draw()

    def draw(self):
        self.ui.on_update()
        self.ui.loop.draw_screen()

    def on_update(self):
        if self.ui and (self.ui.redraw or (self.player and self.player.location.redraw)):
            self.draw()

    def disconnect(self):
        self.master.disconnect(self.avatar.uuid)
        self.terminal.loseConnection()
        self.ui.disconnect()
        self.ui = None

    def restart_ui(self):
        self.master.disconnect(self.avatar.uuid)
        self.ui.restart()
        

class TwistedScreen(Screen):
    """A Urwid screen which knows about the Twisted terminal protocol that is
    driving it.

    A Urwid screen is responsible for:

    1. Input
    2. Output

    Input is achieved in normal urwid by passing a list of available readable
    file descriptors to the event loop for polling/selecting etc. In the
    Twisted situation, this is not necessary because Twisted polls the input
    descriptors itself. Urwid allows this by being driven using the main loop
    instance's `process_input` method which is triggered on Twisted protocol's
    standard `dataReceived` method.
    """

    def __init__(self, terminalProtocol):
        # We will need these later
        self.terminalProtocol = terminalProtocol
        self.terminal = terminalProtocol.terminal
        super(TwistedScreen, self).__init__()
        self.colors = 16
        self._pal_escape = {}
        self.bright_is_bold = True
        self.register_palette_entry(None, 'white', 'black')
        urwid.signals.connect_signal(self, urwid.UPDATE_PALETTE_ENTRY,
            self._on_update_palette_entry)
        # Don't need to wait for anything to start
        #self._started = True
        self._start()


    # Urwid Screen API

    def get_cols_rows(self):
        """Get the size of the terminal as (cols, rows)
        """
        return self.terminalProtocol.width, self.terminalProtocol.height

    def draw_screen(self, maxres, r ):
        """Render a canvas to the terminal.

        The canvas contains all the information required to render the Urwid
        UI. The content method returns a list of rows as (attr, cs, text)
        tuples. This very simple implementation iterates each row and simply
        writes it out.
        """
        (maxcol, maxrow) = maxres
        #self.terminal.eraseDisplay()
        lasta = None
        for i, row in enumerate(r.content()):
            self.terminal.cursorPosition(0, i)
            for (attr, cs, text) in row:
                if attr != lasta:
                    text = b"%s%s" % (self._attr_to_escape(attr).encode("utf-8"), text)
                lasta = attr
                #if cs or attr:
                #print(text.decode('utf-8', "ignore"))
                self.write(text)
        cursor = r.get_cursor()
        if cursor is not None:
            self.terminal.cursorPosition(*cursor)

    # XXX from base screen
    def set_mouse_tracking(self, enable=True):
        """
        Enable (or disable) mouse tracking.

        After calling this function get_input will include mouse
        click events along with keystrokes.
        """
        if enable:
            self.write(urwid.escape.MOUSE_TRACKING_ON)
        else:
            self.write(urwid.escape.MOUSE_TRACKING_OFF)

    # twisted handles polling, so we don't need the loop to do it, we just
    # push what we get to the loop from dataReceived.
    def hook_event_loop(self, event_loop, callback):
        self._urwid_callback = callback
        self._evl = event_loop

    def unhook_event_loop(self, event_loop):
        pass

    # Do nothing here either. Not entirely sure when it gets called.
    def get_input(self, raw_keys=False):
        return

    def get_available_raw_input(self):
        data = self._data
        self._data = []
        return data

    # Twisted driven
    def push(self, data):
        """Receive data from Twisted and push it into the urwid main loop.

        We must here:

        1. filter the input data against urwid's input filter.
        2. Calculate escapes and other clever things using urwid's
        `escape.process_keyqueue`.
        3. Pass the calculated keys as a list to the Urwid main loop.
        """
        self._data = list(map(ord, data.decode("utf-8")))
        self.parse_input(self._evl, self._urwid_callback, self.get_available_raw_input())

    # Convenience
    def write(self, data):
        self.terminal.write(data)

    # Private
    def _on_update_palette_entry(self, name, *attrspecs):
        #print(f"Updating {name} palette: ", attrspecs[{16:0,1:1,88:2,256:3}[self.colors]])
        # copy the attribute to a dictionary containing the escape sequences
        self._pal_escape[name] = self._attrspec_to_escape(
           attrspecs[{16:0,1:1,88:2,256:3}[self.colors]])

    def _attr_to_escape(self, a):
        if a in self._pal_escape:
            return self._pal_escape[a]
        elif isinstance(a, urwid.AttrSpec):
            return self._attrspec_to_escape(a)
        # undefined attributes use default/default
        # TODO: track and report these
        return self._attrspec_to_escape(
            urwid.AttrSpec('default','default'))

    def _attrspec_to_escape(self, a):
        """
        Convert AttrSpec instance a to an escape sequence for the terminal

        >>> s = Screen()
        >>> s.set_terminal_properties(colors=256)
        >>> a2e = s._attrspec_to_escape
        >>> a2e(s.AttrSpec('brown', 'dark green'))
        '\\x1b[0;33;42m'
        >>> a2e(s.AttrSpec('#fea,underline', '#d0d'))
        '\\x1b[0;38;5;229;4;48;5;164m'
        """
        if a.foreground_high:
            fg = "38;5;%d" % a.foreground_number
        elif a.foreground_basic:
            if a.foreground_number > 7:
                if self.bright_is_bold:
                    fg = "1;%d" % (a.foreground_number - 8 + 30)
                else:
                    fg = "%d" % (a.foreground_number - 8 + 90)
            else:
                fg = "%d" % (a.foreground_number + 30)
        else:
            fg = "39"
        st = "1;" * a.bold + "4;" * a.underline + "7;" * a.standout
        if a.background_high:
            bg = "48;5;%d" % a.background_number
        elif a.background_basic:
            if a.background_number > 7:
                # this doesn't work on most terminals
                bg = "%d" % (a.background_number - 8 + 100)
            else:
                bg = "%d" % (a.background_number + 40)
        else:
            bg = "49"
        return f"{urwid.escape.ESC}[0;{fg};{st}{bg}m"#{urwid.escape.ESC}[0m

class UrwidTerminalProtocol(TerminalProtocol):
    """A terminal protocol that knows to proxy input and receive output from
    Urwid.

    This integrates with the TwistedScreen in a 1:1.
    """

    def __init__(self, urwid_mind):
        self.urwid_mind = urwid_mind
        self.width = 80
        self.height = 24

    def connectionMade(self):
        self.urwid_mind.set_terminalProtocol(self)
        self.terminalSize(self.height, self.width)

    def terminalSize(self, height, width):
        """Resize the terminal.
        """
        self.width = width
        self.height = height
        self.urwid_mind.ui.loop.screen_size = None
        self.terminal.eraseDisplay()
        self.urwid_mind.draw()

    def dataReceived(self, data):
        """Received data from the connection.

        This overrides the default implementation which parses and passes to
        the keyReceived method. We don't do that here, and must not do that so
        that Urwid can get the right juice (which includes things like mouse
        tracking).

        Instead we just pass the data to the screen instance's dataReceived,
        which handles the proxying to Urwid.
        """

        self.urwid_mind.push(data)


class UrwidServerProtocol(ServerProtocol):
    def dataReceived(self, data):
        self.terminalProtocol.dataReceived(data)


class UrwidUser(TerminalUser):
    """A terminal user that remembers its avatarId

    The default implementation doesn't
    """
    def __init__(self, original, avatarId):
        TerminalUser.__init__(self, original, avatarId)
        self.avatarId = avatarId
        self.uuid = uuid.uuid4()


class UrwidTerminalSession(TerminalSession):
    """A terminal session that remembers the avatar and chained protocol for
    later use. And implements a missing method for changed Window size.

    Note: This implementation assumes that each SSH connection will only
    request a single shell, which is not an entirely safe assumption, but is
    by far the most common case.
    """

    def openShell(self, proto):
        """Open a shell.
        """
        self.chained_protocol = UrwidServerProtocol(
            UrwidTerminalProtocol, IUrwidMind(self.original))
        TerminalSessionTransport(
            proto, self.chained_protocol,
            IConchUser(self.original),
            self.height, self.width)

    def windowChanged(self, dimensions):
        """Called when the window size has changed.
        """
        (h, w, x, y) = dimensions
        self.chained_protocol.terminalProtocol.terminalSize(h, w)

    def eofReceived(self):
        IUrwidMind(self.original).disconnect()

class UrwidRealm(TerminalRealm):
    """Custom terminal realm class-configured to use our custom Terminal User
    Terminal Session.
    """
    def __init__(self):
        self.mind_factories = {b"new" : UrwidMind}
        self.master = Master()
        self.minds = {}
        self.time = time.time()
        self.update_loop = LoopingCall(self.on_update)
        self.update_loop.start(UPDATE_TIMESTEP)


    def on_update(self):
        #update cycle
        #note: user inputs that do not imply a change of the game state (i.e. changing menu currently viewed) are handled on the mind push function, and drawn immediately (only for the user)
        t = time.time()
        deltatime =  t - self.time
        
        self.master.on_update(deltatime)
        
        # #then update each mind, that updates each ui if necessary
        for k, mind in self.minds.items():
            mind.on_update()

        for k, loc in self.master.world.locations.items():
            loc.redraw = False

        if deltatime > 2*UPDATE_TIMESTEP:
            print("SLOW", deltatime)
        self.time = time.time()

    def _getAvatar(self, avatarId):
        comp = Componentized()
        user = UrwidUser(comp, avatarId)
        comp.setComponent(IConchUser, user)
        sess = UrwidTerminalSession(comp)
        comp.setComponent(ISession, sess)
        mind = UrwidMind(comp, self.master)
        comp.setComponent(IUrwidMind, mind)

        if avatarId in self.master.players and avatarId != b"new":
            player = self.master.players[avatarId]
            mind.avatar.uuid = player.id
            print("Resuming game", mind.avatar.uuid)
        self.minds[mind.avatar.uuid] = mind
        print(f"Connected {avatarId} at {mind.avatar.uuid}")
        return user

    def requestAvatar(self, avatarId, mind, *interfaces):
        for i in interfaces:
            if i is IConchUser:
                if avatarId != b"new" and avatarId not in self.master.players:
                    return defer.fail(credError.UnauthorizedLogin(f"{avatarId} is not a valid game"))
                elif avatarId != b"new" and avatarId in self.minds:
                    return defer.fail(credError.UnauthorizedLogin(f"{avatarId} is already logged in"))
                return (IConchUser,
                        self._getAvatar(avatarId),
                        lambda: None)
        raise NotImplementedError()

class GameServer(TCPServer):
    """docstring for GameServer"""
    def __init__(self, port, factory):
        super().__init__(port, factory)
    
    def add_user(self, avatar):
        username = avatar.uuid
        self.factory.portal.checkers.add_user(username, "")
        

def create_server_factory():
    """Convenience to create a server factory with a portal that uses a realm
    serving a given urwid widget against checkers provided.
    """    
    cred_checkers = [InMemoryUsernamePasswordDatabaseDontUse(new=b'')]
    rlm = UrwidRealm()
    ptl = Portal(rlm, cred_checkers)
    factory = ConchFactory(ptl)
    factory.publicKeys[b'ssh-rsa'] = Key.fromFile('keys/test_rsa.pub')
    factory.privateKeys[b'ssh-rsa'] = Key.fromFile('keys/test_rsa')
    return factory


def create_service(port):
    """Convenience to create a service for use in tac-ish situations.
    """
    f = create_server_factory()
    #return TCPServer(port, f)
    return GameServer(port, f)


def create_application(application_name, port):
    """Convenience to create an application suitable for tac file
    """
    application = Application(application_name)
    svc = create_service(port)
    svc.setServiceParent(application)
    return application

    








