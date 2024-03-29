# encoding: utf-8

"""
Twisted integration for Urwid.
This module allows you to serve Urwid applications remotely over ssh.
The idea is that the server listens as an SSH server, and each connection is
routed by Twisted to urwid, and the urwid UI is routed back to the console.
The concept was a bit of a head-bender for me, but really we are just sending
escape codes and the what-not back to the console over the shell that ssh has
created. This is the same service as provided by the UI components in
twisted.conch.insults.window, except urwid has more features, and seems more
mature.
This module is not highly configurable, and the API is not great, so
don't worry about just using it as an example and copy-pasting.
Process
-------
TODO:
- better gpm tracking: there is no place for os.Popen in a Twisted app I
  think.
Copyright: 2010, Ali Afshar <aafshar@gmail.com>
License:   MIT <http://www.opensource.org/licenses/mit-license.php>
Portions Copyright: 2010, Ian Ward <ian@excess.org>
Licence:   LGPL <http://opensource.org/licenses/lgpl-2.1.php>
Portions Copyright: 2022, Costantino Frittura <inverness@duck.com>
Licence:   LGPL <http://opensource.org/licenses/lgpl-2.1.php>
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Type

import uuid, time
import urwid
from urwid.raw_display import Screen

# from .converter_sixel import convert

from zope.interface import Interface, Attribute, implementer
from twisted.application.service import Application
from twisted.application.internet import TCPServer
from twisted.web import server

from twisted.conch.interfaces import IConchUser, ISession, ISessionSetEnv, EnvironmentVariableNotPermitted
from twisted.conch.insults.insults import TerminalProtocol, ServerProtocol
from twisted.conch.manhole_ssh import (
    ConchFactory,
    TerminalRealm,
    TerminalUser,
    TerminalSession,
    TerminalSessionTransport,
)
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.portal import Portal
from twisted.cred import credentials
from twisted.conch.ssh.keys import Key
from twisted.conch.ssh.userauth import SSHUserAuthServer
from twisted.conch.error import ConchError
from twisted.conch import interfaces
from twisted.python.components import Componentized, Adapter
from twisted.internet.task import LoopingCall
from twisted.internet import defer, reactor


from web.sql_server import SQLConnectorServer


class UrwidUi(object):
    def __init__(self, mind: UrwidMind, toplevel: Type[urwid.Widget]) -> None:
        self.mind = mind
        self.toplevel = toplevel(self.mind)
        self.palette = self.toplevel.palette
        self.redraw = False
        self.screen = TwistedScreen(self.mind.terminalProtocol)
        self.loop = self.create_urwid_mainloop()
        self.loop.run()

    def create_urwid_mainloop(self) -> urwid.MainLoop:
        evl = urwid.TwistedEventLoop(manage_reactor=False)
        loop = urwid.MainLoop(
            self.toplevel,
            screen=self.screen,
            event_loop=evl,
            unhandled_input=self.mind.unhandled_key,
            palette=self.palette,
        )
        loop.screen.set_terminal_properties(colors=256)
        self.screen.loop = loop
        return loop

    def handle_input(self, _input):
        self.toplevel.handle_input(_input)

    def disconnect(self) -> None:
        self.loop.screen.unhook_event_loop(self.loop.event_loop)
        self.loop.screen.stop()


class IUrwidMind(Interface):
    ui = Attribute("")
    terminalProtocol = Attribute("")
    terminal = Attribute("")
    avatar = Attribute("The avatar")

    def push(data) -> None:
        """Push data"""

    def draw() -> None:
        """Refresh the UI"""

    def on_update() -> None:
        """Update cycle"""

    def register_callback(event_name: str, callback: Callable):
        """Register a callback"""

    def emit_event(event_name: str, *args, **kwargs) -> None:
        """Emit an event"""


class UnhandledKeyHandler(object):
    def __init__(self, mind: UrwidMind):
        self.mind = mind

    def push(self, key: tuple | str) -> None:
        if isinstance(key, tuple):
            pass
        else:
            mind_handler = getattr(self, "key_%s" % key.replace(" ", "_"), None)
            if mind_handler is None:
                screen_handler = self.mind.ui.handle_input
                if screen_handler is None:
                    return
                else:
                    return screen_handler(key)
            else:
                return mind_handler(key)

    def key_ctrl_c(self, _) -> None:
        self.mind.disconnect()


@dataclass
class UrwidMaster:
    minds: dict[bytes, UrwidMind]
    toplevel: urwid.Widget

    def register_mind(self, mind: UrwidMind) -> None:
        self.minds[mind.avatar.uuid.bytes] = mind

    def dispatch_event(self, event_name: str, *args, **kwargs) -> None:
        for k, mind in self.minds.items():
            mind.process_event(event_name, *args, **kwargs)


implementer(IUrwidMind)


class UrwidMind(Adapter):
    unhandled_key_factory = UnhandledKeyHandler

    def __init__(self, original: Componentized) -> None:
        super().__init__(original)
        self.master = None
        self.connection_error: None | AvatarConnectionError = None
        self.ui = None
        self.last_frame = time.time()
        self.callbacks = {}
        self.twisted_update_loop: LoopingCall | None = None
        self.terminalProtocol = None
        self.terminal: None | UrwidServerProtocol = None

    @property
    def avatar(self) -> UrwidUser:
        return IConchUser(self.original)

    @property
    def screen_size(self) -> tuple[int, int]:
        if self.ui:
            return self.ui.screen.get_cols_rows()
        return (80, 24)

    def set_ui_redraw(self) -> None:
        if self.ui:
            self.ui.redraw = True

    def set_terminalProtocol(self, terminalProtocol: UrwidTerminalProtocol) -> None:
        self.terminalProtocol = terminalProtocol
        self.terminal = terminalProtocol.terminal
        self.unhandled_key_handler = self.unhandled_key_factory(self)
        self.unhandled_key = self.unhandled_key_handler.push
        if self.master:
            self.ui = UrwidUi(self, self.master.toplevel)
            self.draw()

    def set_master(self, master: UrwidMaster) -> None:
        self.master = master
        self.master.register_mind(self)
        # we ask to redraw as soon as a change from the ui is registered
        self.register_callback("redraw_ui", self.set_ui_redraw, -1)
        # self.register_callback("redraw_ui", self.set_ui_redraw)
        # self.register_callback("redraw_global_ui", lambda: self.master.dispatch_event("redraw_ui"), priority=1)
        self.register_callback(
            "chat_message_sent",
            lambda _from_name, _from_id, msg, attr, language: self.master.dispatch_event(
                "chat_message_received", _from_name, _from_id, msg, attr, language
            ),
        )

    def push(self, data):
        if self.ui:
            self.ui.screen.push(data)
            self.draw()

    def draw(self):
        if self.ui:
            self.ui.loop.draw_screen()
            self.ui.redraw = False

    def disconnect(self):
        if self.master:
            if self.avatar.uuid.bytes in self.master.player_ids and self.terminal:
                self.terminal.write(f"Your player ID is {self.avatar.uuid.hex}\n")
            self.master.disconnect(self)
        if self.ui:
            self.ui.disconnect()
            self.ui = None
        
        if self.twisted_update_loop and self.twisted_update_loop.running:
            self.twisted_update_loop.stop()

        if self.terminal:
            if self.connection_error:
                self.terminal.write(self.connection_error.encode())
            self.terminal.write(f"\nGood bye!\n")
            self.terminal.transport.loseConnection()

    def register_callback(self, event_name: str, callback: Callable, priority: int = 0) -> None:
        if event_name in self.callbacks:
            self.callbacks[event_name].append({"priority": priority, "callback": callback})
            self.callbacks[event_name] = sorted(self.callbacks[event_name], key=lambda x: x["priority"], reverse=True)
        else:
            self.callbacks[event_name] = [{"priority": priority, "callback": callback}]

    def process_event(self, event_name: str, *args, **kwargs) -> None:
        if event_name in self.callbacks:
            for c in self.callbacks[event_name]:
                c["callback"](*args, **kwargs)


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
        # self.register_palette_entry(None, "white", "black")
        urwid.signals.connect_signal(self, urwid.UPDATE_PALETTE_ENTRY, self._on_update_palette_entry)
        # Don't need to wait for anything to start
        # self._started = True
        self._start()

    # Urwid Screen API

    def get_cols_rows(self):
        """Get the size of the terminal as (cols, rows)"""
        return self.terminalProtocol.width, self.terminalProtocol.height

    def draw_screen(self, maxres, r):
        """Render a canvas to the terminal.

        The canvas contains all the information required to render the Urwid
        UI. The content method returns a list of rows as (attr, cs, text)
        tuples. This very simple implementation iterates each row and simply
        writes it out.
        """
        (maxcol, maxrow) = maxres
        # self.terminal.eraseDisplay()
        lasta = None
        for i, row in enumerate(r.content()):
            self.terminal.cursorPosition(0, i)
            for (attr, cs, text) in row:
                if attr != lasta:
                    text = b"%s%s" % (self._attr_to_escape(attr).encode("utf-8"), text)
                lasta = attr
                # if cs or attr:
                # print(text.decode('utf-8', "ignore"))
                self.write(text)
        # cursor = r.get_cursor()
        # if cursor is not None:
        #     self.terminal.cursorPosition(*cursor)

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
        # print(f"Updating {name} palette: ", attrspecs[{16:0,1:1,88:2,256:3}[self.colors]])
        # copy the attribute to a dictionary containing the escape sequences
        self._pal_escape[name] = self._attrspec_to_escape(attrspecs[{16: 0, 1: 1, 88: 2, 256: 3}[self.colors]])

    def _attr_to_escape(self, a):
        if a in self._pal_escape:
            return self._pal_escape[a]
        elif isinstance(a, urwid.AttrSpec):
            return self._attrspec_to_escape(a)
        # undefined attributes use default/default
        # TODO: track and report these
        return self._attrspec_to_escape(urwid.AttrSpec("default", "default"))

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
        return f"{urwid.escape.ESC}[0;{fg};{st}{bg}m"  # {urwid.escape.ESC}[0m


class UrwidTerminalProtocol(TerminalProtocol):
    """A terminal protocol that knows to proxy input and receive output from
    Urwid.

    This integrates with the TwistedScreen in a 1:1.
    """

    def __init__(self, urwid_mind: UrwidMind) -> None:
        self.urwid_mind = urwid_mind
        self.width = 120
        self.height = 24

    def connectionMade(self):
        self.urwid_mind.set_terminalProtocol(self)
        self.terminalSize(self.height, self.width)
        # self.terminal.write('\e[8;50;100t'.encode())


    def terminalSize(self, height: int, width: int) -> None:
        """Resize the terminal."""
        if self.urwid_mind.ui:
            self.width = width
            self.height = height
            self.urwid_mind.ui.loop.screen_size = None
            self.urwid_mind.process_event("screen_resize", width, height)
            # Resizing takes a lot of resources server side,
            # could consider just returning here to avoid that
            self.urwid_mind.ui.redraw = True

    def dataReceived(self, data) -> None:
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


@implementer(ISession, ISessionSetEnv)
class UrwidTerminalSession(TerminalSession):
    """A terminal session that remembers the avatar and chained protocol for
    later use. And implements a missing method for changed Window size.

    Note: This implementation assumes that each SSH connection will only
    request a single shell, which is not an entirely safe assumption, but is
    by far the most common case.
    """

    def openShell(self, proto):
        """Open a shell."""
        self.chained_protocol = UrwidServerProtocol(UrwidTerminalProtocol, IUrwidMind(self.original))
        TerminalSessionTransport(proto, self.chained_protocol, IConchUser(self.original), self.height, self.width)

    def windowChanged(self, dimensions):
        """Called when the window size has changed."""
        (h, w, x, y) = dimensions
        self.chained_protocol.terminalProtocol.terminalSize(h, w)

    def setEnv(name, value, *args):
        """Set an environment variable."""
        raise EnvironmentVariableNotPermitted

    def eofReceived(self):
        print("Session eofReceived")
        IUrwidMind(self.original).disconnect()

    def execCommand(self, proto, cmd):
        print("Error: Cannot execute commands", proto, cmd)
        # self.openShell(proto)
        raise ConchError("Cannot execute commands")

    def closed(self):
        print("Session closed")
        IUrwidMind(self.original).disconnect()


class AvatarConnectionError(str, Enum):
    INVALID_AVATAR_ID = "\nInvalid player ID\nTo create a new game connect with gatti@hostname\nTo recover an existing session connect with [player_id]@hostname\n\n"
    AVATAR_ALREADY_CONNECTED = "\nPlayer ID already connected.\nTo create a new game connect with gatti@hostname\nTo recover an existing session connect with [player_id]@hostname\n\n"


class UrwidRealm(TerminalRealm):
    """Custom terminal realm class-configured to use our custom Terminal User
    Terminal Session.
    """

    FPS = 30
    UPDATE_STEP = 1 / FPS

    def __init__(self) -> None:
        from hacknslassh import HackNSlassh

        self.hacknslassh = HackNSlassh()
        self.minds: dict[bytes, UrwidMind] = {}

        LoopingCall(self.hacknslassh.update).start(self.hacknslassh.UPDATE_STEP)

    def requestAvatar(self, avatarId: bytes, mind: UrwidMind, *interfaces: tuple) -> tuple:
        print("requestAvatar", avatarId, mind, interfaces)
        for i in interfaces:
            if i is IConchUser:
                avatar = self._getAvatar(avatarId)
                return (IConchUser, avatar, lambda: None)
        raise NotImplementedError()

    def _getAvatar(self, avatarId: bytes) -> UrwidUser:
        from hacknslassh.db_connector import get_all_players

        comp = Componentized()
        user = UrwidUser(comp, avatarId)
        comp.setComponent(IConchUser, user)
        sess = UrwidTerminalSession(comp)
        comp.setComponent(ISession, sess)
        mind = UrwidMind(comp)

        all_players = get_all_players()
        hex_ids = [p[0] for p in all_players]
        print("available player ids", hex_ids)

        if avatarId in self.minds:
            mind.connection_error = AvatarConnectionError.AVATAR_ALREADY_CONNECTED
        elif avatarId == b"gatti":
            mind.set_master(self.hacknslassh)
            print("New player id", mind.avatar.uuid.hex)
        else:
            for h in hex_ids:
                if avatarId.decode() == h:
                    print("Recovering session", avatarId)
                    mind.set_master(self.hacknslassh)
                    mind.avatar.uuid = uuid.UUID(hex=h)
                    break
            else:
                mind.connection_error = AvatarConnectionError.INVALID_AVATAR_ID

        comp.setComponent(IUrwidMind, mind)

        mind.twisted_update_loop = LoopingCall(self.update_mind, mind)
        mind.twisted_update_loop.start(self.UPDATE_STEP)

        self.minds[mind.avatar.uuid.bytes] = mind
        return user


    def update_mind(self, mind: UrwidMind) -> None:
        if not mind.master and mind.terminal:
            mind.disconnect()
            del self.minds[mind.avatar.uuid.bytes]

        elif mind.ui and mind.ui.redraw:
            mind.draw()

    # def update_minds(self) -> None:
    #     # #then update each mind, that updates each ui if necessary
    #     to_delete = []
    #     for k, mind in self.minds.items():
    #         if not mind.master:
    #             mind.terminal.write(mind.connection_error.encode())
    #             mind.terminal.transport.loseConnection()
    #             to_delete.append(k)
    #             continue

    #         if not mind.ui:
    #             to_delete.append(k)
    #             continue

    #         if mind.ui.redraw:
    #             mind.draw()

    #     for k in to_delete:
    #         del self.minds[k]


class NoCheckSSHUserAuthServer(SSHUserAuthServer):
    """A SSHUserAuthServer that accepts all incoming connections."""

    interfaceToMethod = {
        credentials.ISSHPrivateKey: b"publickey",
        credentials.IUsernamePassword: b"password",
        credentials.IAnonymous: b"none",
    }

    def auth_none(self, packet):
        """
        No authentication.  Just send a success message.
        """
        return self.portal.login(AlmostAnonymous(self.user), None, interfaces.IConchUser)


@implementer(ICredentialsChecker)
class NoCheckAccess:
    credentialInterfaces = (credentials.IAnonymous,)

    def requestAvatarId(self, credentials):
        return defer.succeed(credentials.username)


@implementer(credentials.IAnonymous)
class AlmostAnonymous:
    def __init__(self, username):
        self.username = username


def create_server_factory():
    """Convenience to create a server factory with a portal that uses a realm
    serving a given urwid widget against checkers provided.
    """
    cred_checkers = [NoCheckAccess()]
    rlm = UrwidRealm()
    ptl = Portal(rlm, cred_checkers)
    factory = ConchFactory(ptl)
    factory.services[b"ssh-userauth"] = NoCheckSSHUserAuthServer
    factory.publicKeys[b"ssh-rsa"] = Key.fromFile("keys/test_rsa.pub")
    factory.privateKeys[b"ssh-rsa"] = Key.fromFile("keys/test_rsa")
    return factory


def create_application(application_name, port):
    """Convenience to create an application suitable for tac file"""
    urwid.escape.SHOW_CURSOR = ""
    application = Application(application_name)
    svc = TCPServer(port, create_server_factory())
    svc.setServiceParent(application)

    # from autobahn.twisted.websocket import WebSocketServerFactory
    # factory = WebSocketServerFactory()
    # factory.protocol = SQLConnectorServer
    # sqls = server.Site(factory)
    # reactor.listenTCP(8080, sqls)

    # resource = File('/static')
    # factory = Site(resource)
    # endpoint = endpoints.TCP4ServerEndpoint(reactor, 8888)
    # endpoint.listen(factory)

    static = server.Site(SQLConnectorServer())
    reactor.listenTCP(8081, static)

    return application
