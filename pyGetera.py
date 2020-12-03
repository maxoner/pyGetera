"""
Author: Панин Максим
GETERA Python API

"""
import json
import os
import pandas as pd 
import re
import sys
from typing import Iterable



# class Table: #предобработка и постобработка таблиц

#     def from_table(self, table, converter reg_exp=None):
#         for i in range(table.shape[0]):
#             getera.input(table.loc[i])


class GeteraIO: #Запись перезапись чтение открытие exe 
    def __init__(self,getera_path:str, input_file, output_file):
        self.getera_path = getera_path
        self.io_files = {"INGET": input_file, "OUTGET": output_file}
        self._config_writer('INGET')
        self._config_writer('OUTGET') 


    def _config_writer(self,filetype):
        """
        Прописывает в конфиге имя выходного или входного файла
        """
        file_path = self.io_files[filetype]
        with open(self.getera_path+'CONFIG.DRV', 'r+') as f:
            config = f.read()
        get = re.compile(fr'{filetype}\:[A-zА-я.1-9]+').search(config)[0]
        config = config.replace(get , f'{filetype}:'+ file_path)
        with open(self.getera_path+r'CONFIG.DRV', 'w') as f:
            f.write(config)

    def read(self, filetype):
        with open(self.getera_path + self.io_files[filetype],'r') as f:
            parsed_file = f.read()
        return parsed_file

    def write(self):
        with open(self.getera_path + self.io_files['INGET'],'r') as f:
            parsed_file = f.write()

    def execute(self):
        os.chdir(self.getera_path)
        os.system('.\GeteraRun.bat')
#-------------------------------------------------------------------------------------------- 
      
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
        def cut_substring(entry:str, parsed_file:str) -> str:
            start_index = parsed_file.find(entry) + len(entry)
            stop_index = parsed_file[start_index:].find('\n') + start_index
            sliced_string = parsed_file[start_index:stop_index]
            return sliced_string

        def replace_string(string:str, data:Iterable, separator=',' ) -> str:
            self.colls = len(data)
            """
            Заменяем значения, разделенные сепаратором, в указанной строке
            """
            row = re.split(fr'{separator}\s*', string)
            #заменяем значения в массиве
            for j in range(len(row) - 1):
                row[j] = '%.03e'%data[j]
            return f'{separator} '.join(row)

        def replace_all_entries(regexp:str, parsed_file:str, data) -> str:
            entries = re.findall(regexp, parsed_file)[:len(data)]
            k = 0
            for i in entries:
                sliced_string = cut_substring(i, parsed_file)
                replaced_string = replace_string(sliced_string, data[k] if type(data[k]) == list else [data[k]])
            #Проблема::нужно вводить данные по порядку, т.к. обращение не по ключу, а по индексу 
                parsed_file = parsed_file.replace(i+sliced_string, i+replaced_string)
                k += 1
            return parsed_file

        def write_to_file(regexp:str, data) -> None:
            """
            Ищет по регулярному выражению все точки вхождения
            и записывает по ним в файл данные из переменной data
            """

            modified_parsed_file = replace_all_entries(regexp, self.read('INGET'), data)
            
            with open(self.getera_path + self.io_files['INGET'],'w') as f:
                f.write(modified_parsed_file)

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
            reg_exp = f' *[@ ] *\*?[{ ll.join(first) }][{ ll.join(second) }]?\d*\*? *[@=] *\s*' 
            if len(second) == 0:
                reg_exp = reg_exp.replace('[]?','')
            #tail = '\D{1,4}\(?\d?\D?\d?\)?\*? *[@=] *'
            #tail = ' *[@=] *'
            #reg_exp += tail
            #reg_exp
            return reg_exp
        
        os.chdir(self.getera_path)
        if reg_exp:
            write_to_file(reg_exp, list(data.values()))
        else:
            write_to_file(gen_regexp(data.keys()), list(data.values()))


    def output(self):
        coefficients = {'keff', 'nu','mu','fi','teta'}
        macroparams = {'stotal', 'sabs', 'sfis','flux','nu$sfis', '1/3strans'}
        output_dict = {}
        #Запускаем гетеру
        self.execute()
        with open(self.getera_path + self.io_files['OUTGET'], 'r') as f:
            parsed_file = f.read()
        def find_entries(type_arg):
            output_dict1 = {}
            if type_arg == 'coeff':
                stringg = '    keff         nu           mu           fi           teta\n'
                line = parsed_file.find(stringg)+len(stringg)    
                j = 0
                prev = ''
                while(parsed_file[line+j] != '\n'):
                    prev += parsed_file[line+j]
                    j+=1
                prev = prev.split(' ')
                prev1=[]
                j = 0
                for j in prev:
                    if (j == '' or j ==' ' or j=='   ' ):
                        continue
                    else:
                        prev1.append(j)
                output_dict1['keff']= float(prev1[0])
                output_dict1['nu'] = float(prev1[1])
                output_dict1['mu'] = float(prev1[2])
                output_dict1['fi'] = float(prev1[3])
                output_dict1['teta'] = float(prev1[4])

            elif type_arg == 'macro':
                stringg = '*grp*flux 1/cm2c  * stotal      * sabs        * sfis.       * nu$sfis.    * 1/3*strans  *1/aver.veloci*aver power\n'
                for entry in (lambda test_str, test_sub:[i for i in range(len(test_str)) if test_str.startswith(test_sub, i)])(parsed_file,stringg):
                    line = entry+len(stringg)    
                    j = 0
                    prev = ['','']
                    p = 0
                    while(p < 2):
                        prev[p] += parsed_file[line+j]
                        j+=1
                        if(parsed_file[line+j] == '\n') #не работает парсинг
                            p+=1
                # for k in range(len((lambda test_str, test_sub:[i for i in range(len(test_str)) if test_str.startswith(test_sub, i)])(parsed_file,stringg))):
                    for k in range(self.colls - 1):
                        prev[k] = prev[k].split(' ')
                        prev1=[]
                        j = 0
                        for j in prev[k]:
                            if (j == '' or j ==' ' or j=='   ' ):
                                continue
                            else:
                                prev1.append(j)
                        output_dict1['Σtot%d'%(k+1)] = float(prev1[2+k]) #  ⎫
                        output_dict1['Σabs%d'%(k+1)] = float(prev1[3+k]) #  ⎪ Заполнение таблицы
                        output_dict1['Σfis%d'%(k+1)] = float(prev1[4+k]) #  ⎬ коэффициентами 
                        output_dict1['νSf%d'%(k+1)] = float(prev1[5+k])  #  ⎪
                        output_dict1['D%d'%(k+1)] = prev1[6+k]           #  ⎭
                return output_dict1
        # xx = re.compile(r'i *1 *\d*.?\d* * *\d*.?\d*')              # ⎫
        # Rho['Σ1→2'] = xx.findall(parsed_file)[0].split('     ')[2]
        output_dict.update(find_entries('coeff'))
        output_dict.update(find_entries('macro'))
        return output_dict
class GeteraUnit:
    def __init__():
        pass

    def find(self) -> dict:
        """
        Ищет все места вхождения
        """
        pass
# 
class InGet(GeteraUnit):
    def replace(self):
        pass

class OutGet(GeteraUnit):
    def parse(self):
        pass

class IsotopeIn(InGet):
    pass

class IsotopesOut(OutGet):
    pass


def cli():
    pass


if __name__ == '__main__':
    cli()