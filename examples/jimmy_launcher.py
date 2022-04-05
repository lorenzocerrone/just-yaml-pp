from plain_yaml_example import main, parser
from jimmy import Jimmy


if __name__ == '__main__':
    args = parser()
    jimmy = Jimmy(args.config)
    jimmy.grid_launcher(main)

