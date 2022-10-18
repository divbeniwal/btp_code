from pathlib import Path 

BASE_PATH = Path(__file__).resolve().parent.parent

DIR = {
        'CONFIG': BASE_PATH / "config.json",
        'DOWNLOADS' : BASE_PATH / "downloads",
        'LOCAL': {
            'BASE': BASE_PATH / ".local",
            'SAR_IMAGE': BASE_PATH / ".local" / "sar_image",
            'CHANDRAYAAN-2': BASE_PATH / ".local" / "chandrayaan-2"
            },
        'DATA': {
            'BASE': BASE_PATH / "data",
            'CHANDRAYAAN-2': {
                'BASE': BASE_PATH / "data" / "chandrayaan-2-data",
                'DATE_MAP': dict(),
                },
            },
        'MATLAB': {
            # TODO: access data file or code files from the matlab directory
            'BASE_PATH': None,
            'CODE': [],
            'DATA': [],
            },
        }


if __name__ == "__main__":
    # This part of the code is only for debugging
    print("Warning: this file ('settings.py') should not be ran as main file")
    print(BASE_PATH)
    print(DIR)

