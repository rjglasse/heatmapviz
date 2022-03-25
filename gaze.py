"""Visualize gaze data as heatmap, event graph and event chart."""

import os
import csv
import argparse
import math
import heatmap
import graphviz
import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import ImageSequenceClip
from PIL import Image, ImageDraw, ImageFont

aois = None

def read_et_data(filename):
    """Read eyetracking CSV file and convert to a list of ['x', 'y', 'timestamp'] elements."""
    with open(filename, 'r') as csv_file:
        reader = csv.reader(csv_file)
        return list(reader)

def extract_resolution(et_data):
    """Extract the screen resolution from the eyetracking data."""
    x_coord, y_coord = et_data[1][2].split(' x ')
    return tuple([int(x_coord), int(y_coord)])

def get_results_location(output):
    """Create output folder structure based on output and file extension."""
    outfile = os.path.split(args.data_file)[1].split(".")[0]
    subfolder = os.path.split(args.data_file)[1].split(".")[0] + "/"
    folderpath = "./results/" + subfolder + output + "/"
    if output == "heatmap":
        folderpath = "./results/" + subfolder + output + "/" + args.format + "/"

    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    return outfile, folderpath

def create_heatmap_image(et_data, resolution):
    """Creates a single eyetracking heatmap image in PNG format."""
    # pull the x, y coordinate pairs from rows of data
    coord_data = []
    for row in et_data[2:]:
        coord_data.append((int(row[0]), resolution[1] - int(row[1])))

    # generate heatmap and save to PNG
    outfile, folderpath = get_results_location("heatmap")
    h_map = heatmap.Heatmap()
    h_map_image = h_map.heatmap(coord_data, size=resolution, area=((0,0), resolution), scheme=args.scheme,
        dotsize=args.point_size, opacity=args.opacity).save(folderpath + outfile + ".png")
    # overlay areas of interest if required
    if args.aoi_file:
        overlay_areas_of_interest(folderpath + outfile + ".png")

    print(folderpath + outfile + ".png")

def overlay_areas_of_interest(image_path):
    """"Draw the areas of interest over a heatmap image"""
    global aois
    if aois is None:
        aois = read_aoi_data(args.aoi_file)
    with Image.open(image_path) as overlay_image:
        overlay = ImageDraw.Draw(overlay_image)
        overlay_font = ImageFont.truetype("Arial Bold.ttf", 16)
        for aoi in aois:
            overlay.text((int(aoi["x1_coord"]+5), int(aoi["y1_coord"]+7)), aoi["area"],(0,0,0),
                font=overlay_font)
            overlay.rectangle([(int(aoi["x1_coord"]), int(aoi["y1_coord"])),
                (int(aoi["x2_coord"]), int(aoi["y2_coord"]))], outline="black", width=2)

        overlay_image.save(image_path)

def create_heatmap_video(et_data, resolution):
    """Creates a movie from a sequence of eyetracking heatmap images in MP4 format."""
    # create output folder
    outfile, folderpath = get_results_location("heatmap")
    if not os.path.exists(folderpath+"/frames"):
        os.makedirs(folderpath+"/frames")

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
                img.save(folderpath + "/frames/" + outfile + "-" + str(imgno) + ".png")
                # overlay areas of interest if required
                if args.aoi_file:
                    overlay_areas_of_interest(folderpath + "/frames/" + outfile + "-" + str(imgno) + ".png")
                pts = []

    if len(pts) > 0:
        imgno += 1
        img = h_map.heatmap(pts, size=resolution, area=((0,0), resolution),
            dotsize=args.point_size, scheme=args.scheme, opacity=args.opacity)
        img.save(folderpath + "/frames/" + outfile + "-" + str(imgno) + ".png")
        # overlay areas of interest if required
        if args.aoi_file:
            overlay_areas_of_interest(folderpath + "/frames/" + outfile + "-" + str(imgno) + ".png")

    # generate timelapse video
    image_list = []
    for index in range(imgno):
        image_list.append(folderpath + "/frames/" + outfile + "-" +  str(index+1)+".png")

    my_clip = ImageSequenceClip(image_list, fps=2)
    outfile += ".mp4"
    my_clip.write_videofile(folderpath + outfile, codec="mpeg4",
        audio=False, verbose=False, logger=None)
    print(folderpath+outfile)

    #Uncomment to automatically create overlay once the video is created
    #Making the overlay
    # timelapsePath=folderpath+"/timelapse.mp4"
    # print "Making overlay..."
    # backclip = VideoFileClip('resources/experiment.mp4')
    # forwardclip = VideoFileClip(timelapsePath).set_opacity(0.5)
    # finalclip = CompositeVideoClip([backclip, forwardclip])
    # finalclip.write_videofile(folderpath+"/composite.mp4", codec="mpeg4", audio=False, fps=30)

def create_heatmap():
    """Creates heatmap visualizations from eytracking (et) data in different formats (png & mp4)."""
    data = read_et_data(args.data_file)
    res = extract_resolution(data)
    # create the output depending on the chosen format
    if args.format == "png":
        create_heatmap_image(data, res)
    elif args.format == "mp4":
        create_heatmap_video(data, res)

def read_aoi_data(filename):
    """Read area of interest regions from file with format [id, x1, y1, x2, y2]"""
    with open(filename, 'r') as csv_file:
        aoi_data = []
        for line in csv.reader(csv_file):
            area = line[0].strip()
            x1_coord = int(line[1])
            y1_coord = int(line[2])
            x2_coord = int(line[3])
            y2_coord = int(line[4])
            aoi_data.append({"area":area, "x1_coord":x1_coord, "y1_coord":y1_coord,
                "x2_coord":x2_coord, "y2_coord":y2_coord})
    return aoi_data

def get_aoi(x_coord, y_coord, list_of_aois):
    """Get the area of interest for the given coordinate or return false"""
    for aoi in list_of_aois:
        if  aoi["x1_coord"] < x_coord < aoi["x2_coord"] \
            and aoi["y1_coord"] < y_coord < aoi["y2_coord"]:
            return aoi["area"]
    return False

def create_aoi_events(data, aois):
    """Build a list of area of interest events [area, gazepoints, duration, dispersion]"""
    # create list of aoi_events
    aoi_events = []
    aoi_current = ""
    for row in data[2:]:
        x_coord, y_coord, timestamp = int(row[0]), int(row[1]), int(row[2])
        area = get_aoi(x_coord, y_coord, aois)
        if area is aoi_current:
            # same event, append new point and update final timestamp
            aoi_events[-1]["points"].append((x_coord, y_coord))
            aoi_events[-1]["end"] = timestamp
        elif area:
            # new event, create a new aoi event
            aoi_current = area
            aoi_events.append({"area":area, "points":[], "start":timestamp, "end":timestamp})
            aoi_events[-1]["points"].append((x_coord, y_coord))
    # calculate duration and dispersion for aoi_events and write to CSV
    outfile, folderpath = get_results_location("events")
    with open(folderpath+outfile+".csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(("area", "duration", "dispersion"))
        for aoi_event in aoi_events:
            aoi_event["duration"] = aoi_event["end"] - aoi_event["start"]
            aoi_event["dispersion"] = dispersion(aoi_event["points"])
            writer.writerow((aoi_event["area"], aoi_event["duration"], aoi_event["dispersion"]))

    return aoi_events

def dispersion(points):
    """Calculate the standard distance for an area of interest event"""
    sum_x = 0
    sum_y = 0
    for point in points:
        sum_x += point[0]
        sum_y += point[1]

    avg_x = sum_x / len(points)
    avg_y = sum_y / len(points)

    sum_of_sq_diff_x = 0.0
    sum_of_sq_diff_y = 0.0
    for x_coord, y_coord in points:
        diff_x = math.pow(x_coord - avg_x, 2)
        diff_y = math.pow(y_coord - avg_y, 2)
        sum_of_sq_diff_x += diff_x
        sum_of_sq_diff_y += diff_y

    sum_of_results = (sum_of_sq_diff_x/len(points)) + (sum_of_sq_diff_y/len(points))
    return math.sqrt(sum_of_results)

def create_event_graph():
    """Create a directed graph of area of interest events."""
    et_data = read_et_data(args.data_file)
    aoi_data = read_aoi_data(args.aoi_file)
    events = create_aoi_events(et_data, aoi_data)
    # find and count edges
    edges = {}
    source_vertex = events[0]["area"]
    for event in events[1:]:
        dest_vertex = event["area"]
        edge = source_vertex + " -> " + dest_vertex
        try:
            edges[edge] += 1
        except KeyError:
            edges[edge] = 1
        source_vertex = dest_vertex
    # generate graphviz
    outfile, folderpath = get_results_location("graph")
    dot = graphviz.Digraph(outfile, comment="test", format="png")
    for edge, count in edges.items():
        src, dst = edge.split(" -> ")
        dot.edge(src, dst, label=str(count))

    dot.render(directory=folderpath)
    print(folderpath+outfile+".gv.png")

def create_event_chart():
    """Create duration and dispersion barcharts for a timeline of area of interest events."""
    et_data = read_et_data(args.data_file)
    aoi_data = read_aoi_data(args.aoi_file)
    events = create_aoi_events(et_data, aoi_data)
    # extract data to lists
    areas = []
    durations = []
    dispersions = []
    for event in events:
        areas.append(event["area"])
        durations.append(event["duration"])
        dispersions.append(event["dispersion"])

    outfile, folderpath = get_results_location("chart")
    # plot chart for duration
    y_pos = np.arange(len(areas))
    fig = plt.figure()
    plt.bar(y_pos, durations, align='center', alpha=0.5)
    plt.xticks(y_pos, areas, rotation='vertical')
    plt.ylabel('Duration (??)')
    plt.title('Areas of Interest over Time')
    plt.tight_layout()
    duration_path = folderpath + outfile + "-duration.png"
    fig.savefig(duration_path)
    print(duration_path)
    # plot chart for dispersion
    fig = plt.figure()
    plt.bar(y_pos, dispersions, align='center', alpha=0.5)
    plt.xticks(y_pos, areas, rotation='vertical')
    plt.ylabel('Dispersion (SDD)')
    plt.title('Areas of Interest over Time')
    plt.tight_layout()
    dispersion_path = folderpath + outfile + "-dispersion.png"
    fig.savefig(dispersion_path)
    print(dispersion_path)

def get_user_args():
    """Parser for command line arguments."""
    # main parser
    parser = argparse.ArgumentParser(description='Visualize gaze data as either \
        a heatmap, event graph or event chart. Output is saved to ./results.')
    subparsers = parser.add_subparsers()
    # heatmap sub-command
    parser_heatmap = subparsers.add_parser('heatmap',
        help='Creates a heatmap as a single PNG image or MP4 video.',
        description="Creates a heatmap as a single PNG image or MP4 video.")
    parser_heatmap.add_argument('-d', '--data-file',
        help='Gaze data file',
        required=True)
    parser_heatmap.add_argument('-f', '--format',
        help='output format [png, mp4]',
        choices=['png', 'mp4'],
        required=True)
    parser_heatmap.add_argument('-s', '--scheme',
        help='colour scheme for heatmap [classic, fire, omg, pbj, pgaitch]',
        choices=['classic', 'fire', 'omg', 'pbj', 'pgaitch'],
        default='classic')
    parser_heatmap.add_argument('-o', '--opacity',
        help='strength of a single point in heatmap (from 0-255)',
        default=128,
        type=int)
    parser_heatmap.add_argument('-p', '--point-size',
        help='size of a single point in heatmap',
        default=150,
        type=int)
    parser_heatmap.add_argument('-a', '--aoi-file',
        help='Area of interest file')
    parser_heatmap.set_defaults(func=create_heatmap)
    # graph sub-command
    parser_graph = subparsers.add_parser('graph',
        help='Creates a graph of area of interest events.')
    parser_graph.add_argument('-d', '--data-file',
        help='Gaze data file',
        required=True)
    parser_graph.add_argument('-a', '--aoi-file',
        help='Area of interest file',
        required=True)
    parser_graph.set_defaults(func=create_event_graph)
    # chart sub-command
    parser_chart = subparsers.add_parser('chart',
        help='Creates a barchart of area of interest events by duration or dispersion.',
        description="Creates a barchart of area of interest events by duration or dispersion.")
    parser_chart.add_argument('-d', '--data-file',
        help='Gaze data file',
        required=True)
    parser_chart.add_argument('-a', '--aoi-file',
        help='Area of interest file',
        required=True)
    parser_chart.set_defaults(func=create_event_chart)
    return parser.parse_args()

if __name__ == '__main__':
    args = get_user_args()
    args.func()
