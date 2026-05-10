"""Test custom DFA implementations"""
from core.automata_engine import AutomataEngine

def test_expression1():
    """Test Expression 1 custom DFA."""
    print("=" * 60)
    print("Testing Expression 1 (a,b) - Custom DFA")
    print("=" * 60)
    
    engine = AutomataEngine()
    engine.set_expression("Expression 1 (a,b)")
    
    data = engine.get_dfa_graph_data()
    print(f"States: {len(data['states'])}")
    print(f"Initial: {data['initial_state']}")
    print(f"Finals: {data['final_states']}")
    print()
    
    # Test strings that should be ACCEPTED
    # Pattern: (aba+bab)(a+b)*(bab)(a+b)*(a+b+ab+ba)(a+b+aa)*
    accept_tests = [
        "abababbabababba",   # aba + bab + bab + ab + (ab)ba = aba + bab + bab + ab + ba
        "abababbaba",        # aba + '' + bab + '' + a + 'ba'
        "babbabbaba",        # bab + '' + bab + '' + ba + ''
        "abababa",           # aba + '' + bab + '' + a + ''
        "babbabba",          # bab + '' + bab + '' + ba + ''
    ]
    
    print("Strings that should be ACCEPTED:")
    for s in accept_tests:
        result = engine.process_string_dfa(s)
        status = '✓ ACCEPTED' if result.accepted else '✗ REJECTED'
        print(f"  '{s}' -> {status}")
    
    # Test strings that should be REJECTED
    reject_tests = [
        "ab",                # Too short
        "aa",                # Doesn't start with aba/bab
        "ababab",            # Missing proper pattern
        "",                  # Empty string
    ]
    
    print("\nStrings that should be REJECTED:")
    for s in reject_tests:
        result = engine.process_string_dfa(s)
        status = '✗ REJECTED' if not result.accepted else '✓ ACCEPTED'
        print(f"  '{s}' -> {status}")

def test_expression2():
    """Test Expression 2 custom DFA."""
    print("\n" + "=" * 60)
    print("Testing Expression 2 (0,1) - Custom DFA")
    print("=" * 60)
    
    engine = AutomataEngine()
    engine.set_expression("Expression 2 (0,1)")
    
    data = engine.get_dfa_graph_data()
    print(f"States: {len(data['states'])}")
    print(f"Initial: {data['initial_state']}")
    print(f"Finals: {data['final_states']}")
    print()
    
    # Pattern: ((101+111+101)+(1+0+11))(1+0+01)*(111+000+101)(1+0)*
    # Simplified: (prefix)(loop)*(pattern)(suffix)*
    # prefix: 101, 111, 1, 0, 11
    # loop: 1, 0, 01 (any combo)
    # pattern: 111, 000, 101
    # suffix: 1, 0 (any combo)
    
    accept_tests = [
        "1111",       # 1 + '' + 111 + ''
        "11110",      # 1 + '' + 111 + '0'
        "0111",       # 0 + '' + 111 + ''
        "01111",      # 0 + '' + 111 + '1'
        "11000",      # 11 + '' + 000 + ''
        "1000",       # 1 + '' + 000 + ''
        "0000",       # 0 + '' + 000 + ''
        "101101",     # 101 + '' + 101 + ''
        "1111111",    # 1 + '1' + 111 + '11'
    ]
    
    print("Testing various strings:")
    for s in accept_tests:
        result = engine.process_string_dfa(s)
        status = '✓ ACCEPTED' if result.accepted else '✗ REJECTED'
        print(f"  '{s}' -> {status}")

if __name__ == "__main__":
    test_expression1()
    test_expression2()
