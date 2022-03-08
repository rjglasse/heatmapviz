"""Creates heatmap visualizations from eytracking (et) data in different formats (png & mp4)."""

import os
import argparse
import csv
import heatmap

from moviepy.editor import ImageSequenceClip

def read_et_data(filename):
    """Read eyetracking CSV file and convert to a list of ['x', 'y', 'timestamp'] elements."""
    with open(filename, 'r') as csv_file:
        reader = csv.reader(csv_file)
        return list(reader)

def extract_resolution(et_data):
    """Extract the screen resolution from the eyetracking data."""
    x_coord, y_coord = et_data[1][2].split(' x ')
    return tuple([int(x_coord), int(y_coord)])

def create_png(et_data, resolution):
    """Creates a single eyetracking heatmap image in PNG format."""
    # create output folder
    folderpath = "./" + args.format + "/" + args.datafile.split('.')[0]
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    print("Saving heatmap to " + folderpath)

    # pull the x, y coordinate pairs from rows of data
    coord_data = []
    for row in et_data[2:]:
        coord_data.append((int(row[0]),int(row[1])))

    # generate heatmap and save to PNG
    h_map = heatmap.Heatmap()
    outfile = "/" + args.datafile.split('.')[0] + ".png"
    h_map.heatmap(coord_data, size=resolution, scheme=args.scheme,
        dotsize=args.point_size, opacity=args.opacity).save(folderpath + outfile)

def create_mp4(et_data, resolution):
    """Creates a movie from a sequence of eyetracking heatmap images in MP4 format."""
    # create output folders
    folderpath = "./" + args.format + "/" + args.datafile.split('.')[0]
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    if not os.path.exists(folderpath+"/imgs"):
        os.makedirs(folderpath+"/imgs")

    h_map = heatmap.Heatmap()
    pts = []
    mod = 0
    counter = 0
    imgno = 0

    # generate heatmaps over time intervals of a second
    for row in et_data[2:]:
        mod = (mod + 1)%2 # take every other point
        if mod == 1:
            counter += 1
            pts.append((int(row[0]), resolution[1] - int(row[1])))
            if counter%25==0: #50 for interval of a second, 25 for half second
                imgno += 1
                img = h_map.heatmap(pts, size=resolution, area=((0,0), resolution),
                    dotsize=args.point_size, scheme=args.scheme, opacity=args.opacity)
                img.save(folderpath+ "/imgs/hm" + str(imgno) + ".png")
                pts = []

    if len(pts) > 0:
        imgno += 1
        img = h_map.heatmap(pts, size = resolution, area = ((0,0), resolution),
            dotsize=args.point_size, scheme=args.scheme, opacity=args.opacity)
        img.save(folderpath + "/imgs/hm" + str(imgno) + ".png")

    # generate timelapse video
    print("Making timelapse...")
    image_list = []
    for index in range(imgno):
        image_list.append(folderpath + "/imgs/hm" + str(index+1)+".png")
    my_clip = ImageSequenceClip(image_list, fps=2)
    outfile = "/" + args.datafile.split('.')[0] + ".mp4"
    my_clip.write_videofile(folderpath + outfile, codec = "mpeg4", audio = False)

    #Uncomment to automatically create overlay once the video is created
    #Making the overlay
    # timelapsePath=folderpath+"/timelapse.mp4"
    # print "Making overlay..."
    # backclip = VideoFileClip('resources/experiment.mp4')
    # forwardclip = VideoFileClip(timelapsePath).set_opacity(0.5)
    # finalclip = CompositeVideoClip([backclip, forwardclip])
    # finalclip.write_videofile(folderpath+"/composite.mp4", codec="mpeg4", audio=False, fps=30)

def get_user_args():
    """Parser for command line arguments."""
    parser = argparse.ArgumentParser(description='Generate a Heatmap from a CSV file with \
        [x, y, ...] format. Output format can be a single image (png) or a movie (mp4) \
        with a folder of image frames.')
    parser.add_argument('-d', '--datafile', help='input CSV file', required=True)
    parser.add_argument('-f', '--format', help='output format [png, mp4]', \
        choices=['png', 'mp4'], required=True)
    parser.add_argument('-s', '--scheme', help='colour scheme for heatmap \
        [classic, fire, omg, pbj, pgaitch]', choices=['classic', 'fire', \
        'omg', 'pbj', 'pgaitch'], default='classic')
    parser.add_argument('-o', '--opacity', help='strength of a single point \
        in heatmap (from 0-255)', default=128, type=int)
    parser.add_argument('-p', '--point-size', help='size of a single point \
        in heatmap', default=150, type=int)
    return parser.parse_args()

if __name__ == '__main__':

    args = get_user_args()
    data = read_et_data(args.datafile)
    res = extract_resolution(data)

    # create the output depending on the chosen format
    if args.format == "png":
        create_png(data, res)
    elif args.format == "mp4":
        create_mp4(data, res)
