from sys import exit
from libs.utils import *
from libs.dir import *
from libs.standardPlots import *
from src.puppet import Puppet
from src.args import argListPuppet
from argsConf.jarvisArgs import argListJarvis
from argsConf.plotArgs import argListPlots
from os.path import join
import optuna

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

# Attribute random name to test run if one wasn't provided
if 'name' not in jconfig.keys() or ('name' in jconfig.keys() and jconfig['name'] is None):
    jconfig['name'] = randomName(7)

printDict(jconfig, statement="> JARVIS using args:")

# Import plot args:
if 'confPlot' in jconfig.keys():
    plotConfig = getConfiguration(jconfig['confPlot'])

if 'optimizer' in jconfig.keys() and 'optimize' in jconfig.keys() and jconfig['optimize']:

    # Create working directory here since it cannot be inside optimization function
    optimizationDir = getWorkDir(jconfig, 'optimization - {}'.format(jconfig['name']), completedText=jconfig['successString'])

    def optimizationObjective(trial):
        # fixme - Lots of unnecessary accesses to the file
        print("=== NEW TRIAL ==  ")

        pconfig = getConfiguration(jconfig['conf'])

        for arg in argListPuppet:
            if arg['name'] not in pconfig.keys():
                pconfig[arg['name']] = None         # todo This may be needed somewhere else
        pconfig = getTrialValuesFromConfig(trial, pconfig, argListPuppet)
        printDict(pconfig, "> Trial for: ")
        pconfig = selectFuncAccordingToParams(pconfig, argListPuppet)

        # Get working directory name that was created in the beginning of the optimization procedure.
        optimizationDir = getWorkDir(jconfig, 'optimization - {}'.format(jconfig['name']), createNew=False, completedText=jconfig['successString'])
        dir = makeDir(optimizationDir, 'trial', completedText=jconfig['successString'])

        puppet = Puppet(pconfig, debug=jconfig['debug'], outputDir=dir)
        reward = puppet.pipeline()
        dumpConfiguration(pconfig, dir, unfoldConfigWith=argListPuppet)
        changeDirName(dir, extraText=jconfig['successString'])

        return reward

    print("==========        RUNNING OPTIMIZATION FOR - [{}]     ==========".format(jconfig['name']))

    study = optuna.create_study(study_name=jconfig['name'], load_if_exists=True)

    try:
        study.optimize(optimizationObjective, n_trials=jconfig['optimizer']['numTrials'], \
                       n_jobs=jconfig['optimizer']['numJobs'])
        # Use catch param?
        # Use storage='sqlite:///example.db'
    except KeyboardInterrupt:
        pass

    results = study.trials_dataframe()
    results.to_csv(join(optimizationDir, 'optimizationTrials.csv'))


# Import puppet configuration and run single/sequential tests
else:

    if 'only' in jconfig['plot']:
        # Instead of running puppet, simply make some plots

        dir = join(jconfig['outputDir'], plotConfig['plotOnlyParams']['dir'])
        c = makePlotConf(plotConfig, 'plotOnlyParams')
        makePrettyPlots(jconfig['plot'], c, argListPlots, 'only', dir, unify=False)
        exit()

    if jconfig['seq']:
        # Sequential test:
        
        configs = getConfiguration(jconfig['confSeq'])['configs']
        if 'confSeq' not in jconfig.keys():
            print('> Missing configuration file for sequential testing - exiting')
            exit()

        pconfigs = []
        
        # Process each configuration process it and verify its validity
        for it, conf in enumerate(configs):
            pconfig = selectFuncAccordingToParams(conf, argListPuppet)
            pconfigs.append(pconfig)

            for arg in argListPuppet:
                if arg['name'] not in pconfig.keys() and arg['required']:
                    print('> Missing required argument "{}" in testrun with index "{}" '.format(arg['name'], it))
                    print('> !!! Ignoring testrun index - {} !!!'.format(it))
                    pconfigs.pop()
                    break

        # Create Directory for outputs
        seqTestDir = getWorkDir(jconfig, 'sequential - {}'.format(jconfig['name']), completedText=jconfig['successString'])

        print("==========        RUNNING TEST RUN - [{}]     ==========".format(jconfig['name']))
        # Run instances
        for pconfig in pconfigs:
            print("=== NEW INSTANCE ==  ")
            printDict(pconfig, statement="> Using args:")
            # Create output directory for instance inside sequential-test directory
            dir = makeDir(seqTestDir, 'testrun', completedText=jconfig['successString'])

            puppet = Puppet(pconfig, debug=jconfig['debug'], outputDir=dir)
            puppet.pipeline()
            dumpConfiguration(pconfig, dir, unfoldConfigWith=argListPuppet)

            c = makePlotConf(plotConfig, 'plotSingleParams')
            makePrettyPlots(jconfig['plot'], c, argListPlots, 'single', dir, unify=False)

            changeDirName(dir, extraText=jconfig['successString'])

        c=makePlotConf(plotConfig, 'plotSeqParams')
        makePrettyPlots(jconfig['plot'], c, argListPlots, 'seq', seqTestDir, unify=True,
                        logFile='logs.json', configFile='config.yaml', unificationType=plotConfig['seqLogConversion'])
        changeDirName(seqTestDir, extraText=jconfig['successString'])

    else:
        # Single test:

        print('> Importing puppet configuration from {}'.format(jconfig['conf']))
        pconfig = getConfiguration(jconfig['conf'])
        pconfig = selectFuncAccordingToParams(pconfig, argListPuppet)

        # Upgrade arguments if command line ones were passed and attribute None value to params which were not passed
        for arg in argListPuppet:
            if arg['name'] in argsPassedPuppet:
                pconfig[arg['name']] = clArgs[arg['name']]
            elif arg['name'] not in pconfig.keys():
                pconfig[arg['name']] = None

        print("==========        RUNNING TEST RUN - [{}]     ==========".format(jconfig['name']))
        printDict(pconfig, statement="> Using args:")

        # Create output directory for instance
        dir = getWorkDir(jconfig, jconfig['name'], completedText=jconfig['successString'])

        # Run instance
        puppet = Puppet(args=pconfig, debug=jconfig['debug'], outputDir=dir)
        puppet.pipeline()
        dumpConfiguration(pconfig, dir, unfoldConfigWith=argListPuppet)

        c=makePlotConf(plotConfig, 'plotSingleParams')
        makePrettyPlots(jconfig['plot'], c, argListPlots, 'single', dir, unify=False)

        changeDirName(dir, extraText=jconfig['successString'])


