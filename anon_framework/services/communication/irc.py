import pydle
import asyncio
import sys
import threading
from .menu import Menu
from anon_framework.config.servers import SERVERS

class PydleBot(pydle.Client):
    """
    The underlying Pydle client implementation. This class handles the
    raw IRC protocol events and calls back to the main IRCClient class.
    """
    def __init__(self, nickname, realname, event_handler):
        super().__init__(nickname, realname=realname, eventloop=event_handler.loop)
        self.event_handler = event_handler

    async def on_connect(self):
        await super().on_connect()
        await self.event_handler.on_welcome()

    async def on_channel_message(self, channel, nickname, message):
        await self.event_handler.on_pubmsg(nickname, message)

    async def on_nickname_in_use(self, nickname):
        # Pydle automatically tries another nick, but we can log it.
        new_nickname = await super().on_nickname_in_use(nickname)
        await self.event_handler.on_nicknameinuse(nickname, new_nickname)

    async def on_raw_motd(self, message):
        # The MOTD is split into parts; this handles each part.
        await self.event_handler.on_server_message(message)

    async def on_list_item(self, channel, user_count, topic):
        await self.event_handler.on_list(channel, user_count, topic)
    
    async def on_list_end(self, channel):
        await self.event_handler.on_listend()

class IRCClient:
    """
    Manages the IRC client state and user interaction. This is a wrapper
    around the PydleBot to separate application logic from protocol logic.
    """
    def __init__(self, nickname, channel, use_tor=False):
        self.server = None
        self.port = None
        self.nickname = nickname
        self.channel = channel
        self.use_tor = use_tor
        self.is_connected = False
        self.menu = Menu(self)
        self.servers = SERVERS
        self.identities = {}
        
        self.loop = asyncio.new_event_loop()
        self.client = PydleBot(nickname, realname='Anon-Framework User', event_handler=self)

    # Event handlers called by PydleBot
    async def on_welcome(self):
        print(f"Successfully connected to {self.server}.")
        self.is_connected = True
        if self.channel:
            print(f"Joining channel {self.channel}...")
            await self.client.join(self.channel)
        print("\n--- You are now in the channel. Type messages and press Enter to send. ---")
        print("--- Type /menu to access the options menu. ---")
    
    async def on_nicknameinuse(self, old, new):
        print(f"Nickname '{old}' was in use. Changed to '{new}'.")
        self.nickname = new

    async def on_pubmsg(self, nickname, message):
        if nickname != self.client.nickname:
            sys.stdout.write('\r' + ' ' * 80 + '\r') 
            print(f"<{nickname}> {message}")
            sys.stdout.write(f"[{self.channel or ''}]> ")
            sys.stdout.flush()

    async def on_server_message(self, message):
        print(f"[Server] {message}")

    async def on_list(self, channel, users, topic):
        print(f"Channel: {channel}, Users: {users}, Topic: {topic}")

    async def on_listend(self):
        print("--- End of channel list ---")

    # User-facing action methods (can be called from input thread)
    async def send_raw_command(self, command):
        if self.is_connected:
            print(f"--> {command}")
            await self.client.raw(command)
        else:
            print("You are not connected to a server.")

    async def send_message(self, message):
        if self.is_connected and self.channel:
            await self.client.message(self.channel, message)
        else:
            print("You are not in a channel. Use the menu to join one.")

    async def list_channels_async(self):
        if self.is_connected:
            print("Requesting channel list from server...")
            await self.client.list()

    def list_channels(self):
        asyncio.run_coroutine_threadsafe(self.list_channels_async(), self.loop)

    async def search_channels_async(self, query):
        if self.is_connected:
            print(f"Searching for channels matching '{query}'...")
            await self.client.list(f"*{query}*")

    def search_channels(self, query):
        asyncio.run_coroutine_threadsafe(self.search_channels_async(query), self.loop)

    def disconnect(self):
        if self.is_connected:
            print("Disconnecting...")
            self.is_connected = False
            asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)

    def join_channel(self, channel):
        if not channel.startswith("#"):
            channel = "#" + channel
        self.channel = channel
        asyncio.run_coroutine_threadsafe(self.client.join(channel), self.loop)
        print(f"Joining {channel}...")

    def leave_channel(self):
        if self.channel:
            asyncio.run_coroutine_threadsafe(self.client.part(self.channel), self.loop)
            print(f"Leaving {self.channel}")
            self.channel = None

    def change_nickname(self, nickname):
        self.nickname = nickname
        asyncio.run_coroutine_threadsafe(self.client.set_nickname(nickname), self.loop)

    def select_server(self):
        print("Please select a server to connect to:")
        for i, server in enumerate(self.servers):
            print(f"{i+1}. {server['name']} ({server['host']}:{server['port']})")

    def input_loop(self):
        while not self.is_connected and self.client.is_connected():
            threading.Event().wait(0.5)

        try:
            while self.is_connected:
                prompt = f"[{self.channel or 'No Channel'}]> "
                message = input(prompt)
                
                if not self.is_connected: break

                if message == '/menu':
                    self.menu.current_menu = "main"
                    while self.is_connected:
                        self.menu.display_menu()
                        choice = input("Enter your choice: ")
                        if not self.menu.handle_choice(choice):
                            print("\n--- Exited menu. You are back in the channel. ---")
                            break
                elif message.startswith('/raw '):
                    command = message.split(' ', 1)[1]
                    asyncio.run_coroutine_threadsafe(self.send_raw_command(command), self.loop)
                elif message.startswith('/'):
                    print(f"Unknown command: '{message}'. Did you mean /menu or /raw?")
                else:
                    asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
        except (KeyboardInterrupt, EOFError):
            self.disconnect()

    def start(self):
        custom_nickname = input(f"Enter your nickname (default: {self.nickname}): ").strip()
        if custom_nickname:
            self.nickname = custom_nickname
            self.client.nickname = custom_nickname
            
        self.select_server()
        while True:
            try:
                choice = int(input("Enter your choice: "))
                if 1 <= choice <= len(self.servers):
                    server_info = self.servers[choice - 1]
                    self.server, self.port = server_info["host"], server_info["port"]
                    break
            except (ValueError, EOFError): pass
            print("Invalid choice.")

        server_info = next((s for s in self.servers if s["host"] == self.server), None)
        ssl_enabled = server_info.get("ssl", False)
        
        proxy = pydle.protocol.SOCKS5Proxy('127.0.0.1', 9050) if self.use_tor else None
        
        input_thread = threading.Thread(target=self.input_loop, daemon=True)
        input_thread.start()

        async def run_client():
            try:
                await self.client.connect(
                    hostname=self.server, port=self.port,
                    tls=ssl_enabled, tls_verify=False, # tls_verify=False for simplicity
                    proxy=proxy
                )
            except Exception as e:
                print(f"Failed to connect: {e}")
        
        print(f"Connecting to {self.server}:{self.port}...")
        self.loop.run_until_complete(run_client())
