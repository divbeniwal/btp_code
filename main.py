from dir import Dir
from settings import DIR
from chandrayaan_2 import Chandrayaan2

def get_dirs() -> Dir:
    return Dir(DIR)

def get_chandrayaan2Obj() -> Chandrayaan2:
    dir = get_dirs()
    return Chandrayaan2(
            path=dir.data.chandrayaan2,
            local_path=dir.local.chandrayaan2
            )
