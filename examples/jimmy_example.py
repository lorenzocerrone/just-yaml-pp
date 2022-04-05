from jimmy import Jimmy
from plain_yaml_example import main, parser


if __name__ == '__main__':
    args = parser()
    main_config = Jimmy(args.config).config
    main(**main_config)
