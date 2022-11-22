from pathlib import Path
from typing import Dict, Any, TypeVar

BASE_PATH = Path(__file__).resolve().parent

DirType = TypeVar('DirType', bound='Dir')


class Dir:
    _base : Dict[str, Any] = {
            'config': BASE_PATH / 'config.json',
            'local': {
                'base': BASE_PATH / '.local',
                'sar_image': BASE_PATH / '.local' / 'sar_image',
                'chandrayaan2': BASE_PATH / '.local' / 'chandrayaan2'
                },
            'data': {
                'base': BASE_PATH / 'data',
                'chandrayaan2': BASE_PATH / 'data' / 'chandrayaan2'
                }
            }


    def __init__(self, dir_dict: Dict[str, Any], base: bool = True) -> None:
        if base:
            self._dirs = self._base.copy()
            self.__update_dirs__(dir_dict=dir_dict)
        else:
            self._dirs = dir_dict

        for dir_name, dirs in self._dirs.items():
            if isinstance(dirs, dict):
                self._dirs[dir_name] = Dir(dirs, base=False)

    def __update_dirs__(self, dir_dict: Dict[str, Any]) -> None:
        for ele in ('local', 'data'):
            if ele in dir_dict and 'base' in dir_dict[ele]:
                ele_dict = dir_dict[ele]
                ele_base_path = ele_dict['base']
                for key in self._dirs[ele]:
                    if key in ele_dict:
                        self._dirs[ele][key] = ele_dict[key]
                    else:
                        self._dirs[ele][key] = ele_base_path / key 
        self._dirs.update(dir_dict)

    def __getattr__(self: DirType, name: str) -> Path | DirType:
        if name in self._dirs:
            return self._dirs[name]
        else:
            raise AttributeError(f"Attribute: {name} does not exits.")

    @property
    def dirs(self) -> Dict[str, Any]:
        dirs = dict()
        for dir_name, path in self._dirs.items():
            if isinstance(path, Dir):
                dirs[dir_name] = path.dirs
            else:
                dirs[dir_name] = path
        return dirs

    def __repr__(self) -> str:
        return str(self.dirs)
    
    def __str__(self) -> str:
        return str(self.dirs)
        
