"""Trace through the DFA to find valid strings"""
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA

# Expression 1
regex1 = '(aba+bab)(a+b)*(bab)(a+b)*(a+b+ab+ba)(a+b+aa)*'
print('Expression 1:', regex1)
print()

nfa1 = NFA.from_regex(regex1)
dfa1 = DFA.from_nfa(nfa1).minify()

print(f'States: {sorted(dfa1.states)}')
print(f'Initial: {dfa1.initial_state}')
print(f'Finals: {dfa1.final_states}')
print()
print('Transitions:')
for state in sorted(dfa1.states):
    if state in dfa1.transitions:
        for symbol, next_state in dfa1.transitions[state].items():
            marker = '*' if next_state in dfa1.final_states else ' '
            print(f'  {state} --{symbol}--> {next_state} {marker}')
print()

# BFS to find shortest accepted string
from collections import deque

def find_accepted_strings(dfa, max_length=15):
    """Find accepted strings using BFS"""
    queue = deque([(dfa.initial_state, '')])
    visited = {(dfa.initial_state, '')}
    accepted = []
    
    while queue and len(accepted) < 10:
        state, path = queue.popleft()
        
        if len(path) > max_length:
            continue
            
        if state in dfa.final_states and path:
            accepted.append(path)
            print(f'Found: "{path}" (length {len(path)})')
            
        if state in dfa.transitions:
            for symbol in sorted(dfa.transitions[state].keys()):
                next_state = dfa.transitions[state][symbol]
                new_path = path + symbol
                if len(new_path) <= max_length:
                    queue.append((next_state, new_path))
    
    return accepted

print('Searching for accepted strings (Expression 1)...')
accepted1 = find_accepted_strings(dfa1, max_length=20)
print(f'Found {len(accepted1)} accepted strings')
print()

# Expression 2
print('='*60)
regex2 = '((101+111+101)+(1+0+11))(1+0+01)*(111+000+101)(1+0)*'
print('Expression 2:', regex2)
print()

nfa2 = NFA.from_regex(regex2)
dfa2 = DFA.from_nfa(nfa2).minify()

print(f'States: {sorted(dfa2.states)}')
print(f'Initial: {dfa2.initial_state}')
print(f'Finals: {dfa2.final_states}')
print()

print('Searching for accepted strings (Expression 2)...')
accepted2 = find_accepted_strings(dfa2, max_length=30)
print(f'Found {len(accepted2)} accepted strings')
