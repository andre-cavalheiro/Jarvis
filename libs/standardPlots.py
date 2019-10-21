from os.path import join
from os import walk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors

colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)
reds = ['lightcoral', 'indianred', 'darkred', 'r', 'lightsalmon']
blues = ['deepskyblue', 'darkcyan', 'lightskyblue', 'steelblue', 'azure']
greens = ['g', 'limegreen', 'forestgreen', 'mediumseagrean', 'palegreen']
greys = ['dimgrey', 'darkgrey', 'lightgrey', 'slategrey', 'silver']
pinks = ['magenta', 'violet', 'purple', 'hotpink', 'pink']
pallets = [reds, blues, greens, greys, pinks]

"""
# Only supports logfile CSV
def plotDemStats(dir, x, ys, logFile, yAxes=[], ymin=None, ymax=None, dpi=180):
    outputName = x + ' by ['
    for n in ys:
        outputName += '{}, '.format(n)
    outputName = outputName + ']'
    outputName = join(dir, outputName)

    csvLocation = join(dir, logFile)
    data = pd.read_csv(csvLocation, sep='\t', index_col=0, encoding='utf-8')
    '''fig, ax = plt.subplots()
    multipleYsLinePlot(ax, data, ys, x, colors=[], dpi=180)
    plt.xlabel(x)
    if yAxes:
        plt.ylabel(yAxes)
    if ymin:
        ax.set_ylim(bottom=0)
    if ymax:
        ax.set_ylim(top=ymax + ymax * 0.1)
    ax.legend()
    plt.savefig(outputName + '.png', dpi=dpi)'''
    makeImage([data], ys, x, outputName, yAxes, ymin, ymax, dpi)
"""

# Only supports logfile CSV
def plotDemStats(level, dir, x, ys, logFile, yLabels=[], yAxes='', ymin=None, ymax=None, pallets=False, dpi=180):

    outputName = buildOutputName(x, ys, dir)

    if level == 'localCSV':
        csvLocation = join(dir, logFile)
        data = pd.read_csv(csvLocation, sep='\t', index_col=0, encoding='utf-8')
        data = [data]
    elif level == 'fetchCSV':
        data = fetchLogsFromDirs(logFile, dir)
    else:
        print('unkown level')
        exit()

    makeImage(data, ys, x, yLabels, outputName, yAxes, ymin, ymax, dpi, usePallets=pallets)

def fetchLogsFromDirs(logFile, dir):
    results = []
    for subdir, dirs, files in walk(dir):
        for f in dirs:
            outFile = join(subdir, f, logFile)
            data = pd.read_csv(outFile, sep='\t', index_col=0, encoding='utf-8')
            results.append(data)
        break  # Only apply recursivness once
    return results

def makeImage(data, ys, x, yLabels=[], outputName='', yAxes='', ymin=None, ymax=None, dpi=180, usePallets=False):

    fig, ax = plt.subplots()

    labelsToUse = yLabels if len(yLabels) == len(data) else ['' for i in data]
    for i, res in enumerate(data):
        if usePallets:
            multipleYsLinePlot(ax, res, ys, x, colors=pallets[i], labels=labelsToUse[i])
        else:
            multipleYsLinePlot(ax, res, ys, x, labels=labelsToUse[i])

    plt.xlabel(x)
    if yAxes:
        plt.ylabel(yAxes)
    if ymin:
        ax.set_ylim(bottom=0)
    if ymax:
        ax.set_ylim(top=ymax + ymax * 0.1)
    ax.legend()
    plt.savefig(outputName + '.png', dpi=dpi)

def multipleYsLinePlot(ax, data, y_types, x_type, colors=[], labels=[]):
    '''
    :param data:    (pd.Dataframe) Data out of output.csv
    :param y_types: (array) Headers to be used from output.csv
    :param x_type:  (str) Single header to be used as x, from output.csv
    :return:
    '''
    assert(len(y_types)>0)
    if x_type == None or x_type == "index":
        x = [str(v) for v in data.index.values]
    else:
        data = data.sort_values(by=[x_type])
        x = data[x_type]

    maxNum = 0
    labelsToUse = labels if len(labels) == len(y_types) else ['' for y in y_types]
    for i, t in enumerate(y_types):
        if colors:
            ax.plot(x, data[t], label=labelsToUse[i], color=colors[i])
        else:
            ax.plot(x, data[t], label=labelsToUse[i])
        maxNum = max(data[t]) if max(data[t]) > maxNum else maxNum

def buildOutputName(x, ys, dir):
    outputName = x + ' by ['
    for n in ys:
        outputName += '{}, '.format(n)
    outputName = outputName + ']'
    outputName = join(dir, outputName)
    return  outputName