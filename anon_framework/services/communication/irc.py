import socket
import socks
import threading
import sys
from .menu import Menu

class IRCClient:
    """
    A basic IRC client with optional Tor support.
    """
    def __init__(self, server, port, nickname, channel, use_tor=False):
        self.server = server
        self.port = port
        self.nickname = nickname
        self.channel = channel
        self.use_tor = use_tor
        self.socket = None
        self.is_connected = False
        self.identities = {}
        self.lock = threading.Lock()
        self.menu = Menu(self)
        self.receive_thread = None

    def connect(self):
        """
        Connects to the IRC server, with an option to use Tor.
        """
        try:
            if self.use_tor:
                print("Connecting to IRC via Tor...")
                socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
                self.socket = socks.socksocket()
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            self.socket.connect((self.server, self.port))
            self.is_connected = True
            self.send_command(f"NICK {self.nickname}")
            self.send_command(f"USER {self.nickname} 0 * :{self.nickname}")
            self.join_channel(self.channel)
            print(f"Connected to {self.server}")
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
        except Exception as e:
            print(f"Error connecting to IRC server: {e}")
            self.disconnect()

    def disconnect(self):
        """
        Disconnects from the IRC server.
        """
        if self.socket:
            self.send_command("QUIT")
            self.socket.close()
            self.is_connected = False
            print("Disconnected from IRC server.")

    def send_command(self, command):
        """
        Sends a command to the IRC server.
        """
        if self.socket and self.is_connected:
            try:
                self.socket.send(f"{command}\r\n".encode("utf-8"))
            except (BrokenPipeError, OSError) as e:
                print(f"Connection error: {e}")
                self.disconnect()

    def send_message(self, message):
        """
        Sends a message to the channel.
        """
        self.send_command(f"PRIVMSG {self.channel} :{message}")

    def list_channels(self):
        """Lists all channels on the server."""
        self.send_command("LIST")
        print("Requesting channel list from server...")

    def search_channels(self, query):
        """Searches for channels matching the query."""
        self.send_command(f"LIST *{query}*")
        print(f"Searching for channels matching '{query}'...")

    def join_channel(self, channel):
        """Joins a new channel."""
        if self.channel:
            self.leave_channel()
        if not channel.startswith("#"):
            channel = "#" + channel
        self.channel = channel
        self.send_command(f"JOIN {self.channel}")
        print(f"Joined {self.channel}")

    def leave_channel(self):
        """Leaves the current channel."""
        self.send_command(f"PART {self.channel}")
        print(f"Left {self.channel}")
        self.channel = None

    def switch_server(self, server, port):
        """Switches to a new server."""
        self.disconnect()
        self.server = server
        self.port = port
        self.connect()

    def change_nickname(self, nickname):
        """Changes the nickname."""
        self.nickname = nickname
        self.send_command(f"NICK {self.nickname}")

    def save_identity(self, name):
        """Saves the current connection details as an identity."""
        self.identities[name] = {
            "server": self.server,
            "port": self.port,
            "nickname": self.nickname,
            "channel": self.channel,
        }
        print(f"Identity '{name}' saved.")

    def load_identity(self):
        """Loads a saved identity."""
        if not self.identities:
            print("No identities saved.")
            return

        print("Saved identities:")
        for name in self.identities:
            print(f"- {name}")
        
        name = input("Enter identity name to load: ")
        identity = self.identities.get(name)
        if identity:
            self.disconnect()
            self.server = identity["server"]
            self.port = identity["port"]
            self.nickname = identity["nickname"]
            self.channel = identity["channel"]
            self.connect()
        else:
            print("Invalid identity name.")

    def receive_messages(self):
        """Receives and prints messages from the server."""
        while self.is_connected:
            try:
                response = self.socket.recv(2048).decode("utf-8")
                if response:
                    with self.lock:
                        sys.stdout.write(response)
                        sys.stdout.flush()
                        # Respond to PING requests
                        if response.startswith("PING"):
                            self.send_command(f"PONG {response.split(':')[1]}")
            except Exception as e:
                with self.lock:
                    print(f"Error receiving message: {e}")
                self.disconnect()
                break

    def start(self):
        """
        Starts the main message parsing loop.
        """
        if not self.is_connected:
            self.connect()

        try:
            while self.is_connected:
                with self.lock:
                    self.menu.display_menu()
                
                choice = input("Enter your choice: ")
                with self.lock:
                    self.menu.handle_choice(choice)

        except KeyboardInterrupt:
            print("\nDisconnecting...")
            self.disconnect()
        except EOFError:
            print("\nDisconnecting...")
            self.disconnect()

def main():
    """
    Main function to run the IRC client.
    """
    server = "irc.libera.chat"
    port = 6667
    nickname = "anon_framework_user"
    channel = "#anon-framework"

    client = IRCClient(server, port, nickname, channel)
    client.start()

if __name__ == "__main__":
    main()
