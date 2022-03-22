"""Creates a list of area of interest (AOI) events from gaze tracking data"""

import os
import argparse
import csv
import math
import graphviz
import numpy as np
import matplotlib.pyplot as plt

def get_user_args():
    """Parser for command line arguments."""
    parser = argparse.ArgumentParser(description='Creates a list of area of interest \
    events from gaze tracking data')
    parser.add_argument('-d', '--datafile', help='input gaze tracking CSV file', required=True)
    parser.add_argument('-a', '--aoifile', help='input area of interest CSV file', required=True)
    return parser.parse_args()

def read_et_data(filename):
    """Read eyetracking CSV file and convert to a list of ['x', 'y', 'timestamp'] elements."""
    with open(filename, 'r') as csv_file:
        reader = csv.reader(csv_file)
        return list(reader)

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

def create_aoi_events():
    """Build a list of area of interest events [area, gazepoints, duration, dispersion]"""
    # create filename and output folder
    outfile = "/" + os.path.split(args.datafile)[1].split(".")[0] + ".csv"
    folderpath = "./results/csv/" + os.path.split(args.datafile)[1].split(".")[0]
    print(folderpath)
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    print("Saving events to " + folderpath)
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
    # calculate duration and dispersion for aoi_events
    with open(folderpath+outfile, 'w', newline='') as file:
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

def create_event_graph(aoi_events):
    """Create a directed graph of area of interest events"""
    # create filename and output folder
    outfile = os.path.split(args.datafile)[1].split('.')[0]
    folderpath = "./results/graph/" + os.path.split(args.datafile)[1].split('.')[0]
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    print("Saving graph to " + folderpath)
    # find and count edges
    edges = {}
    source_vertex = aoi_events[0]["area"]
    for event in aoi_events[1:]:
        dest_vertex = event["area"]
        edge = source_vertex + " -> " + dest_vertex
        try:
            edges[edge] += 1
        except KeyError:
            edges[edge] = 1
        source_vertex = dest_vertex
    # generate graphviz
    dot = graphviz.Digraph(outfile, comment="test", format="pdf")
    for edge, count in edges.items():
        src, dst = edge.split(" -> ")
        dot.edge(src, dst, label=str(count))
    # render and show graph immediately
    dot.render(directory=folderpath)

def create_event_chart(aoi_events):
    """: Create a barchart timeline of events and output to file"""
    # create filename and output folder
    outfile = os.path.split(args.datafile)[1].split('.')[0]
    folderpath = "./results/chart/" + os.path.split(args.datafile)[1].split('.')[0]
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    print("Saving graph to " + folderpath)
    # extract data to lists
    areas = []
    durations = []
    dispersions = []
    for event in aoi_events:
        areas.append(event["area"])
        durations.append(event["duration"])
        dispersions.append(event["dispersion"])
    # plot chart for duration
    y_pos = np.arange(len(areas))
    fig = plt.figure()
    plt.bar(y_pos, durations, align='center', alpha=0.5)
    plt.xticks(y_pos, areas, rotation='vertical')
    plt.ylabel('Duration (??)')
    plt.title('Areas of Interest over Time')
    plt.tight_layout()
    fig.savefig(folderpath+"/"+outfile+"-duration.pdf")
    # plot chart for dispersion
    fig = plt.figure()
    plt.bar(y_pos, dispersions, align='center', alpha=0.5)
    plt.xticks(y_pos, areas, rotation='vertical')
    plt.ylabel('Dispersion (SDD)')
    plt.title('Areas of Interest over Time')
    plt.tight_layout()
    fig.savefig(folderpath+"/"+outfile+"-dispersion.pdf")

if __name__ == '__main__':
    args = get_user_args()
    data = read_et_data(args.datafile)
    aois = read_aoi_data(args.aoifile)
    events = create_aoi_events()
    create_event_graph(events)
    create_event_chart(events)
