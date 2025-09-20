import argparse
import sys
import asyncio
from anon_framework.vpn.nord import NordVPN
from anon_framework.vpn.mullvad import MullvadVPN
from anon_framework.vpn.tor import TorVPN
from anon_framework.services.qbittorrent import QBittorrentClient
from anon_framework.services.i2p import I2PService
from anon_framework.privacy.telemetry import disable_telemetry
from anon_framework.services.communication.irc import IRCClient
from anon_framework.utils.helpers import run_command

def handle_vpn_command(args):
    """Handles all VPN-related commands."""
    vpn_map = {
        'nord': NordVPN(),
        'mullvad': MullvadVPN(),
        'tor': TorVPN(),
    }
    
    if args.provider not in vpn_map:
        print(f"Error: Invalid VPN provider '{args.provider}'. Choices are {list(vpn_map.keys())}.")
        sys.exit(1)
        
    vpn_client = vpn_map[args.provider]
    
    if args.vpn_action == 'connect':
        vpn_client.connect()
    elif args.vpn_action == 'disconnect':
        vpn_client.disconnect()
    elif args.vpn_action == 'status':
        print(vpn_client.get_status())
    else:
        print(f"Error: Invalid VPN action '{args.vpn_action}'.")
        sys.exit(1)

def handle_services_command(args):
    """Handles all service-related commands."""
    if args.service == 'qbittorrent':
        # NOTE: You may need to pass credentials from a config file in a real app
        client = QBittorrentClient() 
        if args.service_action == 'search':
            if not args.query:
                print("Error: The 'search' action requires a query.")
                sys.exit(1)
            results = client.search(" ".join(args.query))
            # Basic print of results
            for res in results:
                print(f"Name: {res.get('fileName')}\nSize: {res.get('fileSize')}\nSeeds: {res.get('nbSeeders')}\nLink: {res.get('fileUrl')}\n---")

    elif args.service == 'i2p':
        client = I2PService()
        if args.service_action == 'start':
            client.start()
        elif args.service_action == 'stop':
            client.stop()
        elif args.service_action == 'status':
            print(client.get_status())
        elif args.service_action == 'search':
             if not args.query:
                print("Error: The 'search' action requires a query.")
                sys.exit(1)
             client.search_torrents(" ".join(args.query))
    else:
        print(f"Error: Invalid service '{args.service}'.")
        sys.exit(1)

def handle_privacy_command(args):
    """Handles all privacy-related commands."""
    if args.privacy_action == 'disable-telemetry':
        disable_telemetry()
    elif args.privacy_action == 'start-tor':
        print("Starting Tor service...")
        stdout, stderr, code = run_command(['sudo', 'systemctl', 'start', 'tor'])
        if code == 0:
            print("Tor service started successfully.")
        else:
            print(f"Error starting Tor service:\n{stderr}")
    elif args.privacy_action == 'stop-tor':
        print("Stopping Tor service...")
        stdout, stderr, code = run_command(['sudo', 'systemctl', 'stop', 'tor'])
        if code == 0:
            print("Tor service stopped successfully.")
        else:
            print(f"Error stopping Tor service:\n{stderr}")
    else:
        print(f"Error: Invalid privacy action '{args.privacy_action}'.")
        sys.exit(1)

def handle_communicate_command(args):
    """Handles all communication-related commands."""
    if args.protocol == 'irc':
        client = IRCClient(args.nickname, args.channel, use_tor=args.tor)
        try:
            # Use asyncio.run() to properly execute the async start method.
            asyncio.run(client.start())
        except KeyboardInterrupt:
            print("\nClient shut down by user.")
    else:
        print(f"Error: Invalid communication protocol '{args.protocol}'.")
        sys.exit(1)

def main():
    """Main entry point for the Anon-Framework CLI."""
    parser = argparse.ArgumentParser(
        description="A cross-platform framework for enhancing user anonymity and privacy."
    )
    subparsers = parser.add_subparsers(dest='command', required=True, help='Main command')

    # VPN Parser
    vpn_parser = subparsers.add_parser('vpn', help='Manage VPN connections')
    vpn_parser.add_argument('provider', choices=['nord', 'mullvad', 'tor'], help='The VPN provider')
    vpn_parser.add_argument('vpn_action', choices=['connect', 'disconnect', 'status'], help='Action to perform')
    vpn_parser.set_defaults(func=handle_vpn_command)

    # Services Parser
    services_parser = subparsers.add_parser('services', help='Manage external services')
    services_parser.add_argument('service', choices=['qbittorrent', 'i2p'], help='The service to manage')
    services_parser.add_argument('service_action', help='Action to perform (e.g., search, start, stop)')
    services_parser.add_argument('query', nargs='*', help='Search query (for search action)')
    services_parser.set_defaults(func=handle_services_command)

    # Privacy Parser
    privacy_parser = subparsers.add_parser('privacy', help='Manage privacy settings')
    privacy_parser.add_argument('privacy_action', choices=['disable-telemetry', 'start-tor', 'stop-tor'], help='Action to perform')
    privacy_parser.set_defaults(func=handle_privacy_command)

    # Communication Parser
    communicate_parser = subparsers.add_parser('communicate', help='Manage communication clients')
    communicate_parser.add_argument('protocol', choices=['irc'], help='The communication protocol')
    communicate_parser.add_argument('--nickname', default='anon_framework_user', help='Your nickname')
    communicate_parser.add_argument('--channel', default='#anon-framework', help='The channel to join')
    communicate_parser.add_argument('--tor', action='store_true', help='Use Tor for the connection')
    communicate_parser.set_defaults(func=handle_communicate_command)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

