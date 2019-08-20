import yaml
import argparse
from os.path import join, exists, isfile
from os import makedirs, listdir
import random, string


# Hack for non-default
class NonDefaultVerifier(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        setattr(namespace, self.dest+'_nonDefault', True)


# Import yaml
def getConfiguration(configFile):
    with open(configFile, 'r') as stream:
        try:
            params = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return params


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


def getWorkDir(jconfig, folderName, extraName='', createNew=True):
    if 'outputDir' in jconfig.keys():
        outputDir = jconfig['outputDir']
    else:
        return '.'  # todo Maybe /tmp ?
    return makeDir(outputDir, folderName + extraName, createNew=createNew)


def makeDir(outputDir, name, createNew=True):
    dir = join(outputDir, name)
    if not exists(dir):
        print('> Created Directory - "{}"'.format(dir))
        makedirs(dir)
    else:
        j = 1
        while exists(dir):
            j += 1
            dir = join(outputDir, '{}-{}'.format(name, j))
        if createNew:
            print('> Directory already exists, using - "{}"'.format(dir))
            makedirs(dir)
        else:
            print('> Using already existent dir - "{}"'.format(dir))
    return dir


def getFilesInDir(dir):
    files = [f for f in listdir(dir) if isfile(join(dir, f))]
    return files


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


def getTrialValuesFromConfig(trial, pconfig, argListPuppet):
    for arg in argListPuppet:
        trialVal = getTrialValues(trial, arg)
        pconfig[arg['name']] = trialVal if trialVal is not None else pconfig[arg['name']]
        if 'children' in arg.keys():
            for childArg in arg['children']:
                trialVal = getTrialValues(trial, childArg)
                pconfig[arg['name']][childArg['name']] = trialVal if trialVal is not None \
                    else pconfig[arg['name']][childArg['name']]

    return pconfig


def getTrialValues(trial, arg):
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