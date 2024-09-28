import argparse

class RawTextArgumentDefaultsHelpFormatter(argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass

class PasswordAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)

def create_base_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description, formatter_class=RawTextArgumentDefaultsHelpFormatter)
    parser.add_argument("username", help="Your Newbook username")
    parser.add_argument("password", help="Your Newbook password", action=PasswordAction)
    parser.add_argument("--debug", action="store_true", help="Runs in debug mode")
    return parser

def add_property_arguments(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("property", help="The property to automate, must match dropdown exactly")
    parser.add_argument("--start", type=int, default=1, help="Starting site number (default: 1)")
    return parser