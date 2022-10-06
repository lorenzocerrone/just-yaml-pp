import argparse
from pathlib import Path


def _try_cascade(value):
    try:
        return int(value)
    except:
        pass

    try:
        return float(value)
    except:
        pass

    return value


def _primitive_type_inference(args_dict):
    for key, value in args_dict.items():
        args_dict[key] = _try_cascade(value)
    return args_dict


def _parse_unknown_args(parser, unknown):
    for arg in unknown:
        if arg.startswith(("-", "--")):
            parser.add_argument(arg.split('=')[0])
    args = parser.parse_args()
    return args


def config_parser():
    parser = argparse.ArgumentParser(description='Jimmy Parser')
    parser.add_argument('--config', '-c', type=Path, help='Path to the YAML config file', required=True)
    _, unknown = parser.parse_known_args()
    args_dict = _parse_unknown_args(parser, unknown).__dict__
    config = args_dict.pop('config')
    args_dict = _primitive_type_inference(args_dict)
    return config, args_dict
