from core.automata_engine import AutomataEngine

e = AutomataEngine()
e.set_expression('Expression 1 (a,b)')
d = e.get_dfa_graph_data()
print("Initial state:", d['initial_state'])
print("Final states:", d['final_states'])
print("Total states:", len(d['states']))
