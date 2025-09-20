class Menu:
    def __init__(self, client):
        self.client = client
        self.menus = {
            "main": self.main_menu,
            "channel": self.channel_menu,
            "server": self.server_menu,
            "nickname": self.nickname_menu,
            "identity": self.identity_menu,
        }
        self.current_menu = "main"

    def display_menu(self):
        """Displays the current menu."""
        self.menus.get(self.current_menu, self.main_menu)()

    def handle_choice(self, choice):
        """
        Handles the user's choice and returns a boolean indicating if the menu
        should remain active.
        """
        menu_handler = getattr(self, f"handle_{self.current_menu}_menu", None)
        if menu_handler:
            return menu_handler(choice)
        else:
            print("Invalid menu.")
            return True # Keep menu active on error

    def main_menu(self):
        """Displays the main menu."""
        print("\n--- Main Menu ---")
        print("1. Channel Navigation")
        print("2. Server Navigation")
        print("3. Nickname Management")
        print("4. Identity Management")
        print("5. Send Message")
        print("6. Disconnect")
        print("7. Exit Menu")

    def handle_main_menu(self, choice):
        """Handles the main menu choice."""
        if choice == "1":
            self.current_menu = "channel"
        elif choice == "2":
            self.current_menu = "server"
        elif choice == "3":
            self.current_menu = "nickname"
        elif choice == "4":
            self.current_menu = "identity"
        elif choice == "5":
            message = input("Enter message to send: ")
            self.client.send_message(message)
        elif choice == "6":
            self.client.disconnect()
        elif choice == "7":
            return False  # Signal to exit the menu loop
        else:
            print("Invalid choice.")
        return True # Keep menu active by default

    def channel_menu(self):
        """Displays the channel navigation menu."""
        print("\n--- Channel Menu ---")
        print(f"Current Channel: {self.client.channel}")
        print("1. Join Channel")
        print("2. Leave Channel")
        print("3. List Channels")
        print("4. Search Channels")
        print("5. Back to Main Menu")

    def handle_channel_menu(self, choice):
        """Handles the channel menu choice."""
        if choice == "1":
            new_channel = input("Enter channel to join: ")
            self.client.join_channel(new_channel)
        elif choice == "2":
            self.client.leave_channel()
        elif choice == "3":
            self.client.list_channels()
        elif choice == "4":
            query = input("Enter search query: ")
            self.client.search_channels(query)
        elif choice == "5":
            self.current_menu = "main"
        else:
            print("Invalid choice.")
        return True # Always keep menu active from this submenu

    def server_menu(self):
        """Displays the server navigation menu."""
        print("\n--- Server Menu ---")
        print(f"Current Server: {self.client.server}")
        print("1. Connect to Server")
        print("2. Disconnect from Server")
        print("3. Back to Main Menu")

    def handle_server_menu(self, choice):
        """Handles the server menu choice."""
        if choice == "1":
            new_server = input("Enter server to connect to: ")
            new_port = int(input("Enter port: "))
            # This is a placeholder as switching servers like this is complex.
            # A full implementation would tear down the reactor and restart.
            print("Server switching is not fully implemented in this version.")
        elif choice == "2":
            self.client.disconnect()
        elif choice == "3":
            self.current_menu = "main"
        else:
            print("Invalid choice.")
        return True # Always keep menu active

    def nickname_menu(self):
        """Displays the nickname management menu."""
        print("\n--- Nickname Menu ---")
        print(f"Current Nickname: {self.client.connection.get_nickname()}")
        print("1. Change Nickname")
        print("2. Back to Main Menu")

    def handle_nickname_menu(self, choice):
        """Handles the nickname menu choice."""
        if choice == "1":
            new_nickname = input("Enter new nickname: ")
            self.client.change_nickname(new_nickname)
        elif choice == "2":
            self.current_menu = "main"
        else:
            print("Invalid choice.")
        return True # Always keep menu active

    def identity_menu(self):
        """Displays the identity management menu."""
        print("\n--- Identity Menu ---")
        print("1. Save Current Identity")
        print("2. Load Identity")
        print("3. Back to Main Menu")

    def handle_identity_menu(self, choice):
        """Handles the identity menu choice."""
        if choice == "1":
            identity_name = input("Enter name for this identity: ")
            # This is a placeholder for a more robust identity management system.
            print(f"Identity '{identity_name}' saved (placeholder).")
        elif choice == "2":
            print("Loading identity (placeholder).")
        elif choice == "3":
            self.current_menu = "main"
        else:
            print("Invalid choice.")
        return True # Always keep menu active

