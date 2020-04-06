from setuptools import setup

setup(
    name = "Wave Engine",
    options = {
        'build_apps': {
            'include_modules': [
                'pypresence',
                'numpy',
                'pywin32'
            ],
            'include_patterns':[
                '**/*.png',
                '**/*.ttf',
                '**/*.egg'
            ],
            'platforms':['win_amd64'
            ],
            'gui_apps':{
                'Wave_Engine':'main.py',
            },
            'plugins':[
                'pandagl'
            ],
        }
    }
)