import argparse
import heatmap
import csv
import os
import time
from moviepy.editor import *

if __name__ == "__main__":

    # read the CSV filepath as an argument
    parser = argparse.ArgumentParser(description='Generate a Heatmap MP4 (video) from a CSV file with [x, y, ...] format.')
    parser.add_argument('-f', dest='filepath', help='path to CSV file', required=True)
    args = parser.parse_args()

    # generate directory path for output
    folderpath = "./mp4/" + args.filepath.split('.')[0]
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    if not os.path.exists(folderpath+"/imgs"):
        os.makedirs(folderpath+"/imgs")
    print("Saving heatmaps to " + folderpath)

    hm = heatmap.Heatmap()
    pts = []
    mod = 0
    counter = 0
    imgno = 0

    # generate heatmaps over time intervals of a second
    with open(args.filepath, 'r') as csvfile:
        freader = csv.reader(csvfile)
        r1 = next(freader)
        r2 = next(freader)
        mysize = r2[2].strip()
        mysize = mysize.split(" x ")
        mysize = list(map(int, mysize))
        mysize = tuple(mysize)
        for row in freader:
            mod = (mod + 1)%2 #take every other point
            if mod == 1:
                counter += 1
                pts.append((int(row[0]), mysize[1] - int(row[1])))
                if counter%25==0: #50 for interval of a second, 25 for half second
                    imgno += 1
                    img = hm.heatmap(pts, size = mysize, area = ((0,0), mysize), dotsize=75) #scale dotsize up?
                    img.save(folderpath+ "/imgs/hm" + str(imgno) + ".png")
                    pts = []

    if len(pts) > 0:
        imgno += 1
        img = hm.heatmap(pts, size = mysize, area = ((0,0), mysize), dotsize=75)
        img.save(folderpath + "/imgs/hm" + str(imgno) + ".png")

    #Generate timelapse video
    print("Making timelapse...")
    image_list = []
    for x in range(imgno):
        image_list.append(folderpath + "/imgs/hm" + str(x+1)+".png")
    my_clip = ImageSequenceClip(image_list, fps=2)
    outfile = "/" + args.filepath.split('.')[0] + ".mp4"
    my_clip.write_videofile(folderpath + outfile, codec = "mpeg4", audio = False)

    #Uncomment to automatically create overlay once the video is created
    #Making the overlay
    # timelapsePath=folderpath+"/timelapse.mp4"
    # print "Making overlay..."
    # backclip = VideoFileClip('resources/experiment.mp4')
    # forwardclip = VideoFileClip(timelapsePath).set_opacity(0.5)
    # finalclip = CompositeVideoClip([backclip, forwardclip])
    # finalclip.write_videofile(folderpath+"/composite.mp4", codec = "mpeg4", audio = False, fps = 30)
