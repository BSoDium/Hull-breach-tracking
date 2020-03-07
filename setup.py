from setuptools import setup

setup(
    name = "Wave Engine",
    options = {
        'build_apps': {
            'include_patterns':[
                '**/*.png'
        ],
        'platforms':['win_amd64'],
        
        'gui_apps':{
            'Wave_Engine':'main.py',
        },
        'plugins':[
            'pandagl'
        ],
        }
        }
)