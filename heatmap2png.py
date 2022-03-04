import argparse
import os
import heatmap
import csv

if __name__ == "__main__":

    # read the CSV filepath as an argument
    parser = argparse.ArgumentParser(description='Generate a Heatmap PNG from a CSV file with [x, y, ...] format.')
    parser.add_argument('-f', dest='filepath', help='path to CSV file', required=True)
    args = parser.parse_args()

    # create folders for results
    folderpath = "./png/" + args.filepath.split('.')[0]
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)

    print("Saving heatmap to " + folderpath)

    # read CSV and convert to a list of ['x', 'y', 'timestamp'] elements
    with open(args.filepath, newline='') as f:
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
    outfile = "/" + args.filepath.split('.')[0] + ".png"
    img = hm.heatmap(coord_data, size=resolution).save(folderpath + outfile)
