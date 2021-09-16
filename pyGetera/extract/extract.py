import pandas as pd
from directory import Config


def extract(config: Config,
            execute: bool = True,
            isotope=None,           # що за костыль
            table_view=False,
            format=None,
            columns=None) -> dict | pd.DataFrame:        

    if execute:
        getera_io.execute(config)

    #----====Main-loop====----
    with open(self.getera_path + self.io_files['OUTGET'], 'r') as f:
        fileIter = f.__iter__()
        parser = Parser(fileIter)

        cases = {
            MACRO_STRING: parser.parse_macro(),     # а почему бы просто не запустить их в словаре? 🤔 
            COEFF_STRING: parser.parse_coefs()}     # словарь, с сетдефаултом котрый перебирает регэкспы.
        if isotope:
            cases[ISOTOPE_STRING1] = parser.parse_isotopes(isotope)
            cases[ISOTOPE_STRING2] = parser.parse_isotopes(isotope)
        burn_case = parser.parse_burn()
        burn_case.send(None)

        while True:
            try:
                curr_line = next(fileIter)
                try: 
                    next(cases[curr_line])
                except KeyError:
                    if burn.match(curr_line):
                        burn_case.send(curr_line)
                    else:
                        continue
            except StopIteration:
                break

    if format == 'pandas':
        table = DataPostProcessor.make_dataframe(parser.parsed_data, columns)
        return table
    elif not columns:
        return parser.parsed_data
    else:
        return {i: parser.parsed_data[i] for i in columns}
