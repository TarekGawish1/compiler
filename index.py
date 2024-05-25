from tabulate import tabulate

def tokenize(input_code):
    tokens = []
    symbol_table = {}
    current_char = ''
    i = 0
    line_number = 1 

    while i < len(input_code):
        current_char = input_code[i]


        if current_char.isspace():
            if current_char == '\n':
                line_number += 1 
            i += 1
            continue


        if current_char.isalpha(): 
            start = i
            while i < len(input_code) and (input_code[i].isalnum() or input_code[i] == '_'):
                i += 1
            lexeme = input_code[start:i]
            if lexeme in ['if', 'else', 'while', 'int', 'float', 'void']:
                tokens.append(('KEYWORD', lexeme))
            else:
                tokens.append(('IDENTIFIER', lexeme))

                if lexeme not in symbol_table:
                    symbol_table[lexeme] = {
                        'type': None,
                        'dimension': None,
                        'line_declaration': line_number,
                        'line_reference': [line_number] 
                    }
                else:
                    
                    symbol_table[lexeme]['line_reference'].append(line_number)
            continue


        if current_char.isdigit() or (current_char == '.' and i + 1 < len(input_code) and input_code[i + 1].isdigit()):
            start = i
            is_float = False
            while i < len(input_code) and (input_code[i].isdigit() or input_code[i] == '.'):
                if input_code[i] == '.':
                    is_float = True
                i += 1
            lexeme = input_code[start:i]
            if is_float:
                tokens.append(('FLOAT_CONSTANT', lexeme))
            else:
                tokens.append(('INT_CONSTANT', lexeme))
            continue


        if current_char in '+-*/=<>!':
            tokens.append(('OPERATOR', current_char))
            i += 1
            continue
        elif current_char in '(){};':
            tokens.append(('PUNCTUATION', current_char))
            i += 1
            continue


        raise ValueError(f"Invalid character: {current_char}")


    for idx, (token_type, lexeme) in enumerate(tokens):
        if token_type == 'KEYWORD' and lexeme in ['int', 'float', 'void']:
            if tokens[idx + 1][0] == 'IDENTIFIER':
                variable_name = tokens[idx + 1][1]
                if variable_name in symbol_table:
                    symbol_table[variable_name]['type'] = lexeme

    return tokens, symbol_table

def create_ordered_symbol_table(symbol_table):
    ordered_symbol_table = sorted(symbol_table.items(), key=lambda item: item[0])
    return ordered_symbol_table


file_name = 'example.txt'
try:
    with open(file_name, 'r') as file:
        input_code = file.read()
except FileNotFoundError:
    print(f"Error: File '{file_name}' not found.")
    exit()


print("Input Code:")
print(input_code)


result_tokens, result_symbol_table = tokenize(input_code)


print("\nTokenized Result:")
table_data = [(token_type, lexeme) for token_type, lexeme in result_tokens]
print(tabulate(table_data, headers=['Token Type', 'Lexeme'], tablefmt='grid'))


print("\nUnordared Symbol Table:")
table_data = []
counter = 1
for variable_name, info in result_symbol_table.items():
    table_data.append((counter, variable_name, info['type'], info['dimension'], info['line_declaration'], info['line_reference']))
    counter += 1
print(tabulate(table_data, headers=['Counter', 'Variable Name', 'Type', 'Dimension', 'Line Declaration', 'Line Reference'], tablefmt='grid'))

ordered_symbol_table = create_ordered_symbol_table(result_symbol_table)
print("\nOrdered Symbol Table: ")
table_data = [(idx + 1, item[0], item[1]['type'], item[1]['dimension'], item[1]['line_declaration'], item[1]['line_reference']) for idx, item in enumerate(ordered_symbol_table)]
print(tabulate(table_data, headers=['Counter', 'Variable Name', 'Type', 'Dimension', 'Line Declaration', 'Line Reference'], tablefmt='grid'))


# E -> E + T | E - T | T
# T -> T * F | T / F | F
    # F -> (E) | id | num+||?

class LLParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.index = 0
        self.parse_tree = {'type': 'E', 'children': []}

    def match(self, expected_token_type):
        if self.current_token and self.current_token[0] == expected_token_type:
            node = {'type': self.current_token[0], 'value': self.current_token[1], 'children': []}
            self.current_node['children'].append(node)
            self.index += 1
            self.current_token = self.tokens[self.index] if self.index < len(self.tokens) else None
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token}")

    def parse(self):
        self.current_token = self.tokens[self.index] if self.tokens else None
        self.current_node = self.parse_tree
        self.E()
        if self.current_token is not None:
            raise SyntaxError("Unexpected token after parsing")

    def E(self):
        self.T()
        self.E_prime()

    def E_prime(self):
        if self.current_token and self.current_token[1] in ['+', '-']:
            self.match(self.current_token[0])
            self.T()
            self.E_prime()

    def T(self):
        self.F()
        self.T_prime()

    def T_prime(self):
        if self.current_token and self.current_token[1] in ['*', '/']:
            self.match(self.current_token[0])
            self.F()
            self.T_prime()

    def F(self):
        if self.current_token and self.current_token[0] == 'INT_CONSTANT':
            self.match('INT_CONSTANT')
        elif self.current_token and self.current_token[0] == 'FLOAT_CONSTANT':
            self.match('FLOAT_CONSTANT')
        elif self.current_token and self.current_token[0] == 'IDENTIFIER':
            self.match('IDENTIFIER')
        elif self.current_token and self.current_token[1] == '(':
            self.match('(')
            self.E()
            self.match(')')
        else:
            raise SyntaxError("Invalid expression")


tokens = [('IDENTIFIER', 'x'), ('+', '+'), ('INT_CONSTANT', '10'), ('*', '*'), ('IDENTIFIER', 'y')]
print("input: x + 10 * y")
parser = LLParser(tokens)
try:
    parser.parse()
    print("Top-Down Parsing successful!")
    import json
    print(json.dumps(parser.parse_tree, indent=4))
except SyntaxError as e:
    print(f"Syntax Error: {e}")




class GrammarAnalyzer:
    def __init__(self, grammar):
        self.grammar = grammar
        self.first_sets = {}
        self.follow_sets = {}
        self.non_terminals = set(self.grammar.keys())

    def compute_first_sets(self):
        for nt in self.non_terminals:
            self.first_sets[nt] = set()

        changed = True
        while changed:
            changed = False
            for nt in self.non_terminals:
                for production in self.grammar[nt]:
                    first_symbol = production[0]
                    if first_symbol not in self.non_terminals:  
                        if first_symbol not in self.first_sets[nt]:
                            self.first_sets[nt].add(first_symbol)
                            changed = True
                    else:  
                        old_size = len(self.first_sets[nt])
                        self.first_sets[nt] |= self.first_sets[first_symbol]
                        if len(self.first_sets[nt]) > old_size:
                            changed = True

    def compute_follow_sets(self):
        start_symbol = list(self.grammar.keys())[0]
        self.follow_sets[start_symbol] = {'$'}  

        for nt in self.non_terminals:
            self.follow_sets[nt] = set()

        changed = True
        while changed:
            changed = False
            for nt in self.non_terminals:
                for production in self.grammar[nt]:
                    for i in range(len(production)):
                        symbol = production[i]
                        if symbol in self.non_terminals:
                            if i < len(production) - 1:
                                next_symbol = production[i + 1]
                                old_size = len(self.follow_sets[symbol])
                                if next_symbol in self.non_terminals:
                                    self.follow_sets[symbol] |= (self.first_sets[next_symbol] - {'epsilon'})
                                else:
                                    self.follow_sets[symbol].add(next_symbol)
                                if len(self.follow_sets[symbol]) > old_size:
                                    changed = True
                            else:  
                                old_size = len(self.follow_sets[symbol])
                                self.follow_sets[symbol] |= self.follow_sets[nt]
                                if len(self.follow_sets[symbol]) > old_size:
                                    changed = True

    def print_first_sets(self):
        print("FIRST Sets:")
        for nt in sorted(self.non_terminals):
            print(f"FIRST({nt}): {self.first_sets[nt]}")

    def print_follow_sets(self):
        print("\nFOLLOW Sets:")
        for nt in sorted(self.non_terminals):
            print(f"FOLLOW({nt}): {self.follow_sets[nt]}")

    def generate_tables(self):
        self.compute_first_sets()
        self.compute_follow_sets()
        self.print_first_sets()
        self.print_follow_sets()


grammar = {
    'E': [['E', '+', 'T'], ['E', '-', 'T'], ['T']],
    'T': [['T', '*', 'F'], ['T', '/', 'F'], ['F']],
    'F': [['(', 'E', ')'], ['id'], ['num']]
}

analyzer = GrammarAnalyzer(grammar)

analyzer.generate_tables()



