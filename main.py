import argparse
from sys import exit
from utils import *
from src.dummyClass import Dummy
from src.args import argListPuppet
from jarvisArgs import argListJarvis
from os.path import join
import optuna
from termcolor import colored

# todo - output configurations to output dir

# Verify command line arguments
parser = argparse.ArgumentParser(description='[==< J A R V I S >==]')
for arg in argListJarvis:
    parser.add_argument('-{}'.format(arg['name']), type=arg['type'], default=arg['default'], required=arg['required'],
                        help=arg['help'], action=NonDefaultVerifier)
for arg in argListPuppet:
    parser.add_argument('-{}'.format(arg['name']), type=arg['type'], default=arg['default'], required=False,
                        help=arg['help'], action=NonDefaultVerifier)
clArgs = parser.parse_args()
argsPassedJarvis = [a['name'] for a in argListJarvis if hasattr(clArgs, '{}_nonDefault'.format(a['name']))]     # Find which params were actually passed
argsPassedPuppet = [a['name'] for a in argListPuppet if hasattr(clArgs, '{}_nonDefault'.format(a['name']))]     # Find which params were actually passed
clArgs = vars(clArgs)      # Convert to dictionary

# Import jarvis configurations if it exists
if clArgs['jc']:
    print('> Importing configuration from {}'.format(clArgs['jc']))
    jconfig = getConfiguration(clArgs['jc'])
    # Upgrade values if command line ones were passed
    for key in argsPassedJarvis:
        jconfig[key] = clArgs[key]

# If no config file then use only command line args
else:
    # Check if all required arguments have been passed
    jconfig = {}
    for arg in argListJarvis:
        if arg['required'] and arg['name'] not in argsPassedJarvis:
            print('> Missing required JARVIS argument "{}" - exiting'.format(arg['name']))
            exit()
        else:
            jconfig[arg['name']] = clArgs[arg['name']]

printDict(jconfig, statement="> Using args:")

if 'optimizer' in jconfig.keys() and jconfig['optimizer']['use']:
    # Create working directory here since it cannot be inside optimization function
    getWorkDir(jconfig, 'optimization')

    def optimizationObjective(trial):
        # fixme - Lots of unnecessary accessess to the file
        pconfig = getConfiguration(jconfig['conf'])
        pconfig = getTrialValuesFromConfig(trial, pconfig, argListPuppet)
        printDict(pconfig, "> Trial for: ")
        pconfig = selectFuncAccordingToParams(pconfig, argListPuppet)

        # Get working directory name that was created in the beginning of the optimization procedure.
        optimizationDir = getWorkDir(jconfig, 'optimization', createNew=False)
        dir = makeDir(optimizationDir, pconfig['name'])

        puppet = Dummy(pconfig, debug=jconfig['debug'], outputDir=dir)
        return puppet.pipeline()

    pconfig = getConfiguration(jconfig['conf'])
    # Attribute random name to test run if one wasn't provided
    if 'name' not in pconfig.keys():
        pconfig['name'] = randomName(7)
    print("==========        RUNNING OPTIMIZATION FOR - [{}]     ==========".format(pconfig['name']))

    study = optuna.create_study(study_name=pconfig['name'], load_if_exists=True)

    try:
        study.optimize(optimizationObjective, n_trials=jconfig['optimizer']['numTrials'], \
                       n_jobs=jconfig['optimizer']['numJobs'])  # Use catch param?
    except KeyboardInterrupt:
        pass

# Import puppet configuration and run single/sequential tests
else:
    if jconfig['seq']:
        # Sequencial test:

        if 'confDir' not in jconfig.keys():
            print('> Missing configuration directory for sequential testing - exiting')
            exit()
        # Import configurations
        conFiles = getFilesInDir(jconfig['confDir'])
        pconfigs = []
        for f in conFiles:
            pconfig = getConfiguration(join(jconfig['confDir'], f))
            pconfig = selectFuncAccordingToParams(pconfig, argListPuppet)

            pconfigs.append(pconfig)
            # Attribute random name to test run if one wasn't provided
            if 'name' not in pconfig.keys():
                pconfig['name'] = randomName(7)
            for arg in argListPuppet:
                if arg['name'] not in pconfig.keys() and arg['required']:
                    print('> Missing required argument "{}" in "{}" testrun'.format(arg['name'], pconfig['name']))
                    print('> !!! Ignoring testrun - {} !!!'.format(pconfig['name']))
                    pconfigs.pop()
                    break

        # Create Directory for outputs
        seqTestDir = getWorkDir(jconfig, 'sequencial-test')

        # Run instances
        for pconfig in pconfigs:
            print("==========        RUNNING TEST RUN - [{}]     ==========".format(pconfig['name']))
            printDict(pconfig, statement="> Using args:")
            # Create output directory for instance inside sequential-test directory
            dir = makeDir(seqTestDir, pconfig['name'])

            puppet = Dummy(pconfig, debug=jconfig['debug'], outputDir=dir)
            puppet.pipeline()

            # fixme - change yaml when name of directory has do be changed, or pass config file to inside the dir?
    else:
        # Single test:

        print('> Importing puppet configuration from {}'.format(jconfig['conf']))
        pconfig = getConfiguration(jconfig['conf'])
        pconfig = selectFuncAccordingToParams(pconfig, argListPuppet)

        # Upgrade arguments if command line ones were passed
        for key in argsPassedPuppet:
            pconfig[key] = clArgs[key]
        # Attribute random name to test run if one wasn't provided
        if 'name' not in pconfig.keys():
            pconfig['name'] = randomName(7)

        print("==========        RUNNING TEST RUN - [{}]     ==========".format(pconfig['name']))
        printDict(pconfig, statement="> Using args:")

        # Create output directory for instance
        dir = getWorkDir(jconfig, pconfig['name'])

        # Run instance
        puppet = Dummy(args=pconfig, debug=jconfig['debug'], outputDir=dir)
        puppet.pipeline()

        # fixme - change directory name to add success ? -> Requires changing a few things above when creating it
