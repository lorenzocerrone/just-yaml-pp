import argparse


def config_parser():
    _parser = argparse.ArgumentParser(description='Jimmy Parser')
    _parser.add_argument('--config', '-c', type=str, help='Path to the YAML config file', required=True)
    args = _parser.parse_args()
    return args
