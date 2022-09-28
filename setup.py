from setuptools import setup, find_packages

exec(open('jimmy/__version__.py').read())
setup(
    name='jimmy',
    version=__version__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    description='Jimmy is just my (py)Yaml',
    author='Lorenzo Cerrone',
    url='https://github.com/lorenzocerrone/python-jimmy',
    author_email='lorenzo.cerrone@iwr.uni-heidelberg.de',
)
