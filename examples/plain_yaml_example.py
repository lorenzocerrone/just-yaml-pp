import argparse
import yaml


def parser():
    args_parser = argparse.ArgumentParser(description='Generic Parser')
    args_parser.add_argument('--config', '-c', type=str, help='Path to the YAML experiments file', required=True)
    return args_parser.parse_args()


def get_loader(data_path: str, batch_size: int, features: int):
    print(f' -loader: {data_path=}, {batch_size=}, {features=}')
    ...
    return 'loader'


def get_optimizer(name, lr):
    print(f' -optimizer: {name=}, {lr=}')
    ...
    return 'optimizer'


def train_model(*args, name: str,
                hidden_size: int,
                input_size: int,
                output_size: int):
    print(f' -training: {name=}, {hidden_size=}, {input_size=}, {output_size=}')
    ...
    return 'result'


def logger(result: str, path: str):
    print(f' -saving: {result} to {path}')


def main(**config):
    print('Starting:')
    loader = get_loader(**config['loader'])
    optimizer = get_optimizer(**config['optimizer'])
    result = train_model(loader, optimizer, **config['model'])
    logger(result, path=config['logger']['path'])


if __name__ == '__main__':
    args = parser()
    with open(args.config, 'r') as f:
        main_config = yaml.safe_load(f)

    main(**main_config)
