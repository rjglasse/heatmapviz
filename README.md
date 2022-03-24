# About
Analyse user gaze data from an eye tracker.

Output can be a heatmap image or movie, a graph of areas of interest that have been visited and how often, or barcharts of both the duration and dispersion of gaze within an area of interest.

# Usage
There are two main types of input data: _gaze data_ and _area of interest_ data.

Gaze data should be in [x, y, timestamp] CSV format (n.b. the first two rows are required to extract the resolution):

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

Area of interest data should be in [name, x1, y1, x2, y2] CSV format:

```
area_1, 100, 100, 200, 200
area_2, 200, 200, 300, 300
area_3, 300, 300, 400, 400
```

Run the script using the appropriate sub-commands for the desired output:

```bash
$ python3 gaze.py heatmap --data-file example.csv --format png
$ python3 gaze.py heatmap -d example.csv -f mp4
$ python3 gaze.py graph --data-file example.csv --aoi-file example-aoi.csv
$ python3 gaze.py chart -d example.csv -a example-aoi.csv
```

Results are output to the `./results/example/` subfolder and organised by the
output type. For more help and additional parameters, run:

```bash
$ python3 gaze.py -h
```

# Output types
Using, `gaze.py graph` will output a heatmap:

![alt text](/example.png)


If areas of interest have been defined, then they will be superimposed onto the heatmap.

> TODO: plot areas of interest on heatmap with black rectangles.

Using `gaze.py graph` will output a graph of the count of transitions between the areas of interest:

![alt text](/example.gv.png)

Using `gaze.py chart` will create two barcharts for duration and dispersion within the areas of interest over time:

![alt text](/example-duration.png)

The first chart plots a timeline of duration in each area of interest. The units are based on the eyetracker data.

![alt text](/example-dispersion.png)

The second chart plots a timeline of dispersion in each area of interest. Dispersion is measured using the standard distance deviation (see: https://pro.arcgis.com/en/pro-app/2.8/tool-reference/spatial-statistics/standard-distance.htm).



# Requirements
The heatmap is processed using: https://github.com/kwauchope/heatmap

Clone it to your local system and then install as follows:

```bash
$ git clone https://github.com/kwauchope/heatmap.git
$ cd heatmap-master
$ python3 setup.py install
```

The heatmap video is created using https://pypi.org/project/moviepy/ and can be installed using pip3:

```bash
$ pip3 install moviepy
```

The graph is created using [Graphviz](https://www.graphviz.org), which you can find here:

https://www.graphviz.org/download/

Once you have installed Graphviz, you can then install its Python library using pip3:

```bash
$ pip3 install graphviz
```

The charts are created using [Matplotlib](https://matplotlib.org/) and can be installed by following instructions here:

https://matplotlib.org/stable/users/installing/index.html

Obs: You may already have some of these requirements; so it is worth checking or using a new virtual environment (see: https://docs.python.org/3/tutorial/venv.html)
