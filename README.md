# About
Simple scripts to handle heatmap data. Create a single image with `heatmap2png.py` or create a movie with `heatmap2mp4.py`.

# Usage
Both scripts work the same:

```bash
$ python3 heatmap2png.py -f example.csv

$ python3 heatmap2mp4.py -f example.csv
```

The results will be output to a `png` or `mp4` subfolder.

# Requirements
The heatmap is processed using this library: https://github.com/kwauchope/heatmap

Clone it to your local system and then install as follows:

```bash
$ git clone https://github.com/kwauchope/heatmap.git
$ cd heatmap-master
$ python3 setup.py install
```

The movie is created by https://pypi.org/project/moviepy/ and can be installed using pip:

```bash
$ pip3 install moviepy
```
