__all__ = ['gen_regex_from_elems', 'replace_all_entries']


from typing import Iterable
import re

from constants import rcin_keyword


def gen_regex_from_elems(strings: Iterable[str]) -> str:
    """
    Генерирует регулярное выражение из массива 
    строк strings

    """ 
    string = ','.join(strings)
    flag = False
    first = []                                  
    second = []
    for i in string:
        if i == ',':
            flag = False
        elif i.isdigit(): 
            continue
        elif flag:
            second.append(i)
            flag = False
        else:
            first.append(i) 
            flag = True
            ll = ''
            reg_exp = fr' *[@ ] *\*?[{ ll.join(first) }][{ ll.join(second) }]?\d*\*? *[@=] *\s*' 
        if len(second) == 0:
            reg_exp = reg_exp.replace('[]?','')
    return reg_exp


def cut_substring(entry: str, parsed_file: str, below: int = 0) -> str:
    start_index = parsed_file.find(entry) + len(entry)
    stop_index = parsed_file[start_index:].find('\n') + start_index
    sliced_string = parsed_file[start_index:stop_index]
    start_index = stop_index
    return sliced_string


def replace_string(string: str, data: list, separator: str = ',') -> str:
    """Заменяем значения, разделенные сепаратором, в указанной строке"""
    row = re.split(fr'{separator}\s*', string)
    #заменяем значения в массиве
    for j in range(len(row) - 1):
        #проверяем на ключевое слово rcin
        if rcin_keyword.match(row[j]): 
            row[j] = data[j]
        else:
            row[j] = '%.03e'%data[j]
    return f'{separator} '.join(row)


def replace_all_entries(regexp: str, parsed_file: str, data: list) -> str:
    entries = re.findall(regexp, parsed_file)[:len(data)]
    k = 0
    for i in entries:
        sliced_string, *_ = cut_substring(
                            i, parsed_file)
        replaced_string = replace_string(
                            sliced_string,
                            data[k] if type(data[k]) == list else [data[k]])
        #Проблема::нужно вводить данные по порядку, т.к. обращение 
        # не по ключу, а по индексу 
        parsed_file = parsed_file.replace(
                                    i+sliced_string, i+replaced_string)
        k += 1
    return parsed_file