import asyncio
import sys
import threading
import ssl
import traceback
from .menu import Menu
from anon_framework.config.servers import SERVERS
import pydle
from pydle.features.tls import TLSSupport

# This is a workaround for a bug in pydle where TLS and proxy arguments conflict.
# We are "monkey-patching" the library by replacing the original problematic
# method with our corrected version before the client starts.
_original_connect = TLSSupport._connect

async def _patched_connect(self, hostname, port, **kwargs):
    """
    A patched version that checks the kwargs for TLS status and removes the
    conflicting 'proxy' argument for TLS connections.
    """
    if kwargs.get('tls'):
        kwargs.pop('proxy', None)
    
    return await _original_connect(self, hostname, port, **kwargs)

# Apply the patch
TLSSupport._connect = _patched_connect


# By patching the library, we can now inherit from the standard pydle.Client
# without causing a Method Resolution Order (MRO) error.
class IRCClient(pydle.Client):
    """
    An IRC client rebuilt using the 'pydle' library for modern,
    asynchronous, and robust communication.
    """
    def __init__(self, nickname, channel, use_tor=False):
        super().__init__(nickname, realname='Anon-Framework User')
        
        self.target_channel = channel
        self.use_tor = use_tor
        self.menu = Menu(self)
        self.servers = SERVERS
        self.is_connected = False
        self.identities = {}
        
        # Create a synchronization event to signal disconnection.
        self._disconnected_event = asyncio.Event()

        # Set encoding properties correctly on initialization.
        self.encoding = 'utf-8'
        self._fallback_encodings = ['latin-1', 'cp1252']

    async def on_raw_motd(self, message):
        """Called for each line of the Message of the Day."""
        print(message)

    async def on_unknown(self, message):
        """Called for any server message that doesn't have a specific handler."""
        # This prevents raw numerics from looking like an error.
        # The `message` object may not have a `.raw` attribute, so we
        # convert it to a string for a safe, generic representation.
        print(f"[Server] {str(message)}")

    async def on_connect(self):
        """Called when the client has successfully connected to the server."""
        await super().on_connect()
        # Get a reference to the event loop for threadsafe operations.
        self.loop = asyncio.get_running_loop()
        print(f"Successfully connected to {self.connection.hostname}.")
        self.is_connected = True
        # Clear the event in case of reconnects.
        self._disconnected_event.clear()
        if self.target_channel:
            print(f"Joining channel {self.target_channel}...")
            await self.join(self.target_channel)

    async def on_join(self, channel, user):
        """Called when a user (including us) joins a channel."""
        if user == self.nickname:
            print(f"Joined {channel}. Type messages and press Enter.")
            print("Type /menu to access options, or /raw to send a raw command.")

    async def on_message(self, target, source, message):
        """Called when a message is received in a channel or private query."""
        if source != self.nickname:
            sys.stdout.write('\r' + ' ' * 80 + '\r')
            print(f"<{source}> {message}")
            sys.stdout.write(f"[{target or ''}]> ")
            sys.stdout.flush()

    async def on_nickname_in_use(self, nickname):
        """Called when the desired nickname is already taken."""
        new_nickname = nickname + '_'
        print(f"Nickname '{nickname}' is in use. Trying '{new_nickname}'.")
        await self.set_nickname(new_nickname)

    async def on_disconnect(self, expected):
        """Called when the client disconnects from the server."""
        await super().on_disconnect(expected)
        print("\nDisconnected from server.")
        self.is_connected = False
        # Signal that the client has disconnected.
        self._disconnected_event.set()


    def send_message(self, message):
        """Sends a message to the current channel, scheduled on the event loop."""
        if self.is_connected and self.target_channel:
            asyncio.run_coroutine_threadsafe(self.message(self.target_channel, message), self.loop)
        else:
            print("You are not in a channel.")

    def send_raw_command(self, command, *args):
        """Sends a raw command, scheduled on the event loop."""
        if self.is_connected:
            print(f"--> {command} {' '.join(args)}")
            asyncio.run_coroutine_threadsafe(self.raw(command, *args), self.loop)
        else:
            print("You are not connected to a server.")

    def list_channels(self):
        print("Requesting channel list...")
        self.send_raw_command("LIST")

    def search_channels(self, query):
        print(f"Searching for channels matching '{query}'...")
        self.send_raw_command("LIST", f"*{query}*")

    def join_channel(self, channel):
        if not channel.startswith("#"):
            channel = "#" + channel
        self.target_channel = channel
        print(f"Joining {channel}...")
        asyncio.run_coroutine_threadsafe(self.join(channel), self.loop)

    def leave_channel(self):
        if self.target_channel:
            print(f"Leaving {self.target_channel}...")
            asyncio.run_coroutine_threadsafe(self.part(self.target_channel), self.loop)
            self.target_channel = None

    def change_nickname(self, nickname):
        asyncio.run_coroutine_threadsafe(self.set_nickname(nickname), self.loop)

    def disconnect(self):
        """Schedules the disconnection on the event loop."""
        asyncio.run_coroutine_threadsafe(super().disconnect(), self.loop)

    def input_loop(self):
        """The main loop for handling user input, run in a separate thread."""
        while not self.is_connected:
            threading.Event().wait(0.2)

        try:
            while self.is_connected:
                prompt = f"[{self.target_channel or 'No Channel'}]> "
                message = input(prompt)

                if not self.is_connected:
                    break

                if message == '/menu':
                    self.menu.current_menu = "main"
                    while self.is_connected:
                        self.menu.display_menu()
                        choice = input("Enter your choice: ")
                        if not self.menu.handle_choice(choice):
                            print("\n--- Exited menu. You are back in the channel. ---")
                            break
                elif message.startswith('/raw '):
                    parts = message.split(' ', 1)
                    if len(parts) > 1:
                        self.send_raw_command(*parts[1].split(' '))
                elif message.startswith('/'):
                    print(f"Unknown command: '{message}'.")
                else:
                    self.send_message(message)
        except (EOFError, KeyboardInterrupt):
            print("\nDisconnecting...")
            self.disconnect()
        

    async def start(self):
        """Configures and starts the IRC client."""
        default_nickname = self.nickname or 'anon_framework_user'
        custom_nickname = input(f"Enter your nickname (default: {default_nickname}): ").strip()
        if custom_nickname:
            self.nickname = custom_nickname

        print("Please select a server to connect to:")
        for i, server in enumerate(self.servers):
            print(f"{i+1}. {server['name']} ({server['host']}:{server['port']})")

        server_info = None
        while not server_info:
            try:
                choice = int(input("Enter your choice: "))
                if 1 <= choice <= len(self.servers):
                    server_info = self.servers[choice - 1]
            except (ValueError, EOFError):
                pass
            if not server_info:
                print("Invalid choice. Please try again.")

        host = server_info["host"]
        port = server_info["port"]
        ssl = server_info.get("ssl", False)
        
        proxy = None
        if self.use_tor:
            print("Configuring connection via Tor...")
            proxy = pydle.protocol.SOCKS5Proxy('127.0.0.1', 9050)

        input_thread = threading.Thread(target=self.input_loop, daemon=True)
        input_thread.start()

        print(f"Connecting to {host}:{port}...")
        try:
            await self.connect(
                hostname=host,
                port=port,
                tls=ssl,
                proxy=proxy,
                tls_verify=False # For simplicity
            )
            # The library handles message processing in the background.
            # We just need to wait for our disconnection event to be set.
            await self._disconnected_event.wait()
        except Exception as e:
            print(f"Failed to connect: {e}")
            print("\n--- DETAILED ERROR ---")
            traceback.print_exc()
            print("----------------------\n")
        finally:
            # The loop is managed by asyncio.run(), so we don't need to stop it manually.
            pass

