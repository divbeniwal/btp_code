import json
import chandrayaan_2

from settings import *

from pathlib import Path


def get_config(config_file_path: Path) -> dict:
    res: dict = dict()
    with config_file_path.open('r') as config:
        res = json.load(config)
    return res


def setup() -> chandrayaan_2.Chandrayaan2:
    config = get_config(DIR['CONFIG'])

    # get configs
    DIR['DATA']['BASE'] = Path(config['dir']['data'])
    DIR['DATA']['CHANDRAYAAN-2']['BASE'] = Path(config['dir']['chandrayaan_2'])
    DIR['MATLAB']['BASE_PATH'] = Path(config['dir']['matlab'])

    # extract chandaryaan-2 data folders
    chObj = chandrayaan_2.Chandrayaan2(
            path=config['dir']['chandrayaan_2'],
            local_path=DIR['LOCAL']['CHANDRAYAAN-2']
            )

    DIR['DATA']['CHANDRAYAAN-2'] = chObj.get_dirs()
    return chObj


def main() -> None:
    setup()


if __name__ == "__main__":
    main()
