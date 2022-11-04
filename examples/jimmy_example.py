from jimmy import JimmyLauncher
from plain_yaml_example import main


def gcn(hidden_size: int,
        input_size: int,
        output_size: int):
    print(f' -gcn, {hidden_size=}, {input_size=}, {output_size=}')
    ...
    return 'result'


if __name__ == '__main__':
    jimmy_launcher = JimmyLauncher()
    # jimmy_launcher.simple_launcher(main)
    jimmy_launcher.auto_launcher(main)

