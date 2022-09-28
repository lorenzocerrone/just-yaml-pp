import pathlib
import time

import yaml
import itertools
import copy
from jimmy.constructors.math_constructors import build_range, build_lin_space, build_log_space, sum_nodes
from jimmy.constructors.path_constructors import home_path, unique_path, make_absolute, join_paths, make_path, find_glob
from jimmy.constructors.basic_constructors import join, jimmy_constructor, time_stamp
from jimmy.jimmy_dict import JimmyMap


def merge_dict_inplace(a: JimmyMap, b: JimmyMap):
    for key, value in b.items():
        if isinstance(b.get(key), JimmyMap) and key in a:
            a[key] = merge_dict_inplace(a.get(key), b.get(key))
        else:
            a[key] = b[key]
    return a


def update_from_template(jimmy_config, config):
    if 'template' in jimmy_config:
        template = jimmy_config.pop('template')
        config = merge_dict_inplace(template, config)
    return config


default_constructors = {'tag:yaml.org,2002:map': jimmy_constructor,
                        '!join': join,
                        '!time-stamp': time_stamp,
                        '!join-paths': join_paths,
                        '!glob': find_glob,
                        '!home': home_path,
                        '!unique-path': unique_path,
                        '!path': make_path,
                        '!absolute-path': make_absolute,
                        '!sum': sum_nodes,
                        '!range': build_range,
                        '!log-space': build_log_space,
                        '!lin-space': build_lin_space
                        }


def _openfile_and_load(path):
    with open(path, 'r') as f:
        return yaml.full_load(f)


def load(loader, node):
    return _openfile_and_load(node.value)


def recursive_dict(a, **kwargs):
    for key, value in a.items():
        if isinstance(value, JimmyMap):
            recursive_dict(a.get(key), **kwargs)

        elif hasattr(value, 'apply'):
            a[key] = value.apply(**kwargs)

    return a


def jimmy_dumper(dumper, data):
    return dumper.represent_dict(getattr(data, 'items')())


def path_dumper(dumper, data):
    data = str(data.absolute())
    return dumper.represent_str(data)


class Jimmy:
    def __init__(self, config_path: str, constructors: dict = None):
        self.config_path = config_path

        constructors = default_constructors if constructors is None else default_constructors.update(constructors)

        for key, func in constructors.items():
            yaml.add_constructor(key, func)

        yaml.add_constructor('!load', load)
        yaml.add_representer(JimmyMap, jimmy_dumper)
        yaml.add_representer(pathlib.PosixPath, path_dumper)

        raw_config = _openfile_and_load(self.config_path)
        if 'jimmy' in raw_config:
            jimmy_config = raw_config.pop('jimmy')
            config = update_from_template(jimmy_config, raw_config)
        else:
            jimmy_config = None
            config = raw_config

        self._config = config
        self.jimmy_config = jimmy_config

    @property
    def config(self):
        return self.parse_config(self._config)

    @staticmethod
    def parse_config(config, **kwargs):
        _config = copy.deepcopy(config)
        return recursive_dict(_config, **kwargs)

    @staticmethod
    def _run(func, config):
        start_time = time_stamp()
        timer = time.time()
        result = func(**config)
        timer = time.time() - timer
        end_time = time_stamp()

        summary = JimmyMap(start_time=start_time, runtime=timer, end_time=end_time, result=result)
        return result, summary

    def _simple_launcher(self, func, config):
        result, summary = self._run(func, config)
        self.dump_config(config, summary)
        return result, summary

    def simple_launcher(self, func, return_summary=False):
        result, summary = self._simple_launcher(func, self.config)

        if return_summary:
            return result, return_summary
        return result

    def dump_config(self, config, summary, name='config.yaml'):
        if 'dump_config' not in self.jimmy_config:
            return None

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

    def grid_launcher(self, func, return_summary=False):
        grid_configs = compute_grid_configs(self._config, self.jimmy_config['grid-launcher'])
        returns, summaries = [], []
        for key, config in grid_configs.items():
            config = self.parse_config(config, experiment_key=key)
            result, summary = self._simple_launcher(func, config)
            returns.append(result)
            summaries.append(summary)

        if return_summary:
            return returns, summaries
        return returns


def compute_grid_configs(config: dict, kwargs: dict):
    def update_nested_dict(base, dict_key, dict_value):
        keys = dict_key.split('/')
        key0, _key = keys[0], '/'.join(keys[1:])
        if len(keys) == 1:
            base.update({key0: dict_value})
        else:
            if key0 not in base:
                base.update({key0: {}})
            up_config = update_nested_dict(base[key0], '/'.join(keys[1:]), dict_value)
            base.update({key0: up_config})
        return base

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


def save_yaml(config, path):
    with open(path, "w") as f:
        yaml.dump(config, f)
