# "jimmy" is just my modified yaml (and a bit more)
It's just my Yaml wrapper with some useful constructors builtin.

jimmy also includes a simple grid launcher for easily mange multiple runs of the script. 

PS: This is just a small personal project and bugs and instability are to be expected!

## Install with conda
```
conda install -c lcerrone jimmy
```

### Jimmy Map
The first difference with plain pyaml is that it construct dictionaries into JimmyMap objects. 
A Jimmy map behave in between a dictionary and a named tuple
```python
from jimmy.jimmy_map import JimmyMap

jimmy_map = JimmyMap(x=1, y=2, z=3)
# get a value
x = jimmy_map['x']
# or 
x = jimmy_map.x
# it's mutable
jimmy_map['z'] = 4

# behave as a map 
def func(x, y, z) -> None: pass
func(**jimmy_map)

# can be converted to a dictionary
jimmy_dictionary = jimmy_map.to_dict()
```
### Special Yaml Constructors
**Generic constructors:**
```yaml
x: !join ['hello', ' ', 'jimmy']  # equivalent to -> x: 'hello jimmy'
y: !load './some_template.yaml'   # load a yaml file a dictionary -> y: {...}
z: !time-stamp []                 # When parsing the config will render the time as 
```
**Path constructors:**
```yaml
a: !path './some_data.txt'                           # will load the path ad a pathlib.Path object
b: !join-paths ['home', 'username', 'some_data.txt'] # will join the path 'home/username/some_data.txt' and load the
                                                     # path ad a pathlib.Path object
c: !glob ['home', 'username', '*.txt']               # will join the path 'home/username/*' and load all file matching
                                                     # '*.txt'
d: !absolute-path './some_local_path.txt'            # will make the local path absolute
e: !home []                                          # will return the home path
f: !here []                                          # will return the path of the current yaml being loaded
g: !unique-path './logs'                             # When parsing the config will to ensure a unique name, 
                                                     # i.e. if a directory called logs exists it will be called /logs_v1
```
**Math constructors:**
```yaml
a: !sum [1, 2, 3]        # will return the sum of the numbers given
b: !range [0, 10, 0.1]   # will create a range of numbers between 0 and 10 with step of .1
c: !logspace [-5, -2, 4] # will create a range of 4 numbers between 10**-5 and 10**2
d: !linspace [0, 1, 100] # will create a range of 100 numbers between 0 and 1
```
### Jimmy Config
As I will show later, Jimmy can also launch the script execution. To do these and some few other 
features your can add a `jimmy` to your yaml config.
The features available are:
- **template**: the key template can be used to load as a base version of the config.
- **dump_config**: specify a key in the overall config where the config will be dumped.
- **grid_launcher**: Defines a grid or parameters over which to run the grid search.

The `jimmy` key will be stripped from the config before the execution.

### Launchers 
**Simple launcher:**
```python
from jimmy import JimmyLauncher
def main(x, y, z):
    ...
    return 0

jimmy_launcher = JimmyLauncher()
print(jimmy_launcher.config)
jimmy_launcher.simple_launcher(main) # return 0
```
when running the script the confing file can be passed as an argument
```bash
python my_script.py --config ./example.yaml
```
It is also possible to replace simple fields on the run 
```bash
python my_script.py --config ./example.yaml --x 10 
```

**Grid launcher:**
Define the grid point in the `jimmyconfig`:
```yaml
logs: !unique-path './results/'
x: 1
y: 2
z:
  a: 3 

jimmy:
  grid_launcher:
    x: [1, 3]
    y: !log-space [-5, -2, 4]
    z/a: !range[0, 10, 1]
```
And run them all using the grid launcher 
```python
from jimmy import JimmyLauncher
def main(x, y, z):
    ...
    return 0

jimmy_launcher = JimmyLauncher()
print(jimmy_launcher.config)
jimmy_launcher.grid_launcher(main) # return a list of all results
```

In order to keep the runs results clean we defined a unique-path as log location.
Unique path instead of using the basic versioning (`v1`, `v2`, etc..), the `grid_launcher` will create a
unique name based on the parameters used in each run (`reults/hparm_x=1_y_0.1_z/a_0`, etc..).

### configuration validation

```python
from jimmy.jimmy_validator import jimmy_validator


@jimmy_validator
class Config:
    # define the config name space
    name: str = 'name'
    x: int = 0
    # custom test functions
    y: float = lambda value: 0 < value < 1
    # type hints are not strictly checked, but you can add as many tests as you wish
    sigma: float = [lambda value: isinstance(value, float), lambda value: 0 < value < 5]


def main(config: Config):
    Config.validate(config)  # will check that the config parsed from the yaml file will fit the required parameters

```

## TODO List
* parallelize the `grid_launcher` runs (still thinking if using simply multiprocessing or either dask or ray).
* improve the `!unique-path` constructor to be more predictable in case of reference and multiple instance of it.
* cleanup the api and write proper docs.   
