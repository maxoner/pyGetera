from typing import Literal, NamedTuple
import os
import re


class Config(NamedTuple):
    GETERA_PATH: str
    INGET: str
    OUTGET: str


def update_config_file(config: Config) -> None:
    """Change input and output filenames in config"""
    for filetype, filename, in (('INGET', config.INGET), ('OUTGET', config.OUTGET)):
        with open(config.GETERA_PATH + 'CONFIG.DRV', 'r') as f:
            config_file = f.read()

        modified_config_file = re.sub(fr'{filetype}\:[A-zА-я.1-9]+', f'{filetype}:'+ filename, config_file)

        with open(config.GETERA_PATH + 'CONFIG.DRV', 'w') as f:
            f.write(modified_config_file)


def execute(config: Config) -> None:
    os.system(config.GETERA_PATH + '/GeteraRun.bat')


def read(config: Config, filetype: Literal['INGET', 'OUTGET']) -> str:
    os.chdir(config.GETERA_PATH)
    with open(config.GETERA_PATH + config._asdict()[filetype], 'r') as f:
        parsed_file = f.read()
    return parsed_file


def write_to_inget(config: Config, file: str) -> None:
    os.chdir(config.GETERA_PATH)
    with open(config.GETERA_PATH + config.INGET,'w') as f:
        f.write(file)

