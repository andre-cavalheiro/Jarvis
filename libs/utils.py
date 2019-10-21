import argparse
from os.path import join
from os import walk
import random, string
from pathlib import Path
import json
import pandas as pd
import yaml

# Import yaml
def getConfiguration(configFile):
    with open(configFile, 'r') as stream:
        params = yaml.safe_load(stream)
    return params


# Dump yaml
def dumpConfiguration(configDict, direcotry, unfoldConfigWith=None):
    if unfoldConfigWith:
        configDict = selectParamsAccordingToFunctions(configDict, unfoldConfigWith) # Reverse functions to its arg names
    t = join(direcotry, 'config.yaml')
    with open(t, 'w') as f:
        yaml.dump(configDict, f, default_flow_style=False)


# Hack for non-default
class NonDefaultVerifier(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        setattr(namespace, self.dest+'_nonDefault', True)


#  Dynamic boolean type for argument parser
def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def randomName(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


def printDict(dict, statement=None):
    if statement:
        print(statement)
    for attr, value in sorted(dict.items()):
        print("\t{}={}".format(attr.upper(), value))


def selectFuncAccordingToParams(config, argList):
    for a in argList:
        if 'possibilities' in a.keys() and len(a['possibilities']) is not 0:
            for p in a['possibilities']:
                if p[0] == config[a['name']]:
                    config[a['name']] = p[1]
                    break
    return config


def selectParamsAccordingToFunctions(config, argList):
    for a in argList:
        if 'possibilities' in a.keys() and len(a['possibilities']) is not 0:
            for p in a['possibilities']:
                if p[1] == config[a['name']]:
                    config[a['name']] = p[0]
                    break
    return config


def getTrialValuesFromConfig(trial, pconfig, argListPuppet):
    for arg in argListPuppet:
        trialVal = getTrialValues(trial, arg)
        pconfig[arg['name']] = trialVal if trialVal is not None else pconfig[arg['name']]
        if 'children' in arg.keys() and pconfig[arg['name']] is not None:
            for childArg in arg['children']:
                trialVal = getTrialValues(trial, childArg)
                pconfig[arg['name']][childArg['name']] = trialVal if trialVal is not None \
                    else pconfig[arg['name']][childArg['name']]

    return pconfig


def getTrialValues(trial, arg):
    if 'optimize' in arg.keys() and arg['optimize']:
        if 'optimizeInt' in arg.keys():
            return trial.suggest_int(arg['name'], arg['optimizeInt'][0], \
                                                     arg['optimizeInt'][1])

        elif 'optimizeUniform' in arg.keys():
            return trial.suggest_uniform(arg['name'], arg['optimizeUniform'][0], \
                                                         arg['optimizeUniform'][1])

        elif 'optimizeLogUniform' in arg.keys():
            return trial.suggest_loguniform(arg['name'], arg['optimizeLogUniform'][0], \
                                                            arg['optimizeLogUniform'][1])

        elif 'optimizeDiscreteUniform' in arg.keys():
            return trial.suggest_loguniform(arg['name'], *arg['optimizeDiscreteUniform'])

        elif 'optimizeCategorical' in arg.keys():
            return trial.suggest_categorical(arg['name'], arg['optimizeCategorical'])
        else:
            return None
    else:
        return None


# Evaluate if situation demands for a plot, and if so apply the ones that are in order.
def makePrettyPlots(enabledModes, config, argListPlots, mode, dir, unify=False, logFile='logs.json',
                    configFile='config.yaml', unificationType=''):

    if mode == 'single':
        modeType = 'singlePlotTypes'
    elif mode == 'seq':
        modeType = 'seqPlotTypes'
    elif mode == 'only':
        modeType = 'onlyPlotTypes'

    # Check if plot mode is enabled
    if mode in enabledModes:
        # Some plots require the unification of outputs.
        if unify:
            if unificationType == 'yaml,json-Csv':
                unifyJsonYamlOutputsIntoCSV(dir, logFile=logFile, configFile=configFile)
            else:
                print('Unkown unification type {}'.format(unificationType))
                exit()

        # Get plot possibilities for selected mode
        g = (e for e in argListPlots if e.get('name') == modeType)
        plotTypes = next(g)

        assert (len(config['x']) == len(config['ys']))
        numPlots = len(config['x'])

        # For every plot possibility check which are selected for this specific mode
        for p in plotTypes['possibilities']:
            type = p[0]
            func = p[1]
            args = p[2]
            if type in config['type']:
                # Build common params between iterations and remove them from the other ones
                sharedParams = {a[0]: config[a[0]] for a in args if a[1] == 'shared' if a[0] in config.keys()}
                toDeleteInd = [i for i, a in enumerate(args) if a[0] in sharedParams.keys()]
                for index in sorted(toDeleteInd, reverse=True):
                    del args[index]

                # Plot
                for j in range(numPlots):
                    # Build iteration specific params
                    params = {n[0]: config[n[0]][j] for n in args if n[0] in config.keys()}
                    func(x=config['x'][j], ys=config['ys'][j], dpi=config['dpi'], level=config['level'], **params, **sharedParams, dir=dir)

# Unify several config.yamls and and logs.json into a single output.csv for the overall sequential running
def unifyJsonYamlOutputsIntoCSV(dir, logFile='logs.json', configFile='config.yaml'):
    logType = logFile.split('.')[-1]
    datasetCols = {}

    for subdir, dirs, files in walk(dir):
        for subdir in dirs:
            # todo - Check name to avoid sequentials and optimizations
            subpathToConf = join(dir, subdir, configFile)
            subpathToOutput = join(dir, subdir, logFile)

            conf = getConfiguration(subpathToConf)
            conf = removeNestedDict(conf)

            with open(subpathToOutput) as f:
                if logType == 'json':
                    outputs = json.load(f)
                elif logType == 'csv':
                    pass
                else:
                    print('Unknown format {}'.format(logType))

            conf.update(outputs)

            newAddOns = []

            for key, val in conf.items():
                if key in datasetCols.keys():
                    datasetCols[key].append(val)
                else:
                    newAddOns.append((key, val))

            for t in newAddOns:
                datasetCols[t[0]] = [t[1]]

    unified_results = pd.DataFrame(data=datasetCols)
    unified_results.to_csv("{}/output.csv".format(dir), sep='\t', encoding='utf-8')

    return unified_results


def removeNestedDict(d):
    newAddOns = []
    for key, val in d.items():
        if isinstance(val, dict):
            for key_, val_ in val.items():
                newAddOns.append((key, key_, val_))
    for t in newAddOns:
        if t[0] in d.keys():
            d.pop(t[0])
        d[t[1]] = t[2]
    return d


def makePlotConf(plotConfig, paramType):
    a = plotConfig.copy()
    b = plotConfig[paramType]
    del a['plotSingleParams']
    del a['plotSeqParams']
    del a['plotOnlyParams']
    a.update(b)
    return a
