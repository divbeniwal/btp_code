import json
import chandrayaan_2

from settings import *

from pathlib import Path


def get_config(config_file_path: Path) -> dict:
    res: dict = dict()
    with config_file_path.open('r') as config:
        res = json.load(config)
    return res


def setup() -> chandrayaan_2.Chandrayaan_2:
    config = get_config(DIR['CONFIG'])

    # get configs
    DIR['CODE'] = Path(config['dir']['code'])
    DIR['DATA'] = Path(config['dir']['data'])
    DIR['CHANDRAYAAN-2']['BASE'] = Path(config['dir']['chandrayaan_2'])
    DIR['MATLAB']['BASE_PATH'] = Path(config['dir']['matlab'])

    # extract chandaryaan-2 data folders
    ch_data = chandrayaan_2.Chandrayaan_2(config['dir']['chandrayaan_2'])
    DIR['CHANDRAYAAN-2'] = ch_data.get_dirs()

    return ch_data


def main() -> None:
    setup()


if __name__ == "__main__":
    main()
