from setuptools import setup
## Setup of the app
setup(
    name='phyloweb',
    packages=['phyloweb'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)
