import argparse
import csv
import heatmap
import os
import time

from moviepy.editor import *

def create_png():
    # read CSV and convert to a list of ['x', 'y', 'timestamp'] elements
    with open(args.datafile, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)

    # extract the screen resolution from the CSV data
    x, y = data[1][2].split(' x ')
    resolution = tuple([int(x), int(y)])

    # pull the x,y coords from rows of data
    # - ignores timestamp and any other columns after [x, y, ...]
    # - ignores the first two lines of file which are not coord data
    coord_data = []
    for sample in data[2:]:
        coord_data.append((int(sample[0]),int(sample[1])))

    # generate heatmap and save to PNG
    # - reuses the original filename and changes extension to ".png"
    hm = heatmap.Heatmap()
    outfile = "/" + args.datafile.split('.')[0] + ".png"
    img = hm.heatmap(coord_data, size=resolution).save(folderpath + outfile)

def create_mp4():
    hm = heatmap.Heatmap()
    pts = []
    mod = 0
    counter = 0
    imgno = 0

    # generate heatmaps over time intervals of a second
    with open(args.datafile, 'r') as csvfile:
        freader = csv.reader(csvfile)
        r1 = next(freader)
        r2 = next(freader)
        x, y = r2[2].strip().split(" x ")
        resolution = tuple([int(x), int(y)])
        for row in freader:
            mod = (mod + 1)%2 #take every other point
            if mod == 1:
                counter += 1
                pts.append((int(row[0]), resolution[1] - int(row[1])))
                if counter%25==0: #50 for interval of a second, 25 for half second
                    imgno += 1
                    img = hm.heatmap(pts, size = resolution, area = ((0,0), resolution), dotsize=75) #scale dotsize up?
                    img.save(folderpath+ "/imgs/hm" + str(imgno) + ".png")
                    pts = []

    if len(pts) > 0:
        imgno += 1
        img = hm.heatmap(pts, size = resolution, area = ((0,0), resolution), dotsize=75)
        img.save(folderpath + "/imgs/hm" + str(imgno) + ".png")

    #Generate timelapse video
    print("Making timelapse...")
    image_list = []
    for x in range(imgno):
        image_list.append(folderpath + "/imgs/hm" + str(x+1)+".png")
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
    # finalclip.write_videofile(folderpath+"/composite.mp4", codec = "mpeg4", audio = False, fps = 30)

if __name__ == '__main__':
    # handle command line arguments
    parser = argparse.ArgumentParser(description='Generate a Heatmap from a CSV file with [x, y, ...] format. Output format can be a single image (png) or a movie (mp4) with a folder of image frames.')
    parser.add_argument('-d', '--datafile', help='input CSV file', required=True)
    parser.add_argument('-f', '--format', help='output format [png, mp4]', choices=['png', 'mp4'], required=True)
    args = parser.parse_args()

    # create output folders
    folderpath = "./" + args.format + "/" + args.datafile.split('.')[0]
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)

    print("Saving heatmap to " + folderpath)

    # create the output depending on the chosen format
    if args.format == "png":
        create_png()
    elif args.format == "mp4":
        create_mp4()
