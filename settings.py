from pathlib import Path 

BASE_PATH = Path(__file__).resolve().parent.parent

DIR = {
        'CONFIG': BASE_PATH / "code" / "config.json",
        'CODE' : BASE_PATH / "code",
        'DOWNLOADS' : BASE_PATH / "code" / "downloads",
        'DATA': BASE_PATH / "data",
        'CHANDRAYAAN-2': {
            'BASE': BASE_PATH / "isro_data",
            'DATA_FILES': [],
            },
        'MATLAB': {
            # TODO: access data file or code files from the matlab directory
            'BASE_PATH': None,
            'CODE': [],
            'DATA': [],
            }
        }


if __name__ == "__main__":
    # This part of the code is only for debugging
    print("Warning: this file ('settings.py') should be ran as main file")
    print(BASE_PATH)
    print(DIR)

