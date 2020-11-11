"""
Author: Панин Максим
GETERA Python API

"""
import os
import re
import pandas as pd 


class Table(pd.DataFrame):
    def __init__(self,data):
        super().__init__()
    def __iter__(self):
        pass


class GeteraInterface:
    """
    Обеспечивает редактирование и ввод в гетеру соответствующих файлов.
    Аргументы при объявлении:

    getera_path : путь до папки с гетерой

    """
    def __init__(self,getera_path:str):
        self.getera_path = getera_path
        self.io_files = {}

    def _config_writer(self,path,filetype):
        #self.input_file = path
        file_path = self.io_files[filename] = path
        with open(self.getera_path+r'CONFIG.DRV', 'r+') as f:
            config = f.read()
        inget = re.compile(f'{filetype}\:[A-zА-я.1-9]+').search(config)[0]
        config = config.replace(inget , f'{filetype}:'+ file_path)
        with open(self.getera_path+r'CONFIG.DRV', 'w') as f:
            f.write(config)
        
    def set_input_file(self,path):
        self._config_writer(path, 'INGET' )

    def set_output_file(self,path):
        self._config_writer(path, 'OUTGET')


    def input(self, data, strings=None, reg_exp=None):
        """
        Вводит данные во входной txt файл, входые параметры:
            
            strings
                Принимает на вход массив строк, с именами переписываемых параметров. 
                Названия элементов записывать так же как в гетере,но без собак и звездочек,
                например ['t', 'U235','U238','Er']  

            reg_exp
                Принимает на вход r-строку.
                Если вы шарите в регулярных выражениях, можете самостоятельно задать то выражение, 
                по которому функция ищет места, в которых следует переписать значения.
        """

        def write_to_file(regexp:str) -> None:
            """
            Ищет по регулярному выражению все точки вхождения
            и записывает по ним в файл данные из переменной data
            """
            with open(self.getera_path + self.input_file,'r') as f:
                file = f.readlines()
            regex_input = re.compile(regexp)
            k = 0
            for i in regex_input.findall(file):
                line = file.find(i)+len(i)
                j = 0
                prev = ''
                while(file[line+j] != ','):
                    prev += file[line+j]
                    j+=1
                a = '%.03e'%data[k]
                file = file.replace(i+prev,i+a)
                k+=1
            with open(self.getera_path + self.input_file,'w') as f:
                f.write(file)

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
            reg_exp = f' *[@ ] *\*?[{ ll.join(first) }][{ ll.join(second) }]?\d*\*? *[@=] *' 
            if len(second) == 0:
                reg_exp = reg_exp.replace('[]?','')
            #tail = '\D{1,4}\(?\d?\D?\d?\)?\*? *[@=] *'
            #tail = ' *[@=] *'
            #reg_exp += tail
            #reg_exp
            return reg_exp
        
        os.chdir(self.getera_path)
        if reg_exp:
            write_to_file(reg_exp)
        else:
            write_to_file(gen_regexp(strings))


    def output(self):
        """
        Запускает файл getera.exe и вытаскивает нужные параметры из out файла.
        """
            
        #Запускаем гетеру
        os.chdir(self.getera_path) 
        os.system('getera.exe')
        output_dict = '*grp*flux 1/cm2c  * stotal      * sabs        * sfis.       * nu$sfis.    * 1/3*strans  *1/aver.veloci*aver power\n'
        with open(self.getera_path+self.output_file) as f:
            file = f.read()
        line = file.find(output_dict)+len(output_dict)    
        j = 0
        prev = ['','']
        p = 0
        Rho = {}
        while(p < 2):
            prev[p] += file[line+j]
            j+=1
            if(file[line+j] == '\n'):
                p+=1
        for k in [0,1]:
            prev[k] = prev[k].split(' ')
            prev1=[]
            j = 0
            for j in prev[k]:
                if (j == '' or j ==' ' or j=='   ' ):
                    continue
                else:
                    prev1.append(j)
            Rho['Σtot%d'%(k+1)] = float(prev1[2+k])
            Rho['Σabs%d'%(k+1)] = float(prev1[3+k])
            Rho['Σfis%d'%(k+1)] = float(prev1[4+k])
            Rho['νSf%d'%(k+1)] = float(prev1[5+k])
            Rho['D%d'%(k+1)] = prev1[6+k]
        with open(self.getera_path+self.output_file) as f:
            file = f.read()

        xx = re.compile(r'i *1 *\d*.?\d* * *\d*.?\d*')
        Rho['Σ1→2'] = xx.findall(file)[0].split('     ')[2]
        return Rho
        

def main():
    pass


if __name__ == '__main__':
    main()
