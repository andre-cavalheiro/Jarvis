from libs.standardPlots import *

argListPlots = [
    {
        'name': 'singlePlotTypes',
        'type': str,
        'default': None,
        'required': False,
        'help': '',
        'possibilities': [
            ('line', plotDemStats, [('yAxes', 'standard'), ('logFile', 'shared'),
                                   ('ymin', 'shared'), ('ymax', 'shared')])
            ]
    },
    {
        'name': 'seqPlotTypes',
        'type': str,
        'default': None,
        'required': False,
        'help': '',
        'possibilities': [
            ('line', plotDemStats, [('yAxes', 'standard'), ('logFile', 'shared'),
                                    ('ymin', 'shared'), ('ymax', 'shared')]),
        ]
    },
    {
        'name': 'onlyPlotTypes',
        'type': str,
        'default': None,
        'required': False,
        'help': '',
        'possibilities': [
            ('lineHigher', plotDemStats, [('yAxes', 'standard'), ('pallets', 'shared'), ('yLabels', 'shared'),
                                          ('logFile', 'shared'), ('ymin', 'shared'), ('ymax', 'shared'), ])
        ]
    },
]