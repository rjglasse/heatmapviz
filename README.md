# About
Visualizes eyetracker data as a heatmap. A single image of the interaction or a movie of the sequence of interactions can be generated.

# Usage
Data should be in [x, y, ...] CSV format (n.b. the first two rows are required):

```csv
X Gaze Data, Y Gaze Data, Time
(0, 0), 1920 x 1080
912,408,866483295
910,402,866483304
909,399,866483314
908,399,866483342
907,401,866483347
...
```

Run the script using either short or long parameters:

```bash
$ python3 heatmapviz.py -d example.csv -f png

$ python3 heatmapviz.py --data example.csv --format mp4
```

The results will be output to a `png` or `mp4` subfolder:

![alt text](/example.png)

The heatmap can be further refined with the following parameters:

```
-p --point-size     pixel size of each sample point in heatmap [default is 150]
-s --scheme         colour scheme for heatmap [default is classic, others are fire, omg, pbj, pgaitch]
-o --opacity        change the opacity for the heatmap [default is 128]
```

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
