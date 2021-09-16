from constants import by_space
import re


class Parser:

    def __init__(self, file_iterator):
        self.file_iterator = file_iterator
        self.parsed_data = {
            'keff':[], 'nu':[], 'mu':[],
            'fi':[], 'teta':[], 'aver_burn':[]
            }

    def parse_coefs(self):
        curr_time = 0
        while True:
            line = next(self.file_iterator)
            raw_cffs = by_space.split(line)[1:-1]
            self.parsed_data['keff'].append(float(raw_cffs[0]))
            self.parsed_data['nu'].append(float(raw_cffs[1])), 
            self.parsed_data['mu'].append(float(raw_cffs[2]))
            self.parsed_data['fi'].append(float(raw_cffs[3]))
            self.parsed_data['teta'].append(float(raw_cffs[4]))
            yield 0
            curr_time += 1

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
                        f'{curr_zone}::flux{gr_num}': float(raw_cffs[1]),
                        f'{curr_zone}::stotal{gr_num}': float(raw_cffs[2]),
                        f'{curr_zone}::sabs{gr_num}': float(raw_cffs[3]),
                        f'{curr_zone}::sfis{gr_num}': float(raw_cffs[4]),
                        f'{curr_zone}::nusfis{gr_num}': float(raw_cffs[5]),
                        f'{curr_zone}::1/3*strans{gr_num}': float(raw_cffs[6]),
                        f'{curr_zone}::1/vel*power{gr_num}': float(raw_cffs[7])
                        })
                self.parsed_data.update(parsed_coeffs)
            curr_zone += 1
            yield parsed_coeffs

    def parse_isotopes(self, isotopes):
        curr_time = 0
        for i in isotopes:
            self.parsed_data[f'ρ({i})'] = []
        while True:
            while True:
                line =  next(self.file_iterator)
                if re.match(r'\s*\-\-+\s*', line):
                    break
                try:
                    raw_istps = by_space.split(line)[1:-1]
                    if raw_istps[1] in isotopes:
                        self.parsed_data[f'ρ({raw_istps[1]})'].append(
                                                            float(raw_istps[2]))
                except Exception:
                    break
                else:
                    continue
            yield 0
            curr_time += 1
    
    def parse_burn(self):
        line = yield
        while True:
            line = yield
            self.parsed_data['aver_burn'].append(
                                         float(re.findall(r'\d+.\d+', line)[0])) 


class DataPostProcessor:

    @staticmethod
    def make_dataframe(data:dict, columns=None) -> pd.DataFrame:
        """
        создает pandas.DataFrame из словаря

        """
        if columns:
            res = {i :data[i] for i in columns}
            try:
                result = pd.DataFrame(res)
            except Exception:
                res['keff'].insert(0, 0)
                result = pd.DataFrame(res)
            return result 

    @staticmethod
    def texify(data: dict, ignore_columns=None):
        pass

    @staticmethod
    def make_xls(data: dict):
        pass