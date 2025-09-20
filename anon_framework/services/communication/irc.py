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
        self.reactor_running = False

    def on_welcome(self, connection, event):
        """Called when the server sends the initial welcome message."""
        print(f"Successfully connected to {self.server}.")
        self.is_connected = True
        if self.channel:
            print(f"Joining channel {self.channel}...")
            connection.join(self.channel)
        print("\n--- You are now in the channel. Type messages and press Enter to send. ---")
        print("--- Type /menu to access the options menu. ---")

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
            # Use carriage return to overwrite the current input line
            sys.stdout.write('\r' + ' ' * 80 + '\r') 
            print(f"<{event.source.nick}> {event.arguments[0]}")
            # Reprint the input prompt
            sys.stdout.write(f"[{self.channel or ''}]> ")
            sys.stdout.flush()


    def on_list(self, connection, event):
        """Called for each item in a channel list."""
        # The arguments list from the server can vary, especially if a topic is not set.
        # Format is typically: ['<nickname>', '<channel>', '<user_count>', '<topic>']
        args = event.arguments
        channel = args[1] if len(args) > 1 else "Unknown Channel"
        users = args[2] if len(args) > 2 else "N/A"
        topic = args[3] if len(args) > 3 else ""
        print(f"Channel: {channel}, Users: {users}, Topic: {topic}")

    def on_listend(self, connection, event):
        """Called when the channel list is complete."""
        print("--- End of channel list ---")

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

    def input_loop(self):
        """The main loop for handling user input."""
        # Wait until the connection is established before starting.
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
                    self.menu.current_menu = "main"  # Reset to main menu
                    # Start a loop to handle menu navigation
                    while self.is_connected:
                        self.menu.display_menu()
                        choice = input("Enter your choice: ")
                        # handle_choice will return False when the user wants to exit the menu
                        if not self.menu.handle_choice(choice):
                            print("\n--- Exited menu. You are back in the channel. ---")
                            break
                elif message.startswith('/'):
                    print(f"Unknown command: '{message}'. Did you mean /menu?")
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
        
        # Define connection parameters
        connect_factory = irc.connection.Factory()
        if ssl_enabled:
            context = ssl.create_default_context()
            # This lambda function ensures the server_hostname is passed for verification
            ssl_wrapper = lambda sock: context.wrap_socket(sock, server_hostname=self.server)
            connect_factory = irc.connection.Factory(wrapper=ssl_wrapper)

        if self.use_tor:
            print("Connecting to IRC via Tor...")
            socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
            # The irc library uses the default proxy, so we just need to patch the socket
            irc.connection.socket = socks.socksocket
        
        try:
            # Pass encoding parameters when creating the server instance
            server_instance = self.reactor.server(fallback_encoding='latin-1')
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
        
        # Start the input loop in a separate thread
        input_thread = threading.Thread(target=self.input_loop, daemon=True)
        input_thread.start()

        print(f"Connecting to {self.server}:{self.port}...")
        try:
            self.reactor_running = True
            self.reactor.process_forever()
        finally:
            self.reactor_running = False

