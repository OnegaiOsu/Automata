"""Test regex expressions with automata-lib"""
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA

# Test Expression 1
regex1 = '(aba+bab)(a+b)*(bab)(a+b)*(a+b+ab+ba)(a+b+aa)*'
print('='*60)
print('Expression 1:', regex1)
print('='*60)

try:
    nfa1 = NFA.from_regex(regex1)
    dfa1 = DFA.from_nfa(nfa1).minify()
    print(f'DFA states: {len(dfa1.states)}')
    print(f'Initial: {dfa1.initial_state}')
    print(f'Finals: {dfa1.final_states}')
    print()
    
    # Test various strings - trying to find accepted ones
    test_strings = [
        'abababa',      # aba + '' + bab + '' + a + ''
        'ababbaba',     # aba + '' + bab + '' + ba + ''
        'babbabbab',    # bab + '' + bab + '' + bab (if bab matches a+b+ab+ba? no)
        'babbabba',     # bab + '' + bab + '' + ba + ''
        'abababb',      # aba + '' + bab + '' + b + ''  
        'abababba',     # aba + '' + bab + '' + ba + ''
        'ababababab',   # aba + 'b' + bab + '' + ab + ''
        'abaabababa',   # aba + 'a' + bab + '' + a + 'ba'
        'abababbabab',  # aba + '' + bab + '' + ab + 'ab'
    ]
    
    print('Testing strings:')
    for s in test_strings:
        try:
            result = dfa1.accepts_input(s)
            status = '✓ ACCEPTED' if result else '✗ rejected'
            print(f'  "{s}" -> {status}')
        except Exception as e:
            print(f'  "{s}" -> Error: {e}')
            
except Exception as e:
    print(f'Error building DFA: {e}')
    import traceback
    traceback.print_exc()

print()
print('='*60)

# Test Expression 2  
regex2 = '((101+111+101)+(1+0+11))(1+0+01)*(111+000+101)(1+0)*'
print('Expression 2:', regex2)
print('='*60)

try:
    nfa2 = NFA.from_regex(regex2)
    dfa2 = DFA.from_nfa(nfa2).minify()
    print(f'DFA states: {len(dfa2.states)}')
    print(f'Initial: {dfa2.initial_state}')
    print(f'Finals: {dfa2.final_states}')
    print()
    
    test_strings = [
        '1111',         # 1 + '' + 111 + ''
        '0111',         # 0 + '' + 111 + ''
        '0000',         # 0 + '' + 000 + ''
        '1000',         # 1 + '' + 000 + ''
        '11111',        # 11 + '' + 111 + ''
        '101101',       # 101 + '' + 101 + ''
        '1011010',      # 101 + '' + 101 + '0'
        '111111',       # 111 + '' + 111 + ''
        '1111111',      # 111 + '' + 111 + '1'
        '01111',        # 0 + '' + 111 + '1'
        '00001',        # 0 + '' + 000 + '1'
    ]
    
    print('Testing strings:')
    for s in test_strings:
        try:
            result = dfa2.accepts_input(s)
            status = '✓ ACCEPTED' if result else '✗ rejected'
            print(f'  "{s}" -> {status}')
        except Exception as e:
            print(f'  "{s}" -> Error: {e}')

except Exception as e:
    print(f'Error building DFA: {e}')
    import traceback
    traceback.print_exc()
