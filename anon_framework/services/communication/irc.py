import socket
import socks

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
            self.send_command(f"JOIN {self.channel}")
            print(f"Connected to {self.server} and joined {self.channel}")
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
            self.socket.send(f"{command}\r\n".encode("utf-8"))

    def send_message(self, message):
        """
        Sends a message to the channel.
        """
        self.send_command(f"PRIVMSG {self.channel} :{message}")

    def start(self):
        """
        Starts the main message parsing loop.
        """
        if not self.is_connected:
            self.connect()

        while self.is_connected:
            try:
                response = self.socket.recv(2048).decode("utf-8")
                if response:
                    print(response, end='')
                    # Respond to PING requests
                    if response.startswith("PING"):
                        self.send_command(f"PONG {response.split(':')[1]}")
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.disconnect()
                break

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
