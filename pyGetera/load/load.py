__all__ = ['load']

from pyGetera import directory
from pyGetera.load.services import replace_all_entries, gen_regex_from_elems

from typing import Optional
from directory import Config


def load(config: Config,
         data: dict[str, int | float],
         reg_exp: Optional[str] = None
         ) -> None:
    """
    Вводит данные во входной txt файл, входые параметры:
        
        data
            Принимает на вход словарь, где ключи это имена переписываемых параметров. 
            Названия элементов записывать так же как в гетере,но без собак и звездочек,
            например {'t':293.0, 'U235':3*10**(-24),'U238':5*10**(-21),'Er':0}  

        reg_exp
            Принимает на вход r-строку.
            Если вы шарите в регулярных выражениях, можете самостоятельно задать то выражение, 
            по которому функция ищет места, в которых следует переписать значения.


    """
    modified_parsed_file = replace_all_entries(
        regexp = gen_regex_from_elems(data.keys()) if not reg_exp else reg_exp,
        parsed_file = directory.read(config, 'INGET'),
        data = list(data.values())
    )
    directory.write_to_inget(config, modified_parsed_file)

