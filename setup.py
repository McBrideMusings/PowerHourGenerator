from setuptools import setup

setup(
    name='PowerHourGenerator',
    version='0.1.0',
    entry_points={
        'console_scripts': [
            'phgen = phgen.cli:main'
        ]
    },
    install_requires=[
        'pytube',
        'ffmpeg-python'
    ]
)


if __name__ == "__main__":
    print("fasfasf")