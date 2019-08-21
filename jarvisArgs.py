from utils import str2bool

argListJarvis = [{
        'name': 'jc',
        'type': str,
        # 'default': None,
        'default': 'jarvisConfig.yaml',
        'required': False,
        'help': 'Jarvis configuration file (yaml).'
    },
    {
        'name': 'debug',
        'type': str2bool,
        'default': False,
        'required': False,
        'help': 'Whether in debug mode or not'
    },
    {
        'name': 'optimizer',
        'type': str,
        'default': False,
        'required': False,
        'help': 'Whether in optimizer mode or not'
    },
    {
        'name': 'conf',
        'type': str,
        'default': None,
        'required': False,
        'help': 'Configuration file for child program.'
    },
    {
        'name': 'seq',
        'type': str2bool,
        'default': False,
        'required': False,
        'help': 'Indicate whether multiple or single test [default: False]'
    },
    {
        'name': 'confDir',
        'type': str,
        'default': None,
        'required': False,
        'help': 'Directory in which configuration files are located for sequential testing.'
    },
    {
        'name': 'outputDir',
        'type': str,
        'default': None,
        'required': False,
        'help': 'Output Directory'
    }
]