from pathlib import Path
from typing import Dict
from dataclasses import dataclass, field

BASE_PATH = Path(__file__).resolve().parent

@dataclass
class DirDict:
    base: Path = field(init=True, repr=True)


@dataclass
class Local(DirDict):
    sar_image: Path = field(init=False, repr=True)
    chandrayaan2: Path = field(init=False, repr=True)

    def __post_init__(self) -> None:
        self.sar_image = self.base / "sar_image"
        self.chandrayaan2 = self.base / "chandrayaan2"

    def set(self, **kwargs) -> None:
        if "base" in kwargs:
            self.base = kwargs["base"]
            self.__post_init__()

        self.sar_image = kwargs.get('sar_image', self.sar_image)
        self.chandrayaan2 = kwargs.get('chandrayaan2', self.chandrayaan2)


@dataclass
class Data(DirDict):
    chandrayaan2: Path = field(init=False, repr=True)

    def __post_init__(self) -> None:
        self.chandrayaan2 = self.base / "chandrayaan2"


    def set(self, **kwargs) -> None:
        if "base" in kwargs:
            self.base = kwargs["base"]
            self.__post_init__()

        self.chandrayaan2 = kwargs.get('chandrayaan2', self.chandrayaan2)


class Dir(DirDict):
    base:       Path = BASE_PATH
    config:     Path = BASE_PATH / "config.json"
    local:      Local = Local(BASE_PATH / ".local")
    data:       Data = Data(BASE_PATH / "data")

    def __init__(self, dir: Dict) -> None:
        self.config = dir.get('config', self.config)
        if 'local' in dir:
            self.local = Local(dir["local"]['base'])
            self.local.set(**dir['local'])
        if 'data' in dir:
            self.data = Data(dir['data']['base'])
            self.data.set(**dir['data'])



