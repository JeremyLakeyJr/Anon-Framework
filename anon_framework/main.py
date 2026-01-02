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
from anon_framework.utils.helpers import run_command, validate_input
from anon_framework.configuration import get_config
from anon_framework.utils.logging import setup_logging, get_logger


def handle_vpn_command(args):
    """Handles all VPN-related commands."""
    logger = get_logger('vpn')
    
    vpn_map = {
        'nord': NordVPN,
        'mullvad': MullvadVPN,
        'tor': TorVPN,
    }
    
    if args.provider not in vpn_map:
        logger.error(f"Invalid VPN provider: {args.provider}")
        print(f"Error: Invalid VPN provider '{args.provider}'. Choices are {list(vpn_map.keys())}.")
        sys.exit(1)
    
    try:
        vpn_client = vpn_map[args.provider]()
        
        if args.vpn_action == 'connect':
            logger.info(f"Connecting to {args.provider}")
            success = vpn_client.connect()
            sys.exit(0 if success else 1)
        elif args.vpn_action == 'disconnect':
            logger.info(f"Disconnecting from {args.provider}")
            success = vpn_client.disconnect()
            sys.exit(0 if success else 1)
        elif args.vpn_action == 'status':
            status = vpn_client.get_status()
            print(status)
            logger.info(f"Status check for {args.provider}: {status}")
        else:
            logger.error(f"Invalid VPN action: {args.vpn_action}")
            print(f"Error: Invalid VPN action '{args.vpn_action}'.")
            sys.exit(1)
    except Exception as e:
        logger.exception(f"Error handling VPN command: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def handle_services_command(args):
    """Handles all service-related commands."""
    logger = get_logger('services')
    config = get_config()
    
    try:
        if args.service == 'qbittorrent':
            # Get credentials from config
            qb_config = config.get('qbittorrent', {})
            client = QBittorrentClient(
                host=qb_config.get('host', 'localhost'),
                port=qb_config.get('port', 8080),
                username=qb_config.get('username'),
                password=qb_config.get('password')
            )
            
            if args.service_action == 'search':
                if not args.query:
                    print("Error: The 'search' action requires a query.")
                    sys.exit(1)
                
                query = " ".join(args.query)
                logger.info(f"Searching qBittorrent for: {query}")
                results = client.search(query)
                
                if not results:
                    print("No results found.")
                else:
                    for res in results:
                        print(f"Name: {res.get('fileName')}")
                        print(f"Size: {res.get('fileSize')}")
                        print(f"Seeds: {res.get('nbSeeders')}")
                        print(f"Link: {res.get('fileUrl')}")
                        print("---")
            else:
                print(f"Error: Invalid qBittorrent action '{args.service_action}'.")
                sys.exit(1)

        elif args.service == 'i2p':
            client = I2PService()
            
            if args.service_action == 'start':
                logger.info("Starting I2P service")
                success = client.start()
                sys.exit(0 if success else 1)
            elif args.service_action == 'stop':
                logger.info("Stopping I2P service")
                success = client.stop()
                sys.exit(0 if success else 1)
            elif args.service_action == 'status':
                status = client.get_status()
                print(status)
                logger.info(f"I2P status: {status}")
            elif args.service_action == 'search':
                if not args.query:
                    print("Error: The 'search' action requires a query.")
                    sys.exit(1)
                query = " ".join(args.query)
                logger.info(f"Searching I2P for: {query}")
                client.search_torrents(query)
            else:
                print(f"Error: Invalid I2P action '{args.service_action}'.")
                sys.exit(1)
        else:
            logger.error(f"Invalid service: {args.service}")
            print(f"Error: Invalid service '{args.service}'.")
            sys.exit(1)
    except Exception as e:
        logger.exception(f"Error handling services command: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def handle_privacy_command(args):
    """Handles all privacy-related commands."""
    logger = get_logger('privacy')
    
    try:
        if args.privacy_action == 'disable-telemetry':
            logger.info("Disabling OS telemetry")
            disable_telemetry()
        elif args.privacy_action == 'start-tor':
            print("Starting Tor service...")
            logger.info("Starting Tor service")
            stdout, stderr, code = run_command(['sudo', 'systemctl', 'start', 'tor'], timeout=30)
            if code == 0:
                print("Tor service started successfully.")
                logger.info("Tor service started successfully")
            else:
                print(f"Error starting Tor service:\n{stderr}")
                logger.error(f"Failed to start Tor service: {stderr}")
        elif args.privacy_action == 'stop-tor':
            print("Stopping Tor service...")
            logger.info("Stopping Tor service")
            stdout, stderr, code = run_command(['sudo', 'systemctl', 'stop', 'tor'], timeout=30)
            if code == 0:
                print("Tor service stopped successfully.")
                logger.info("Tor service stopped successfully")
            else:
                print(f"Error stopping Tor service:\n{stderr}")
                logger.error(f"Failed to stop Tor service: {stderr}")
        else:
            logger.error(f"Invalid privacy action: {args.privacy_action}")
            print(f"Error: Invalid privacy action '{args.privacy_action}'.")
            sys.exit(1)
    except Exception as e:
        logger.exception(f"Error handling privacy command: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def handle_communicate_command(args):
    """Handles all communication-related commands."""
    logger = get_logger('communicate')
    config = get_config()
    
    try:
        if args.protocol == 'irc':
            # Validate nickname
            nickname = args.nickname
            if not validate_input(nickname, max_length=30):
                print("Error: Invalid nickname. Use alphanumeric characters, dash, underscore only.")
                logger.error(f"Invalid nickname provided: {nickname}")
                sys.exit(1)
            
            # Validate channel
            channel = args.channel
            if not channel.startswith('#'):
                channel = '#' + channel
            if not validate_input(channel[1:], max_length=50):  # Remove # for validation
                print("Error: Invalid channel name.")
                logger.error(f"Invalid channel provided: {channel}")
                sys.exit(1)
            
            logger.info(f"Starting IRC client - nickname: {nickname}, channel: {channel}, tor: {args.tor}")
            client = IRCClient(nickname, channel, use_tor=args.tor)
            try:
                # Use asyncio.run() to properly execute the async start method.
                asyncio.run(client.start())
            except KeyboardInterrupt:
                print("\nClient shut down by user.")
                logger.info("IRC client shut down by user")
        else:
            logger.error(f"Invalid communication protocol: {args.protocol}")
            print(f"Error: Invalid communication protocol '{args.protocol}'.")
            sys.exit(1)
    except Exception as e:
        logger.exception(f"Error handling communicate command: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main entry point for the Anon-Framework CLI."""
    # Parse config and setup logging first
    config = get_config()
    log_config = config.get('logging', {})
    setup_logging(
        level=log_config.get('level', 'INFO'),
        log_file=log_config.get('file'),
        console=log_config.get('console', True)
    )
    
    logger = get_logger('main')
    logger.info("Starting Anon-Framework CLI")
    
    parser = argparse.ArgumentParser(
        description="A cross-platform framework for enhancing user anonymity and privacy.",
        epilog="For more information, visit: https://github.com/JeremyLakeyJr/Anon-Framework"
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
    irc_config = config.get('irc', {})
    communicate_parser.add_argument(
        '--nickname',
        default=irc_config.get('default_nickname', 'anon_framework_user'),
        help='Your nickname'
    )
    communicate_parser.add_argument(
        '--channel',
        default=irc_config.get('default_channel', '#anon-framework'),
        help='The channel to join'
    )
    communicate_parser.add_argument('--tor', action='store_true', help='Use Tor for the connection')
    communicate_parser.set_defaults(func=handle_communicate_command)

    try:
        args = parser.parse_args()
        args.func(args)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Unexpected error in main: {e}")
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


