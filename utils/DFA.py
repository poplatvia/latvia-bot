# M = (Q, sigma, delta, q0, F)
from graphviz import Digraph

class DFA:
    def __init__(self):
        self.Q = set()  # Set of states
        self.sigma = set()  # Alphabet
        self.delta = {}  # Transition function
        self.q0 = None  # Initial state
        self.F = set()  # Set of accepting states

    def set_alphabet(self, alphabet: str):
        self.sigma = set(alphabet)

    def add_state(self, state: int, is_accepting=False):
        self.Q.add(state)
        if is_accepting:
            self.F.add(state)

    def add_transition(self, from_state: int, input_symbol: str, to_state: int):
        if from_state not in self.Q or to_state not in self.Q:
            raise ValueError("States must be added to the DFA before adding transitions.")
        if input_symbol not in self.sigma:
            raise ValueError("Input symbol must be part of the alphabet.")
        self.delta[(from_state, input_symbol)] = to_state

    def set_start_state(self, state: int):
        if state not in self.Q:
            raise ValueError("State must be added to the DFA before setting it as the start state.")
        self.q0 = state

    def accepts(self, input_string: str) -> bool:
        current_state = self.q0
        for symbol in input_string:
            if (current_state, symbol) not in self.delta:
                return False
            current_state = self.delta[(current_state, symbol)]
        return current_state in self.F
    
    def draw(self, title=None, filename="dfa"):
            # Create a directed graph and save to png
            dot = Digraph(format='png', engine='dot')
            dot.attr(rankdir='LR')

            # start arrow
            dot.node('start', label='start', shape='none', width='0', height='0')
            dot.edge('start', str(self.q0))

            # draw all states
            for state in self.Q:
                # make sure final states are double circles
                shape = 'doublecircle' if state in self.F else 'circle'
                html_label = f'<q<sub>{state}</sub>>'
                dot.node(str(state), label=html_label, shape=shape)

            # transitions
            edges = {}
            for (from_state, symbol), to_state in self.delta.items():
                key = (from_state, to_state)
                if key not in edges:
                    edges[key] = []
                edges[key].append(symbol)

            for (src, dst), symbols in edges.items():
                label = ", ".join(sorted(symbols))
                dot.edge(str(src), str(dst), label=label)

            if title:
                dot.attr(label=title, labelloc='t', fontsize='20')

            # Render and save
            dot.render(filename, cleanup=True)
            print(f"DFA saved as {filename}.png")