

# PowerHourGenerator

Hello friends! Feel free to open an issue or a pull request!

*PowerHourGenerator* is a lightweight Python command-line utility for automatically generating power hours. What is a power hour, you might ask? It's an hour-long video compilations of music videos, each 1 min long. After each song, you take a drink of your beverage (ideally beer). [Here's an example](https://youtu.be/Rn6_yYX_25M)

Now making them can be time consuming because you have to at a minimum download 60 videos (don't tell Google), clip each to a 🔥60-second subset, and likely also add text for the title and artist and number *and probably add fades in and out*. What if I told you that could be automated...That's what *PowerHourGenerator* is for. 

This CLI will automate downloading all the videos, clipping them to a desired start time and length, add a fade in and out, add the title/artist and number to the video files and output 60 individual video files which can be combined and exported in a video editor of your choice. And just as a cherry on top, it'll standardize the output resolutions/aspect ratios because we all like that 1 song who's video is a square, or only has a 240p version. It's much much faster to add to a video editor if you don't have to deal with that.

## Requirements

- Python 3.11.1 (lower ones might work too that's just what I have installed)

## Quickstart

### Installation

*PowerHourGenerator* (from here on is `phgen` because that's the name of the CLI and is shorter) is not yet on PIP so you'll need to download the repo and install manually. To do so, download the repo, unzip anywhere you'd like, navigate to the root folder with `setup.py` in your favorite terminal and run this command

```bash
$ pip install .
```

Alternatively, if you plan on helping me develop the repo run this command instead so you don't need to reinstall when you implement changes to the library

```bash
$ pip install -e .
```

### Using the command-line interface

The CLI only has 1 required argument, the `-i --input` file path, which you do not need to specify as long as it's the first parameter. This command, for example, would parse and process a file named test.tsv

Currently phgen requires a `csv` or `tsv` formatted with the following header

```bash
$ phgen input.tsv
```

Currently phgen requires a `csv` or `tsv` formatted with the following header

```tsv
title	artist	start_time	duration	link
```

- `title` is the title of the song, which if text is added will be written onto the screen
- `artist` is the name of the credited artist for the song, which if text is added will be written onto the screen
- `start_time` is the timestamp to start the clip at. Format as `m:ss`. If blank, it will start 0:00
- `duration` is the integer length of the video to clip in seconds to use after start time. this column is optional, defaults 60
- `link` is a working YouTube link to download, clip and process. Other sites may work as determined by `pytube` but are untested

The CLI has the following optional arguments as well

- `-p --project` The name of the output directory, and will be used in the name of all outputted video files. Defaults to `ph01` or a higher number if a directory with that name already exists
- `-res --resolution` the desired resolution of the project, written in the standard format (1080p, for example). Other resolutions are untested 🤷
- `-r --range` the range from the input to process. Accepts either 1 or 2 numbers separated by a `-` or `:`. The first number is the starting index, second is length. If only 1 number is provided it'll start there and go to the end of the input file
- `-d --dry_run` Accepts no parameters, will cause the CLI to *only* parse the input file and output it's results. Use to ensure you're formatted everything correctly
- `-xt --no_text` Accepts no parameters, will cause the CLI to skip the text step
- `-xf --no_fade` Accepts no parameters, will cause the CLI to skip the fade in-out step
- `-xc --no_clip` Accepts no parameters, will cause the CLI to skip clipping the videos to a specified length
