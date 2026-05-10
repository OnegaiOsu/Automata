"""
Automata Engine - Core logic for DFA, CFG, and PDA operations.
Provides custom hand-crafted automata for educational visualization.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import re


class AutomataType(Enum):
    """Types of automata supported."""
    DFA = "DFA"
    CFG = "CFG"
    PDA = "PDA"


@dataclass
class TransitionStep:
    """Represents a single transition step in automata processing."""
    from_state: str
    symbol: str
    to_state: str
    step_number: int
    stack_before: list[str] = field(default_factory=list)  # For PDA
    stack_after: list[str] = field(default_factory=list)   # For PDA
    pda_action: str = ""  # Description of PDA action


@dataclass
class ProcessingResult:
    """Result of processing a string through an automaton."""
    accepted: bool
    steps: list[TransitionStep]
    final_state: str
    error_message: Optional[str] = None


@dataclass
class CFGRule:
    """Represents a Context-Free Grammar production rule."""
    left: str
    right: list[str]
    
    def __str__(self) -> str:
        return f"{self.left} → {' | '.join(self.right)}"


@dataclass 
class PDAState:
    """Represents a PDA state with type information."""
    name: str
    state_type: str  # 'start', 'read', 'reject', 'accept', 'decision'
    description: str = ""


@dataclass
class PDATransition:
    """Represents a PDA transition."""
    from_state: str
    to_state: str
    input_symbol: str  # 'a', 'b', 'ε', etc.
    stack_pop: str = ""
    stack_push: str = ""


class CustomDFA:
    """Custom DFA with explicit states and transitions."""
    def __init__(self, states: set, alphabet: set, transitions: dict, 
                 initial_state: str, final_states: set):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states
    
    def accepts_input(self, input_string: str) -> bool:
        """Check if the DFA accepts the input string."""
        current = self.initial_state
        for symbol in input_string:
            if symbol not in self.alphabet:
                return False
            if current not in self.transitions:
                return False
            if symbol not in self.transitions[current]:
                return False
            current = self.transitions[current][symbol]
        return current in self.final_states


class AutomataEngine:
    """
    Engine for creating and simulating automata from regular expressions.
    Provides DFA, CFG, and PDA representations with step-by-step processing.
    Uses custom hand-crafted automata for better educational visualization.
    """
    
    # Predefined regex expressions
    EXPRESSIONS = {
        "Expression 1 (a,b)": "(aba+bab)(a+b)*(bab)(a+b)*(a+b+ab+ba)(a+b+aa)*",
        "Expression 2 (0,1)": "((101+111+101)+(1+0+11))(1+0+01)*(111+000+101)(1+0)*"
    }
    
    MAX_STATES_WARNING = 50
    
    def __init__(self):
        self._current_expression_key: Optional[str] = None
        self._dfa: Optional[CustomDFA] = None
        self._cfg_rules: list[CFGRule] = []
        self._pda_states: list[PDAState] = []
        self._pda_transitions: list[PDATransition] = []
        self._alphabet: set[str] = set()
        self._states_warning: bool = False
        self._state_count: int = 0
        
    @property
    def current_expression(self) -> Optional[str]:
        """Get the current regex expression string."""
        if self._current_expression_key:
            return self.EXPRESSIONS.get(self._current_expression_key)
        return None
    
    @property
    def current_expression_name(self) -> Optional[str]:
        """Get the name of the current expression."""
        return self._current_expression_key
    
    @property
    def states_warning(self) -> bool:
        """Returns True if DFA has more than MAX_STATES_WARNING states."""
        return self._states_warning
    
    @property
    def state_count(self) -> int:
        """Returns the number of states in the current DFA."""
        return self._state_count
    
    @property
    def alphabet(self) -> set[str]:
        """Returns the alphabet of the current automaton."""
        return self._alphabet
    
    def get_expression_names(self) -> list[str]:
        """Get list of available expression names."""
        return list(self.EXPRESSIONS.keys())
    
    def set_expression(self, expression_name: str) -> bool:
        """
        Set the current expression and build all automata representations.
        Returns True if successful, False otherwise.
        """
        if expression_name not in self.EXPRESSIONS:
            return False
        
        self._current_expression_key = expression_name
        
        # Determine alphabet from expression
        if "Expression 1" in expression_name:
            self._alphabet = {'a', 'b'}
            self._build_expression1_automata()
        else:
            self._alphabet = {'0', '1'}
            self._build_expression2_automata()
        
        return True
    
    def _build_expression1_automata(self):
        """Build custom DFA, CFG, and PDA for Expression 1: (aba+bab)(a+b)*(bab)(a+b)*(a+b+ab+ba)(a+b+aa)*"""
        self._build_expression1_dfa()
        self._build_expression1_cfg()
        self._build_expression1_pda()
    
    def _build_expression1_dfa(self):
        """
        Build the custom DFA matching the user's diagram for Expression 1.
        States match the user's diagram: - (initial), q1, q3, q1', q4, T, q5, q6, q7, q8, + (final)
        """
        states = {'-', 'q1', 'q3', 'q1\'', 'q4', 'T', 'q5', 'q6', 'q7', 'q8', '+'}
        alphabet = {'a', 'b'}
        initial_state = '-'
        final_states = {'+'}
        
        # Transitions matching the user's DFA diagram exactly
        # Expression: (aba+bab)(a+b)*(bab)(a+b)*(a+b+ab+ba)(a+b+aa)*
        transitions = {
            # Initial branching for (aba+bab)
            '-': {'a': 'q1', 'b': 'q1\''},   # Start: a->q1 (aba path), b->q1' (bab path)
            
            # aba path: q1 --b--> q3 --a--> T
            'q1': {'b': 'q3', 'a': 'q1'},    # Need 'b' for aba, self-loop on 'a'
            'q3': {'a': 'T', 'b': 'q3'},     # Need 'a' to complete aba -> T
            
            # bab path: q1' --a--> q4 --b--> T
            'q1\'': {'a': 'q4', 'b': 'q1\''}, # Need 'a' for bab
            'q4': {'b': 'T', 'a': 'q4'},     # Need 'b' to complete bab -> T
            
            # T state: (a+b)* self-loop, then 'a' starts looking for 'bab'
            'T': {'a': 'q5', 'b': 'T'},      # Self-loop on 'b', 'a' starts bab detection
            
            # Looking for 'bab' pattern after first (a+b)*
            'q5': {'b': 'q6', 'a': 'q5'},    # Got 'a', need 'b'
            'q6': {'a': 'q7', 'b': 'q6'},    # Got 'ab', need 'a' (with b self-loop)
            'q7': {'b': 'q8', 'a': 'q5'},    # Got 'aba', need 'b' for second 'bab'
            
            # After bab, checking (a+b+ab+ba) and going to final
            'q8': {'a': '+', 'b': '+'},      # Any of a,b leads to final
            
            # Final state with (a+b+aa)* - self-loops for acceptance
            '+': {'a': '+', 'b': '+'},       # Accept and stay (a+b+aa)*
        }
        
        self._dfa = CustomDFA(states, alphabet, transitions, initial_state, final_states)
        self._state_count = len(states)
        self._states_warning = False
    
    def _build_expression1_cfg(self):
        """
        Build the CFG matching the user's diagram for Expression 1.
        S → A B C B D E
        A → aba | bab
        B → aB | bB | ε
        C → bab
        D → a | b | ab | ba
        E → aE | bE | aaE | ε
        """
        self._cfg_rules = [
            CFGRule('S', ['ABCBDE']),
            CFGRule('A', ['aba', 'bab']),
            CFGRule('B', ['aB', 'bB', 'ε']),
            CFGRule('C', ['bab']),
            CFGRule('D', ['a', 'b', 'ab', 'ba']),
            CFGRule('E', ['aE', 'bE', 'aaE', 'ε']),
        ]
    
    def _build_expression1_pda(self):
        """
        Build the PDA matching the user's flowchart diagram for Expression 1.
        Uses a flowchart-style representation with decision nodes.
        """
        # PDA States (flowchart style)
        self._pda_states = [
            PDAState('Start', 'start', 'Initial state'),
            PDAState('Read1', 'decision', 'Read first symbol'),
            PDAState('ReadA1', 'read', 'Path for aba'),
            PDAState('ReadB1', 'read', 'Path for bab'),
            PDAState('Reject', 'reject', 'Invalid input'),
            PDAState('ReadA2', 'read', 'Continue aba'),
            PDAState('ReadB2', 'read', 'Continue bab'),
            PDAState('Loop1', 'decision', 'First (a+b)* loop'),
            PDAState('Read2', 'read', 'Start bab search'),
            PDAState('Read3', 'read', 'Middle of bab'),
            PDAState('Read4', 'read', 'End of bab'),
            PDAState('Loop2', 'decision', 'Second (a+b)* loop'),
            PDAState('Read5', 'read', 'Check (a+b+ab+ba)'),
            PDAState('Read6', 'read', 'Final pattern'),
            PDAState('Loop3', 'decision', 'Final (a+b+aa)* loop'),
            PDAState('Accept', 'accept', 'String accepted'),
        ]
        
        # PDA Transitions
        self._pda_transitions = [
            PDATransition('Start', 'Read1', 'ε', 'ε', 'Z'),
            PDATransition('Read1', 'ReadA1', 'a', 'ε', 'ε'),
            PDATransition('Read1', 'ReadB1', 'b', 'ε', 'ε'),
            PDATransition('ReadA1', 'Reject', 'a', 'ε', 'ε'),
            PDATransition('ReadA1', 'ReadA2', 'b', 'ε', 'ε'),
            PDATransition('ReadB1', 'ReadB2', 'a', 'ε', 'ε'),
            PDATransition('ReadB1', 'Reject', 'b', 'ε', 'ε'),
            PDATransition('ReadA2', 'Loop1', 'a', 'ε', 'ε'),
            PDATransition('ReadB2', 'Loop1', 'b', 'ε', 'ε'),
            PDATransition('Loop1', 'Loop1', 'a,b', 'ε', 'ε'),
            PDATransition('Loop1', 'Read2', 'ε', 'ε', 'ε'),
            PDATransition('Read2', 'Read3', 'b', 'ε', 'ε'),
            PDATransition('Read3', 'Read4', 'a', 'ε', 'ε'),
            PDATransition('Read4', 'Loop2', 'b', 'ε', 'ε'),
            PDATransition('Loop2', 'Loop2', 'a,b', 'ε', 'ε'),
            PDATransition('Loop2', 'Read5', 'ε', 'ε', 'ε'),
            PDATransition('Read5', 'Read6', 'a,b', 'ε', 'ε'),
            PDATransition('Read6', 'Loop3', 'a,b', 'ε', 'ε'),
            PDATransition('Loop3', 'Loop3', 'a,b', 'ε', 'ε'),
            PDATransition('Loop3', 'Accept', 'ε', 'Z', 'ε'),
        ]
    
    def _build_expression2_automata(self):
        """Build custom DFA, CFG, and PDA for Expression 2."""
        self._build_expression2_dfa()
        self._build_expression2_cfg()
        self._build_expression2_pda()
    
    def _build_expression2_dfa(self):
        """
        Build the custom DFA matching the user's diagram for Expression 2.
        Expression: ((101+111+101) + (1+0+11)) (1+0+01)* (111+000+101) (1+0)*
        States: - (initial), q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, + (final)
        """
        states = {'-', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10', '+'}
        alphabet = {'0', '1'}
        initial_state = '-'
        final_states = {'+'}
        
        # Transitions matching the user's DFA diagram exactly
        # Expression: ((101+111+101)+(1+0+11))(1+0+01)*(111+000+101)(1+0)*
        transitions = {
            # Initial state: branches on 0 or 1
            '-': {'1': 'q1', '0': 'q3'},
            
            # q1: from initial on '1', leads to q2 on '1' or q3 on '0'
            'q1': {'1': 'q2', '0': 'q3'},
            
            # q2: continues '11' path, goes to q4 on '1'
            'q2': {'1': 'q4', '0': 'q6'},
            
            # q3: from '0' path, goes to q5 on '1', self-loop or back on '0'
            'q3': {'1': 'q5', '0': 'q3'},
            
            # q4: part of middle section, connects to q6 on '0', to + on '1'
            'q4': {'0': 'q6', '1': '+'},
            
            # q5: continues pattern, goes to q7 on '1'
            'q5': {'1': 'q7', '0': 'q5'},
            
            # q6: connects to q8 on '0', q7 on '1'  
            'q6': {'0': 'q8', '1': 'q7'},
            
            # q7: key state for (111+000+101) detection
            'q7': {'0': 'q7', '1': 'q9'},
            
            # q8: part of '000' detection path
            'q8': {'0': 'q10', '1': 'q7'},
            
            # q9: part of '111' detection, goes to + on '1'
            'q9': {'1': '+', '0': 'q7'},
            
            # q10: end of '000', goes to + on '0'
            'q10': {'0': '+', '1': 'q9'},
            
            # Final state: (1+0)* self-loop
            '+': {'0': '+', '1': '+'},
        }
        
        self._dfa = CustomDFA(states, alphabet, transitions, initial_state, final_states)
        self._state_count = len(states)
        self._states_warning = False
    
    def _build_expression2_cfg(self):
        """
        Build the CFG for Expression 2 matching the user's diagram exactly.
        Expression: ((101+111+101)+(1+0+11))(1+0+01)*(111+000+101)(1+0)*
        
        S → A B C D
        A → 101 | 111 | 101 | 1 | 0 | 11
        B → 1B | 0B | 01B | ε
        C → 111 | 000 | 101
        D → 0D | 1D | ε
        """
        self._cfg_rules = [
            CFGRule('S', ['ABCD']),
            CFGRule('A', ['101', '111', '101', '1', '0', '11']),
            CFGRule('B', ['1B', '0B', '01B', 'ε']),
            CFGRule('C', ['111', '000', '101']),
            CFGRule('D', ['0D', '1D', 'ε']),
        ]
    
    def _build_expression2_pda(self):
        """Build PDA for Expression 2 matching the user's flowchart diagram."""
        self._pda_states = [
            PDAState('Start', 'start', 'Initial state'),
            PDAState('Read1', 'decision', 'First read - branch on 0/1'),
            PDAState('Reject', 'reject', 'Invalid path'),
            PDAState('ReadL1', 'decision', 'Left branch (1 path)'),
            PDAState('ReadL2', 'read', 'Continue 1 path'),
            PDAState('ReadL3', 'read', 'Continue 1 path'),
            PDAState('ReadR1', 'decision', 'Right branch (0 path)'),
            PDAState('ReadM1', 'decision', 'Middle section'),
            PDAState('ReadM2', 'read', 'Middle reads'),
            PDAState('ReadM3', 'read', 'Middle reads'),
            PDAState('ReadM4', 'read', 'Middle reads'),
            PDAState('ReadF1', 'decision', 'Final pattern check'),
            PDAState('Accept', 'accept', 'String accepted'),
        ]
        
        self._pda_transitions = [
            PDATransition('Start', 'Read1', 'ε', 'ε', 'Z'),
            PDATransition('Read1', 'ReadL1', '1', 'ε', 'ε'),
            PDATransition('Read1', 'ReadR1', '0', 'ε', 'ε'),
            PDATransition('Read1', 'Reject', 'ε', 'ε', 'ε'),
            PDATransition('ReadL1', 'ReadL2', '1', 'ε', 'ε'),
            PDATransition('ReadL1', 'ReadR1', '0', 'ε', 'ε'),
            PDATransition('ReadL2', 'ReadM1', '1', 'ε', 'ε'),
            PDATransition('ReadR1', 'ReadM1', '1', 'ε', 'ε'),
            PDATransition('ReadR1', 'ReadR1', '0', 'ε', 'ε'),
            PDATransition('ReadM1', 'ReadM2', '0,1', 'ε', 'ε'),
            PDATransition('ReadM2', 'ReadM3', '0,1', 'ε', 'ε'),
            PDATransition('ReadM3', 'ReadF1', '0,1', 'ε', 'ε'),
            PDATransition('ReadF1', 'ReadF1', '0,1', 'ε', 'ε'),
            PDATransition('ReadF1', 'Accept', 'ε', 'Z', 'ε'),
        ]

    def _regex_to_cfg(self, regex: str) -> list[CFGRule]:
        """Convert regex to CFG production rules."""
        rules = []
        var_counter = [0]  # Use list for mutable counter in nested function
        
        def get_new_var():
            var_counter[0] += 1
            return f"A{var_counter[0]}"
        
        def parse_regex(expr: str, var: str) -> list[CFGRule]:
            """Recursively parse regex and generate CFG rules."""
            local_rules = []
            expr = expr.strip()
            
            if not expr:
                local_rules.append(CFGRule(var, ["ε"]))
                return local_rules
            
            # Handle alternation (lowest precedence)
            # Find + at the top level (not inside parentheses)
            depth = 0
            alternatives = []
            current = ""
            
            for char in expr:
                if char == '(':
                    depth += 1
                    current += char
                elif char == ')':
                    depth -= 1
                    current += char
                elif char == '+' and depth == 0:
                    if current:
                        alternatives.append(current)
                    current = ""
                else:
                    current += char
            
            if current:
                alternatives.append(current)
            
            if len(alternatives) > 1:
                # Multiple alternatives
                right_sides = []
                for alt in alternatives:
                    if len(alt) == 1 and alt.isalpha():
                        right_sides.append(alt)
                    elif alt == "ε":
                        right_sides.append("ε")
                    else:
                        new_var = get_new_var()
                        right_sides.append(new_var)
                        local_rules.extend(parse_regex(alt, new_var))
                local_rules.append(CFGRule(var, right_sides))
                return local_rules
            
            # Handle concatenation
            # Parse into segments (handling parentheses and Kleene star)
            segments = []
            i = 0
            while i < len(expr):
                if expr[i] == '(':
                    # Find matching closing parenthesis
                    depth = 1
                    j = i + 1
                    while j < len(expr) and depth > 0:
                        if expr[j] == '(':
                            depth += 1
                        elif expr[j] == ')':
                            depth -= 1
                        j += 1
                    
                    inner = expr[i+1:j-1]
                    
                    # Check for Kleene star
                    if j < len(expr) and expr[j] == '*':
                        segments.append(('star', inner))
                        i = j + 1
                    else:
                        segments.append(('group', inner))
                        i = j
                elif expr[i].isalnum():
                    # Single symbol
                    if i + 1 < len(expr) and expr[i + 1] == '*':
                        segments.append(('star', expr[i]))
                        i += 2
                    else:
                        segments.append(('symbol', expr[i]))
                        i += 1
                else:
                    i += 1
            
            if len(segments) == 0:
                local_rules.append(CFGRule(var, ["ε"]))
            elif len(segments) == 1:
                seg_type, seg_content = segments[0]
                if seg_type == 'symbol':
                    local_rules.append(CFGRule(var, [seg_content]))
                elif seg_type == 'star':
                    # A -> BA | ε, where B generates seg_content
                    new_var = get_new_var()
                    local_rules.extend(parse_regex(seg_content, new_var))
                    local_rules.append(CFGRule(var, [f"{new_var}{var}", "ε"]))
                elif seg_type == 'group':
                    local_rules.extend(parse_regex(seg_content, var))
            else:
                # Concatenation of multiple segments
                concat_parts = []
                for seg_type, seg_content in segments:
                    if seg_type == 'symbol':
                        concat_parts.append(seg_content)
                    else:
                        new_var = get_new_var()
                        concat_parts.append(new_var)
                        if seg_type == 'star':
                            inner_var = get_new_var()
                            local_rules.extend(parse_regex(seg_content, inner_var))
                            local_rules.append(CFGRule(new_var, [f"{inner_var}{new_var}", "ε"]))
                        else:
                            local_rules.extend(parse_regex(seg_content, new_var))
                
                local_rules.append(CFGRule(var, ["".join(concat_parts)]))
            
            return local_rules
        
        rules = parse_regex(regex, "S")
        return rules
    
    def get_dfa_graph_data(self) -> Optional[dict]:
        """
        Get DFA data for visualization.
        Returns dict with states, transitions, initial_state, final_states.
        """
        if self._dfa is None:
            return None
        
        return {
            'states': list(self._dfa.states),
            'transitions': dict(self._dfa.transitions),
            'initial_state': self._dfa.initial_state,
            'final_states': list(self._dfa.final_states),
            'alphabet': list(self._alphabet)
        }
    
    def get_dfa_dot(self) -> Optional[str]:
        """Get DOT representation of the DFA for Graphviz rendering."""
        if self._dfa is None:
            return None
        
        try:
            # Generate DOT manually for better control
            lines = ['digraph DFA {', '    rankdir=LR;', '    node [shape=circle];']
            
            # Mark final states with double circle
            for state in self._dfa.final_states:
                lines.append(f'    "{state}" [shape=doublecircle];')
            
            # Add invisible start node
            lines.append('    "" [shape=none];')
            lines.append(f'    "" -> "{self._dfa.initial_state}";')
            
            # Add transitions
            for from_state, transitions in self._dfa.transitions.items():
                # Group transitions by target state
                target_symbols = {}
                for symbol, to_state in transitions.items():
                    if to_state not in target_symbols:
                        target_symbols[to_state] = []
                    target_symbols[to_state].append(symbol)
                
                for to_state, symbols in target_symbols.items():
                    label = ','.join(sorted(symbols))
                    lines.append(f'    "{from_state}" -> "{to_state}" [label="{label}"];')
            
            lines.append('}')
            return '\n'.join(lines)
        except Exception as e:
            print(f"Error generating DOT: {e}")
            return None
    
    def process_string_dfa(self, input_string: str) -> ProcessingResult:
        """
        Process a string through the DFA and return step-by-step results.
        """
        if self._dfa is None:
            return ProcessingResult(
                accepted=False,
                steps=[],
                final_state="",
                error_message="DFA not initialized"
            )
        
        # Validate input string
        for char in input_string:
            if char not in self._alphabet:
                return ProcessingResult(
                    accepted=False,
                    steps=[],
                    final_state="",
                    error_message=f"Invalid symbol '{char}'. Expected symbols from {self._alphabet}"
                )
        
        steps = []
        current_state = self._dfa.initial_state
        
        for i, symbol in enumerate(input_string):
            if current_state not in self._dfa.transitions:
                return ProcessingResult(
                    accepted=False,
                    steps=steps,
                    final_state=current_state,
                    error_message=f"No transitions from state {current_state}"
                )
            
            if symbol not in self._dfa.transitions[current_state]:
                return ProcessingResult(
                    accepted=False,
                    steps=steps,
                    final_state=current_state,
                    error_message=f"No transition for symbol '{symbol}' from state {current_state}"
                )
            
            next_state = self._dfa.transitions[current_state][symbol]
            steps.append(TransitionStep(
                from_state=current_state,
                symbol=symbol,
                to_state=next_state,
                step_number=i + 1
            ))
            current_state = next_state
        
        accepted = current_state in self._dfa.final_states
        return ProcessingResult(
            accepted=accepted,
            steps=steps,
            final_state=current_state
        )
    
    def process_string_pda(self, input_string: str) -> ProcessingResult:
        """
        Process a string through the PDA with stack operations.
        Uses DFA for actual acceptance, generates PDA-style step descriptions.
        """
        if self._dfa is None:
            return ProcessingResult(
                accepted=False,
                steps=[],
                final_state="",
                error_message="PDA not initialized"
            )
        
        # Validate input string
        for char in input_string:
            if char not in self._alphabet:
                return ProcessingResult(
                    accepted=False,
                    steps=[],
                    final_state="",
                    error_message=f"Invalid symbol '{char}'. Expected symbols from {self._alphabet}"
                )
        
        steps = []
        current_state = self._dfa.initial_state
        stack = ['Z']  # Initial stack symbol
        
        for i, symbol in enumerate(input_string):
            if current_state not in self._dfa.transitions:
                return ProcessingResult(
                    accepted=False,
                    steps=steps,
                    final_state=current_state,
                    error_message=f"No transitions from state {current_state}"
                )
            
            if symbol not in self._dfa.transitions[current_state]:
                return ProcessingResult(
                    accepted=False,
                    steps=steps,
                    final_state=current_state,
                    error_message=f"No transition for symbol '{symbol}' from state {current_state}"
                )
            
            next_state = self._dfa.transitions[current_state][symbol]
            stack_before = stack.copy()
            
            # Generate meaningful stack operations for educational purposes
            # Push symbol marker when entering key states, pop when leaving
            stack_action = ""
            if i == 0:
                # First symbol - push marker
                stack.append(symbol.upper())
                stack_action = f"Push {symbol.upper()}"
            elif next_state in self._dfa.final_states:
                # Approaching final state - pop to accept
                if len(stack) > 1:
                    popped = stack.pop()
                    stack_action = f"Pop {popped}"
            else:
                # Regular transition - optionally track progress
                if len(stack) < 5:  # Limit stack depth
                    stack.append(symbol.upper())
                    stack_action = f"Push {symbol.upper()}"
            
            steps.append(TransitionStep(
                from_state=current_state,
                symbol=symbol,
                to_state=next_state,
                step_number=i + 1,
                stack_before=stack_before,
                stack_after=stack.copy(),
                pda_action=stack_action
            ))
            current_state = next_state
        
        accepted = current_state in self._dfa.final_states
        return ProcessingResult(
            accepted=accepted,
            steps=steps,
            final_state=current_state
        )
    
    def get_cfg_rules(self) -> list[CFGRule]:
        """Get the CFG production rules."""
        return self._cfg_rules
    
    def get_cfg_text(self) -> str:
        """Get formatted CFG rules as text in clean educational format."""
        if not self._cfg_rules:
            return "No CFG rules generated."
        
        # Group rules by left-hand side
        grouped = {}
        for rule in self._cfg_rules:
            if rule.left not in grouped:
                grouped[rule.left] = []
            for r in rule.right:
                if r not in grouped[rule.left]:
                    grouped[rule.left].append(r)
        
        lines = ["Context-Free Grammar:", "=" * 40, ""]
        
        # Display in the order: S first, then A, B, C, D, E...
        # Start symbol first
        if 'S' in grouped:
            # Format the S rule with spaces between variables for readability
            s_right = grouped['S'][0] if grouped['S'] else ''
            # Add spaces between capital letters for better readability
            formatted = ' '.join(list(s_right)) if s_right.isupper() or (len(s_right) > 1 and all(c.isupper() for c in s_right)) else s_right
            lines.append(f"S → {formatted}")
            lines.append("")
            del grouped['S']
        
        # Other rules in alphabetical order
        for left in sorted(grouped.keys()):
            right_parts = grouped[left]
            lines.append(f"{left} → {' | '.join(right_parts)}")
        
        lines.extend(["", "=" * 40])
        lines.append(f"Start Symbol: S")
        lines.append(f"Terminals: {{{', '.join(sorted(self._alphabet))}}}")
        
        return '\n'.join(lines)
    
    def get_pda_states(self) -> list:
        """Get PDA states for visualization."""
        return self._pda_states
    
    def get_pda_transitions(self) -> list:
        """Get PDA transitions for visualization."""
        return self._pda_transitions
    
    def validate_string(self, input_string: str) -> tuple[bool, str]:
        """
        Quick validation of string against current automaton.
        Returns (is_valid, message).
        """
        if self._dfa is None:
            return False, "No automaton loaded"
        
        for char in input_string:
            if char not in self._alphabet:
                return False, f"Invalid symbol '{char}'"
        
        try:
            accepted = self._dfa.accepts_input(input_string)
            if accepted:
                return True, "String accepted by the automaton"
            else:
                return False, "String rejected by the automaton"
        except Exception as e:
            return False, f"Error: {str(e)}"
