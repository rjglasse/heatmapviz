"""Creates a list of area of interest (AOI) events from gaze tracking data"""

import os
import argparse
import csv
import math

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
        if x_coord > aoi["x1_coord"] and x_coord < aoi["x2_coord"] \
            and y_coord > aoi["y1_coord"] and y_coord < aoi["y2_coord"]:
            return aoi["area"]
    return False

def create_aoi_events():
    """Build a list of area of interest events [area, gazepoints, duration, dispersion]"""
    # create output folder
    folderpath = "./aoi/" + args.datafile.split('.')[0]
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    print("Saving aoi events to " + folderpath)

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
            aoi_events.append({"area":area, "points":[], "start":timestamp})
            aoi_events[-1]["points"].append((x_coord, y_coord))
    # TODO: calculate summary stats for duration and dispersion
    return aoi_events

def dispersion(points):
    """Calculate the standard distance deviation for an area of interest event"""
    sum_x = 0
    sum_y = 0
    for point in points:
        sum_x += point[0]
        sum_y += point[1]
    avg_x = sum_x / len(points)
    avg_y = sum_y / len(points)

    print("Mean Center: {0}, {1}".format(avg_x, avg_y))
    sum_of_sq_diff_x = 0.0
    sum_of_sq_diff_y = 0.0

    for x, y in points:
        diff_x = math.pow(x - avg_x, 2)
        diff_y = math.pow(y - avg_y, 2)
        sum_of_sq_diff_x += diff_x
        sum_of_sq_diff_y += diff_y
    sum_of_results = (sum_of_sq_diff_x/len(points)) + (sum_of_sq_diff_y/len(points))
    standard_distance = math.sqrt(sum_of_results)
    print("Standard Distance: {0}". format(standard_distance))
    return standard_distance

if __name__ == '__main__':
    args = get_user_args()
    data = read_et_data(args.datafile)
    aois = read_aoi_data(args.aoifile)
    # print(aois)
    events = create_aoi_events()
    dispersion(events[0]["points"])
