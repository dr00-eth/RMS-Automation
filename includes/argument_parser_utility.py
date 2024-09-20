import argparse

def create_base_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("username", help="Your RMS Cloud username")
    parser.add_argument("password", help="Your RMS Cloud password")
    parser.add_argument("--debug", action="store_true", help="Runs in training mode")
    return parser

def add_property_arguments(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("property", help="The property to automate, must match dropdown exactly")
    parser.add_argument("--start", type=int, default=1, help="Starting site number (default: 1)")
    return parser