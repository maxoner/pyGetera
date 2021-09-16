import re

# ----=====Regular-expressions=====----
rcin_keyword = re.compile(r'rcin\(\d\)=\d.?\d?')
by_space = re.compile(r'\s+')
burn = re.compile(r'\s*\*\*\* average burn up =\s*\d+\.\d+\s*.*')


# ----=====Raw-keyword-strings=====----
MACRO_STRING = '*grp*flux 1/cm2c  * stotal      * sabs        * sfis.       * nu$sfis.    * 1/3*strans  *1/aver.veloci*aver power\n'
COEFF_STRING = '    keff         nu           mu           fi           teta\n'
ISOTOPE_STRING1 = '    izotop   /             concentration number of izotops=63\n'
ISOTOPE_STRING2 = '    izotop   /             concentration number of izotops=62\n' 