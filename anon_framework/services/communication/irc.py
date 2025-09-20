import asyncio
import sys
import threading
import ssl
from .menu import Menu
from anon_framework.config.servers import SERVERS
import pydle

# This is a workaround for a bug in pydle where TLS and proxy arguments conflict.
# We create a patched version of the TLS feature that handles proxying correctly.
class PatchedTLSSupport(pydle.features.tls.TLSSupport):
    async def _connect_tls(self, hostname, port, tls_verify=True, **kwargs):
        # Pop the proxy argument so it's not passed to asyncio.open_connection
        kwargs.pop('proxy', None)
        return await super()._connect_tls(hostname, port, tls_verify=tls_verify, **kwargs)

class IRCClient(pydle.Client):
    """
    An IRC client rebuilt using the 'pydle' library for modern,
    asynchronous, and robust communication.
    """
    def __init__(self, nickname, channel, use_tor=False):
        # We pass the feature classes directly to the constructor.
        # This is more robust across different pydle versions.
        feature_list = [
            pydle.features.rfc1459.RFC1459Support,
            pydle.features.ctcp.CTCPSupport,
            PatchedTLSSupport  # Use our patched TLS class
        ]
        super().__init__(nickname, realname='Anon-Framework User', features=feature_list)
        
        self.target_channel = channel
        self.use_tor = use_tor
        self.menu = Menu(self)
        self.servers = SERVERS
        self.is_connected = False
        self.identities = {}

    async def on_connect(self):
        """Called when the client has successfully connected to the server."""
        await super().on_connect()
        print(f"Successfully connected to {self.connection.hostname}.")
        self.is_connected = True
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
        print("\nDisconnected from server.")
        self.is_connected = False
        if not self.loop.is_closed():
             self.loop.stop()

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
        finally:
            if not self.loop.is_closed():
                self.loop.stop()

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
                tls_verify=False, # For simplicity
                encoding='utf-8',
                fallback_encodings=['latin-1', 'cp1252']
            )
            await self.run_forever()
        except Exception as e:
            print(f"Failed to connect: {e}")
        finally:
            if not self.loop.is_closed():
                self.loop.stop()

