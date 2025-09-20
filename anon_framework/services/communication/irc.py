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
        self.connection = None

    def on_welcome(self, connection, event):
        """Called when the server sends the initial welcome message."""
        print(f"Successfully connected to {self.server}.")
        self.is_connected = True
        if self.channel:
            print(f"Joining channel {self.channel}...")
            connection.join(self.channel)

    def on_disconnect(self, connection, event):
        """Called when disconnected from the server."""
        print(f"Disconnected from server: {event.arguments[0]}")
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
            print(f"<{event.source.nick}> {event.arguments[0]}")

    def on_list(self, connection, event):
        """Called for each item in a channel list."""
        print(f"Channel: {event.arguments[1]}, Users: {event.arguments[2]}, Topic: {event.arguments[3]}")

    def on_listend(self, connection, event):
        """Called when the channel list is complete."""
        print("--- End of channel list ---")

    def send_message(self, message):
        """Sends a message to the current channel."""
        if self.is_connected:
            self.connection.privmsg(self.channel, message)
            # Print our own message to the console for a better user experience.
            print(f"<{self.connection.get_nickname()}> {message}")

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
            # Give the disconnect message a moment to be sent
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

    def menu_loop(self):
        """The main loop for handling user input from the menu."""
        # Wait until the connection is established before showing the menu.
        while not self.is_connected:
            threading.Event().wait(0.5)
            # If the reactor stops before connecting, exit the loop.
            if not self.reactor.is_running():
                return

        try:
            while self.is_connected:
                self.menu.display_menu()
                choice = input("Enter your choice: ")
                if not self.is_connected:
                    break
                self.menu.handle_choice(choice)
        except (KeyboardInterrupt, EOFError):
            print("\nDisconnecting...")
            self.disconnect()

    def start(self):
        """Starts the IRC client, including server selection and connection."""
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
        
        # Define connection parameters
        connect_factory = irc.connection.Factory()
        if ssl_enabled:
            context = ssl.create_default_context()
            connect_factory = irc.connection.Factory(wrapper=context.wrap_socket)

        if self.use_tor:
            print("Connecting to IRC via Tor...")
            socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
            # The irc library uses the default proxy, so we just need to patch the socket
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
        
        # Start the menu in a separate thread so it doesn't block the IRC client
        menu_thread = threading.Thread(target=self.menu_loop, daemon=True)
        menu_thread.start()

        print(f"Connecting to {self.server}:{self.port}...")
        self.reactor.process_forever()

