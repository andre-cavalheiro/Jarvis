from libs.utils import str2bool, randomName

argListJarvis = [{
        'name': 'jc',
        'type': str,
        # 'default': None,
        'default': 'jarvisConfig.yaml',
        'required': False,
        'help': 'Jarvis configuration file (yaml).'
    },
    {
        'name': 'name',
        'type': str,
        'default': randomName(7),
        'required': False,
        'help': 'Name of test run [default: random string with 7 characters].'

    },
    {
        'name': 'debug',
        'type': str2bool,
        'default': False,
        'required': False,
        'help': 'Whether in debug mode or not'
    },
    {
        'name': 'conf',
        'type': str,
        'default': 'src/config.yaml',
        'required': False,
        'help': 'Configuration file for puppet program. (default: src/config.yaml)'
    },
    {
        'name': 'confSeq',
        'type': str,
        'default': 'src/configSeq.yaml',
        'required': False,
        'help': 'Configuration file for puppet program in sequential mode. (default: src/configSeq.yaml)'
    },
    {
        'name': 'outputDir',
        'type': str,
        'default': None,
        'required': False,
        'help': 'Output Directory'
    },
    {
        'name': 'seq',
        'type': str2bool,
        'default': False,
        'required': False,
        'help': 'Indicate whether multiple or single test [default: False]'
    },
    {
        'name': 'optimize',
        'type': str,
        'default': False,
        'required': False,
        'help': 'Whether in optimizer mode or not'
    },
    {
        'name': 'optimizer',
        'type': str,  # Actually an object
        'default': False,
        'required': False,
        'help': 'Whether in optimizer mode or not'
    },
    {
        'name': 'successString',
        'type': str,
        'default': ' - finished',
        'required': False,
        'help': 'The text that will appear attached to the directories name whenever a testrun finishes sucessfully\
                [default: " - finished"]'
    },
]