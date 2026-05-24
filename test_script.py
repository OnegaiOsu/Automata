from core.automata_engine import AutomataEngine;
import re;
e=AutomataEngine();
e.set_expression('Expression 2 (0,1)');
regex = r'^(1|0|11|101|111)(1|0|01)*(111|000|101)(1|0)*$';
tests=['1111','1101','0000','000','111','1010','10101','11000','01101','1001','10010','00100','00101','10100','111111','000111','101','01','0','1','1000','10000','0010','11100','10011','10110','11011','01010','100100','10001','01000','01001','0000000','110011','100101'];
for t in tests:
    dfa = e.validate_string(t)[0]
    ref = bool(re.fullmatch(regex, t))
    flag = 'OK' if dfa == ref else 'MISMATCH'
    print(f'{t:<10} dfa={dfa!s:<5} regex={ref!s:<5} {flag}')
