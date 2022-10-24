from dataclasses import dataclass
from pathlib import Path, PosixPath
from jimmy.constructors.utils import generic_constructor
import time
from collections.abc import Mapping
import yaml
import itertools
import copy
from jimmy.constructors.math_constructors import build_range, build_lin_space, build_log_space, sum_nodes
from jimmy.constructors.path_constructors import home_path, unique_path, make_absolute, join_paths, make_path
from jimmy.constructors.path_constructors import join_paths_glob, here_path
from jimmy.constructors.basic_constructors import jimmy_constructor, time_stamp, join, jimmy_configurator_constructor
from jimmy.utils import config_parser
from jimmy.jimmy_map import JimmyMap, split_jimmy_map, GenericDict, Configurator
from functools import partial
from typing import Any, Callable


def touch_file_or_dir(path: Path):
    if path.exists():
        return None

    if path.suffix:
        touch_file_or_dir(path.parent)
        path.touch(exist_ok=True)
    else:
        path.mkdir(exist_ok=True, parents=True)


def merge_dict_inplace(a: GenericDict, b: GenericDict) -> GenericDict:
    assert type(a) == type(b), f'Types in the source dictionary {b} of type {type(b)} ' \
                               f'and target{a} of type {type(a)} must match.'
    for key, value in b.items():
        if isinstance(b.get(key), JimmyMap) and key in a:
            a[key] = merge_dict_inplace(a.get(key), b.get(key))
        else:
            a[key] = b[key]
    return a


def update_from_template(jimmy_config: GenericDict, config: GenericDict) -> GenericDict:
    if 'template' in jimmy_config:
        template = jimmy_config.get('template')
        config = merge_dict_inplace(template, config)
    return config


default_constructors = {'tag:yaml.org,2002:map': jimmy_constructor,
                        '!configurator': jimmy_configurator_constructor,
                        '!join': join,
                        '!time-stamp': time_stamp,
                        '!join-paths': join_paths,
                        '!glob': join_paths_glob,
                        '!home': home_path,
                        '!unique-path': unique_path,
                        '!path': make_path,
                        '!absolute-path': make_absolute,
                        '!sum': sum_nodes,
                        '!range': build_range,
                        '!log-space': build_log_space,
                        '!lin-space': build_lin_space
                        }


def _load(path: Path) -> GenericDict:
    with open(path, 'r') as f:
        config = yaml.full_load(f)
        return config


def load_node(loader, node) -> GenericDict:
    if isinstance(node, yaml.nodes.ScalarNode):
        value = node.value

    elif isinstance(node, yaml.nodes.SequenceNode):
        value = generic_constructor(loader, node)
        if len(value) == 1:
            value = value[0]
        else:
            raise ValueError('!load allows only for length 1 list as input.')
    else:
        raise ValueError('!load allows only for string or list inputs.')

    value = Path(value)
    if not value.exists():
        raise ValueError(f'!load cannot load {value}. File does not exists.')

    return _load(value)


def update_nested_dict(base: GenericDict, dict_key: str, dict_value: Any) -> GenericDict:
    keys = dict_key.split('/')
    key0, _key = keys[0], '/'.join(keys[1:])
    if len(keys) == 1:
        base = merge_dict_inplace(base, {key0: dict_value})
    else:
        if key0 not in base:
            base = merge_dict_inplace(base, {key0: {}})
        up_config = update_nested_dict(base[key0], '/'.join(keys[1:]), dict_value)
        base = merge_dict_inplace(base, {key0: up_config})
    return base


def update_from_cli(base: dict, cli_kwargs: dict):
    for key, value in cli_kwargs.items():
        base = update_nested_dict(base, dict_key=key, dict_value=value)
    return base


def jimmy_load(path: Path, cli_kwargs: dict = None, constructors: dict = None) -> tuple[GenericDict, GenericDict]:
    # add new constructors
    constructors = default_constructors if constructors is None else default_constructors.update(constructors)
    constructors['!here'] = partial(here_path, path=path)

    for key, func in constructors.items():
        yaml.add_constructor(key, func)

    yaml.add_constructor('!load', load_node)

    # add new representer
    yaml.add_representer(JimmyMap, jimmy_dumper)
    yaml.add_representer(PosixPath, path_dumper)

    # load config
    config = _load(path)

    if cli_kwargs is not None:
        config = update_from_cli(config, cli_kwargs)

    if 'jimmy' in config:
        raw_config, jimmy_config = split_jimmy_map(config)
        config = update_from_template(jimmy_config, raw_config)
        return config, jimmy_config
    else:
        return config, JimmyMap()


def recursive_dict(a: GenericDict, **kwargs) -> GenericDict:
    for key, value in a.items():
        if isinstance(value, JimmyMap):
            recursive_dict(a.get(key), **kwargs)

        elif isinstance(value, dict):
            recursive_dict(a.get(key), **kwargs)

        elif hasattr(value, 'apply'):
            a[key] = value.apply(**kwargs)

    return a


def jimmy_dumper(dumper, data: JimmyMap):
    return dumper.represent_dict(data.to_dict())


def path_dumper(dumper, data: Path):
    data = str(data.absolute())
    return dumper.represent_str(data)


def compute_grid_configs(config: GenericDict, kwargs: GenericDict) -> GenericDict:
    all_config = {}
    for new_params in itertools.product(*kwargs.values()):
        _config = copy.deepcopy(config)
        new_name = 'hparam'

        for value, key in zip(new_params, kwargs.keys()):
            _config = update_nested_dict(_config, key, value)
            key_final = key.split('/')[-1]
            new_name += f'_{key_final}:{value}'

        all_config[new_name] = _config

    return all_config


def save_yaml(config: GenericDict, path: Path) -> None:
    with open(path, "w") as f:
        yaml.dump(config, f)


@dataclass
class JimmyConfig:
    template: GenericDict = None
    dump_config: str = None
    grid_launcher: GenericDict = None


class JimmyLauncher:
    def __init__(self, config_path: Path = None, cli_kwargs: dict = None, constructors: Mapping = None):
        if config_path is None:
            config_path, cli_kwargs = config_parser()

        self.config_path = config_path
        self._config, jimmy_config = jimmy_load(self.config_path, cli_kwargs=cli_kwargs, constructors=constructors)
        self.jimmy_config = JimmyConfig(**jimmy_config)

    @property
    def config(self) -> GenericDict:
        return self.parse_config(self._config)

    @staticmethod
    def parse_config(config, **kwargs):
        _config = copy.deepcopy(config)
        return recursive_dict(_config, **kwargs)

    def dump_config(self, config, summary, name='config.yaml'):
        if self.jimmy_config.dump_config is None:
            return None

        if summary is not None:
            config['run_summary'] = summary

        config_path = self._get_dump_path(config, dump_key=self.jimmy_config.dump_config)

        if config_path.exists() and config_path.is_file():
            config_path = config_path.parent / name

        elif config_path.exists() and config_path.is_dir():
            config_path = config_path / name

        else:
            config_path = config_path / name
            config_path.parent.mkdir(exist_ok=True, parents=True)
        save_yaml(config, config_path)

    @staticmethod
    def _get_dump_path(config, dump_key):
        keys = dump_key.split('/')
        config_copy = copy.deepcopy(config)
        for key in keys:
            config_copy = config_copy.get(key)
        return config_copy

    @staticmethod
    def _run(func, config):
        start_time, timer = time_stamp().apply(), time.time()
        result = func(**config)
        end_time, timer = time_stamp().apply(), time.time() - timer

        summary = JimmyMap(start_time=start_time,
                           runtime=timer,
                           end_time=end_time,
                           result=result)
        return result, summary

    def simple_launcher(self, func: Callable, config: GenericDict = None, return_summary: bool = False):
        if config is None:
            config = self.config

        self.dump_config(config, summary=None)
        result, summary = self._run(func, config)
        self.dump_config(config, summary)

        if return_summary:
            return result, return_summary
        return result

    def grid_launcher(self, func: Callable, return_summary: bool = False):
        if self.jimmy_config.grid_launcher is None:
            raise ValueError('Grid launcher required a "grid_launcher to be defined" in the jimmy-config.')

        grid_configs = compute_grid_configs(self._config, self.jimmy_config.grid_launcher)
        returns, summaries = [], []
        for key, config in grid_configs.items():
            config = self.parse_config(config, experiment_key=key)
            result, summary = self.simple_launcher(func, config, return_summary=True)
            returns.append(result)
            summaries.append(summary)

        if return_summary:
            return returns, summaries
        return returns


def jimmy_launcher(func, **jimmy_kwargs):
    def wrapper():
        _jimmy_launcher = JimmyLauncher(**jimmy_kwargs)
        return _jimmy_launcher.simple_launcher(func, return_summary=False)

    return wrapper


def jimmy_grid_launcher(func, **jimmy_kwargs):
    def wrapper():
        _jimmy_launcher = JimmyLauncher(**jimmy_kwargs)
        return _jimmy_launcher.grid_launcher(func, return_summary=False)

    return wrapper
