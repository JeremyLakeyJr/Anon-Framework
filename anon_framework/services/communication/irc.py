import irc.client
import irc.connection
import irc.strings
import threading
import sys
import ssl
import socks
import socket
from .menu import Menu
from anon_framework.config.servers import SERVERS
from jaraco.stream.buffer import LineBuffer

class RobustLineBuffer(LineBuffer):
    """
    A custom line buffer that is initialized with a 'replace' error handling
    strategy. This prevents the client from crashing when it encounters
    byte sequences that are not valid UTF-8.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = 'replace'

class CustomServerConnection(irc.client.ServerConnection):
    """
    A server connection that uses our RobustLineBuffer class to handle
    all incoming data, thus preventing decoding-related crashes.
    """
    buffer_class = RobustLineBuffer

class IRCClient:
    """
    An IRC client using the 'irc' library with optional Tor support.
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
        
        self.reactor = irc.client.Reactor()
        # Use our custom connection class which uses the robust buffer.
        self.reactor.server_class = CustomServerConnection
        self.connection = None
        self.reactor_running = False

    def on_welcome(self, connection, event):
        """Called when the server sends the initial welcome message."""
        print(f"Successfully connected to {self.server}.")
        self.is_connected = True
        if self.channel:
            print(f"Joining channel {self.channel}...")
            connection.join(self.channel)
        # This will be printed after the MOTD
        # print("\n--- You are now in the channel. Type messages and press Enter to send. ---")
        # print("--- Type /menu to access the options menu. ---")

    def on_disconnect(self, connection, event):
        """Called when disconnected from the server."""
        print(f"\nDisconnected from server: {event.arguments[0]}")
        self.is_connected = False
        # This will stop the reactor.process_forever() loop
        self.reactor.disconnect_all()

    def on_nicknameinuse(self, connection, event):
        """Called when the chosen nickname is already in use."""
        current_nick = connection.get_nickname()
        new_nick = current_nick + "_"
        print(f"Nickname '{current_nick}' is already in use. Trying '{new_nick}'.")
        connection.nick(new_nick)

    def on_pubmsg(self, connection, event):
        """Called on a public message in a channel."""
        # We don't want to print our own messages back to ourselves.
        if not irc.strings.are_equal(event.source.nick, connection.get_nickname()):
            # Use carriage return to overwrite the current input line
            sys.stdout.write('\r' + ' ' * 80 + '\r') 
            print(f"<{event.source.nick}> {event.arguments[0]}")
            # Reprint the input prompt
            sys.stdout.write(f"[{self.channel or ''}]> ")
            sys.stdout.flush()

    def on_server_message(self, connection, event):
        """Prints generic server messages, like the MOTD."""
        if event.arguments:
            # The second argument is usually the text content.
            print(f"[Server] {event.arguments[-1]}")

    def on_endofmotd(self, connection, event):
        """Called when the MOTD has been fully received."""
        print("\n--- You are now in the channel. Type messages and press Enter to send. ---")
        print("--- Type /menu to access the options menu. ---")


    def on_list(self, connection, event):
        """Called for each item in a channel list."""
        args = event.arguments
        channel = args[1] if len(args) > 1 else "Unknown Channel"
        users = args[2] if len(args) > 2 else "N/A"
        topic = args[3] if len(args) > 3 else ""
        print(f"Channel: {channel}, Users: {users}, Topic: {topic}")

    def on_listend(self, connection, event):
        """Called when the channel list is complete."""
        print("--- End of channel list ---")

    def send_raw_command(self, command):
        """Sends a raw command string to the server."""
        if self.is_connected:
            print(f"--> {command}")
            self.connection.send_raw(command)
        else:
            print("You are not connected to a server.")

    def send_message(self, message):
        """Sends a message to the current channel."""
        if self.is_connected and self.channel:
            self.connection.privmsg(self.channel, message)
        else:
            print("You are not in a channel. Use the menu to join one.")

    def list_channels(self):
        """Requests a list of all channels from the server."""
        if self.is_connected:
            print("Requesting channel list from server...")
            self.connection.list()

    def search_channels(self, query):
        """Searches for channels matching a query."""
        if self.is_connected:
            print(f"Searching for channels matching '{query}'...")
            self.connection.list([f"*{query}*"])

    def disconnect(self):
        """Disconnects the client from the server."""
        if self.is_connected:
            self.is_connected = False
            self.connection.disconnect("User disconnected.")
            self.reactor.process_once(0.1)

    def join_channel(self, channel):
        """Joins a new IRC channel."""
        if self.is_connected:
            if not channel.startswith("#"):
                channel = "#" + channel
            self.channel = channel
            self.connection.join(channel)
            print(f"Joining {channel}...")

    def leave_channel(self):
        """Leaves the current channel."""
        if self.is_connected and self.channel:
            self.connection.part(self.channel)
            print(f"Leaving {self.channel}")
            self.channel = None

    def change_nickname(self, nickname):
        """Changes the client's nickname."""
        if self.is_connected:
            self.connection.nick(nickname)
            self.nickname = nickname

    def select_server(self):
        """Prompts the user to select a server from the list."""
        print("Please select a server to connect to:")
        for i, server in enumerate(self.servers):
            print(f"{i+1}. {server['name']} ({server['host']}:{server['port']})")

    def input_loop(self):
        """The main loop for handling user input."""
        while not self.is_connected:
            threading.Event().wait(0.5)
            if not self.reactor_running:
                return

        try:
            while self.is_connected:
                prompt = f"[{self.channel or 'No Channel'}]> "
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
                    command = message.split(' ', 1)[1]
                    self.send_raw_command(command)
                elif message.startswith('/'):
                    print(f"Unknown command: '{message}'. Did you mean /menu or /raw?")
                else:
                    self.send_message(message)

        except (KeyboardInterrupt, EOFError):
            print("\nDisconnecting...")
            self.disconnect()

    def start(self):
        """Starts the IRC client, including server selection and connection."""
        custom_nickname = input(f"Enter your nickname (default: {self.nickname}): ").strip()
        if custom_nickname:
            self.nickname = custom_nickname
            
        self.select_server()
        while True:
            try:
                choice = int(input("Enter your choice: "))
                if 1 <= choice <= len(self.servers):
                    server_info = self.servers[choice - 1]
                    self.server = server_info["host"]
                    self.port = server_info["port"]
                    break
            except (ValueError, EOFError):
                pass
            print("Invalid choice. Please try again.")

        server_info = next((s for s in self.servers if s["host"] == self.server), None)
        ssl_enabled = server_info.get("ssl", False)
        
        connect_factory = irc.connection.Factory()
        if ssl_enabled:
            context = ssl.create_default_context()
            ssl_wrapper = lambda sock: context.wrap_socket(sock, server_hostname=self.server)
            connect_factory = irc.connection.Factory(wrapper=ssl_wrapper)

        if self.use_tor:
            print("Connecting to IRC via Tor...")
            socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
            irc.connection.socket = socks.socksocket
        
        try:
            server_instance = self.reactor.server()
            self.connection = server_instance.connect(
                server=self.server,
                port=self.port,
                nickname=self.nickname,
                connect_factory=connect_factory
            )
        except irc.client.ServerConnectionError as x:
            print(f"Error connecting to server: {x}")
            return

        # Add all the event handlers
        self.connection.add_global_handler("welcome", self.on_welcome, -10)
        self.connection.add_global_handler("disconnect", self.on_disconnect)
        self.connection.add_global_handler("nicknameinuse", self.on_nicknameinuse)
        self.connection.add_global_handler("pubmsg", self.on_pubmsg)
        self.connection.add_global_handler("list", self.on_list)
        self.connection.add_global_handler("listend", self.on_listend)
        
        # Add handlers for server info and MOTD
        self.connection.add_global_handler("motd", self.on_server_message)
        self.connection.add_global_handler("motdstart", self.on_server_message)
        self.connection.add_global_handler("endofmotd", self.on_endofmotd)
        
        input_thread = threading.Thread(target=self.input_loop, daemon=True)
        input_thread.start()

        print(f"Connecting to {self.server}:{self.port}...")
        try:
            self.reactor_running = True
            self.reactor.process_forever()
        finally:
            self.reactor_running = False

