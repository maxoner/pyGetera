"""
Author: Панин Максим
GETERA Python API

"""
# import json
import os
import pandas as pd 
import re
from typing import Iterable

#----=====Regular-expressions=====----
rcin_keyword    = re.compile(r'rcin\(\d\)=\d.?\d?')
by_space        = re.compile(r'\s+')
is_parse_method = re.compile(r'parse_.*')

#----=====Raw-keyword-strings=====----
macro_string = '*grp*flux 1/cm2c  * stotal      * sabs        * sfis.       * nu$sfis.    * 1/3*strans  *1/aver.veloci*aver power\n'
coeff_string = '    keff         nu           mu           fi           teta\n' 

#-------------------------------------
class GeteraIO: #Запись перезапись чтение открытие exe 
    """
    Инкапсулирует работу с файлами и программой: чтение, запись, выполнение exe, 
    а также запись в конфиг имени входного и выходного файлов
    """
    def __init__(self,getera_path:str, input_file, output_file):
        self.getera_path = getera_path
        self.io_files = {"INGET": input_file, "OUTGET": output_file}
        self.write_to_config('INGET')
        self.write_to_config('OUTGET') 

    def write_to_config(self,filetype):
        """
        Прописывает в конфиге имя выходного или входного файла
        """
        os.chdir(self.getera_path)
        file_path = self.io_files[filetype]
        with open(self.getera_path+'CONFIG.DRV', 'r+') as f:
            config = f.read()
        get = re.compile(fr'{filetype}\:[A-zА-я.1-9]+').search(config)[0]
        config = config.replace(get , f'{filetype}:'+ file_path)
        with open(self.getera_path+r'CONFIG.DRV', 'w') as f:
            f.write(config)

    def read(self, filetype):
        os.chdir(self.getera_path)
        with open(self.getera_path + self.io_files[filetype],'r') as f:
            parsed_file = f.read()
        return parsed_file

    def write(self, file):
        os.chdir(self.getera_path)
        with open(self.getera_path + self.io_files['INGET'],'w') as f:
            f.write(file)

    def execute(self):
        os.chdir(self.getera_path)
        os.system(r'.\GeteraRun.bat')
      

class StringProcessor:
    """
    Задает методы для поиска и замены в подстроке
    """

    @staticmethod
    def cut_substring(entry:str, parsed_file:str, below=0) -> str:
        start_index = parsed_file.find(entry) + len(entry)
        arr = []
        for _ in range(below+1):
            stop_index = parsed_file[start_index:].find('\n') + start_index
            sliced_string = parsed_file[start_index:stop_index]
            start_index = stop_index
            arr.append(sliced_string)
        return arr if below != 0 else sliced_string

    @staticmethod
    def replace_string(string:str, data:Iterable, separator=',' ) -> str:
        """
        Заменяем значения, разделенные сепаратором, в указанной строке
        """
        row = re.split(fr'{separator}\s*', string)
        #заменяем значения в массиве
        for j in range(len(row) - 1):
            if rcin_keyword.match(row[j]): #проверяем на ключевое слово внутреннего радиуса
                row[j] = data[j]
            row[j] = '%.03e'%data[j]
        return f'{separator} '.join(row)

    @staticmethod
    def replace_all_entries(regexp:str, parsed_file:str, data) -> str:
        entries = re.findall(regexp, parsed_file)[:len(data)]
        k = 0
        for i in entries:
            sliced_string = StringProcessor.cut_substring(i, parsed_file)
            replaced_string = StringProcessor.replace_string(sliced_string, data[k] if type(data[k]) == list else [data[k]])
            #Проблема::нужно вводить данные по порядку, т.к. обращение не по ключу, а по индексу 
            parsed_file = parsed_file.replace(i+sliced_string, i+replaced_string)
            k += 1
        return parsed_file


class Parser:
    def __init__(self, file_iterator):
        self.file_iterator = file_iterator
        self.dict_of_started = {}
        self._start_generators()

    def _start_generators(self):
        for i in dir(Parser):
            if is_parse_method.match(i):
                self.dict_of_started[i] = getattr(Parser, i)(self)

    def parse_coefs(self):
        while True:
            line = next(self.file_iterator)
            raw_cffs = by_space.split(line)[1:-1]
            parsed_coeffs = {
                'keff':float(raw_cffs[0]),
                'nu':float(raw_cffs[1]),
                'mu':float(raw_cffs[2]),
                'fi':float(raw_cffs[3]),
                'teta':float(raw_cffs[4])
            } 
            yield parsed_coeffs

    def parse_macro(self):
        curr_zone = 1
        while True:
            parsed_coeffs = {}
            while True:
                line = next(self.file_iterator)
                raw_cffs = by_space.split(line)[1:-1]
                try:
                    gr_num = int(raw_cffs[0])
                except BaseException:
                    break
                parsed_coeffs.update({
                        f'{curr_zone}::flux{gr_num}'       : float(raw_cffs[1]),
                        f'{curr_zone}::stotal{gr_num}'     : float(raw_cffs[2]),
                        f'{curr_zone}::sabs{gr_num}'       : float(raw_cffs[3]),
                        f'{curr_zone}::sfis{gr_num}'       : float(raw_cffs[4]),
                        f'{curr_zone}::nusfis{gr_num}'     : float(raw_cffs[5]),
                        f'{curr_zone}::1/3*strans{gr_num}' : float(raw_cffs[6]),
                        f'{curr_zone}::1/vel*power{gr_num}': float(raw_cffs[7])
                })

            curr_zone += 1
            yield parsed_coeffs

    # def parse_isotopes(self, file_iterator, coeff_dict):
        # yield 0
class DataPostProcessor:
    @staticmethod
    def make_dataframe(data:dict, columns=None) -> pd.DataFrame:
        """
        создает pandas.DataFrame из словаря
        """
        result = pd.Series(data).to_frame().T
        if columns:
            table = pd.concat((result[i] for i in columns), axis=1)
            return table 
        else:
            return result

    @staticmethod
    def texify(data:dict, ignore_columns=None):
        pass

    # def make_xls(data:dict):
        # pass

class GeteraInterface(GeteraIO):
    """
    Обеспечивает редактирование и ввод в гетеру соответствующих файлов.
    Аргументы при объявлении:

    getera_path : путь до папки с гетерой

    """

    def input(self, data, reg_exp=None):
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

        def gen_regexp(strings:str) -> str:
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
            #tail = '\D{1,4}\(?\d?\D?\d?\)?\*? *[@=] *'
            #tail = ' *[@=] *'
            #reg_exp += tail
            #reg_exp
            return reg_exp
        
        modified_parsed_file = StringProcessor.replace_all_entries(
            reg_exp if reg_exp else gen_regexp(data.keys()),
            self.read('INGET'),
            list(data.values()))
        self.write(modified_parsed_file)

    def output(self, table_view=False, format=None, columns=None):        

        #---====Main-Loop====---
        self.execute()
        with open(self.getera_path + self.io_files['OUTGET'],'r') as f:
            parsed_data = {}  
            fileIter = f.__iter__()
            parser = Parser(fileIter)
            cases = {
                macro_string : parser.dict_of_started['parse_macro'],
                coeff_string : parser.dict_of_started['parse_coefs']
            }
            while True:
                try:
                    curr_line = next(fileIter)
                    try: 
                        parser_response = next(cases[curr_line])
                        parsed_data.update(parser_response)
                    except KeyError:
                        continue
                except StopIteration:
                    break
                
        if format == 'pandas':
            table = DataPostProcessor.make_dataframe(parsed_data, columns)
            return table 
        else:
            return parsed_data

def cli():
    pass


if __name__ == '__main__':
    cli()
