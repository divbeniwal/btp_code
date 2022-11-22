from dir import Dir
from settings import DIR
from sar.models import Chandrayaan2

def get_dirs() -> Dir:
    return Dir(DIR)

def get_chandrayaan2Obj() -> Chandrayaan2:
    dir = Dir(DIR)
    if hasattr(dir, 'data') and hasattr(dir.data, 'chandrayaan2'):
        if dir.data.chandrayaan2.is_dir():
            return Chandrayaan2(
                    path=dir.data.chandrayaan2,
                    local_path=dir.local.chandrayaan2
                    )
        else:
            msg = f"directory for chandrayaan2 data files is incorrect, dir: {dir.data.chandrayaan2.__str__}"
            raise ValueError(msg)
    else:
        raise RuntimeError(f"Something went wrong, 'if hasattr(dir, 'data') and hasattr(dir.data, 'chandrayaan2'):' -> False")


if __name__ == "__main__":
    sar_img = get_chandrayaan2Obj().date_map['20210312']
    sar_img.multilook_azimuth(nmls=20, method='mean')