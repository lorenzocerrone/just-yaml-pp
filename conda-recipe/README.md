## Conda build
In order to create conda package manually:

Run: 
```
conda build -c conda-forge
```

## Release new version
1. Make sure that `bump2version` is installed in your conda env
2. Checkout master branch
3. Run `bumpversion patch` (or `major` or `minor`) - this will bum the version in `.bumpversion.cfg` and `__version__.py` add create a new tag.
4. Run `git push && git push --tags` - this will trigger tagged travis build
