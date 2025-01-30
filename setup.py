from setuptools import setup

setup(
    name='PowerHourGenerator',
    version='0.2.0',
    entry_points={
        'console_scripts': [
            'phgen = phgen.cli:main'
        ]
    },
    install_requires=[
        'yt_dlp',
        'ffmpeg-python'
    ],
    python_requires='>=3.10'
)


if __name__ == "__main__":
    print("fasfasf")