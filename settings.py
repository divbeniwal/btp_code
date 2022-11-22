from pathlib import Path 
from dir import BASE_PATH

DIR = {
#        'config': BASE_PATH / "config.json",
#        'local': {
#            'base': BASE_PATH / ".local",
#            'sar_image': BASE_PATH / ".local" / "sar_image",
#            'chandrayaan2': BASE_PATH / ".local" / "chandrayaan-2",
#            'chandrayaan2': Path('--- path to the directory / folder ---')
#            },
        'data': {
            'base': BASE_PATH / "data",
            'chandrayaan2': BASE_PATH / "data" / "isro_data",
            },
#         TODO: matlab
        }

