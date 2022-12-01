from setuptools import setup, find_packages

setup(
	name='phgen',
	version='0.1.0',
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    packages=find_packages(include=['phgen', 'phgen.*']),
    entry_points={
        'console_scripts': [
            'phgen=phgen.main:main_args'
        ]
    },
    install_requires=[
        'pytube',
        'ffmpeg-python'
    ]
)