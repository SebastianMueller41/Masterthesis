import re

class TseitinTransformer:
    def __init__(self):
        self.var_counter = 1
        self.var_map = {}
        self.clauses = []

    def transform(self, formula):
        if isinstance(formula, str):
            if formula in self.var_map:
                return self.var_map[formula]
            else:
                self.var_map[formula] = self.var_counter
                self.var_counter += 1
                return self.var_map[formula]
        elif formula[0] == 'not':
            var = self.transform(formula[1])
            return -var
        else:
            new_var = self.var_counter
            self.var_counter += 1
            for subformula in formula[1:]:
                sub_var = self.transform(subformula)
                if formula[0] == 'and':
                    self.clauses.append([-new_var, sub_var])
                elif formula[0] == 'or':
                    self.clauses.append([new_var, -sub_var])
            if formula[0] == 'and':
                self.clauses.append([new_var] + [-self.transform(subformula) for subformula in formula[1:]])
            elif formula[0] == 'or':
                self.clauses.append([-new_var] + [self.transform(subformula) for subformula in formula[1:]])
            return new_var

    def to_dimacs(self):
        dimacs_clauses = []
        for clause in self.clauses:
            dimacs_clauses.append(" ".join(map(str, clause)) + " 0")
        header = f'p cnf {self.var_counter - 1} {len(dimacs_clauses)}'
        return header + '\n' + '\n'.join(dimacs_clauses)

def parse_formula(formula_str):
    def tokenize(s):
        tokens = s.replace("(", " ( ").replace(")", " ) ").split()
        return [t for t in tokens if t]

def parse_formula(formula_str):
    def tokenize(s):
        s = s.replace("&&", " and ").replace("||", " or ").replace("!", " not ").replace("(", " ( ").replace(")", " ) ")
        return s.split()

    def parse(tokens):
        def next_token():
            return tokens.pop(0) if tokens else None

        def parse_expression():
            token = next_token()
            if token is None:
                raise SyntaxError("Unexpected EOF")
            if token == '(':
                sub_expr = []
                while tokens and tokens[0] != ')':
                    sub_expr.append(parse_expression())
                if not tokens or next_token() != ')':
                    raise SyntaxError("Expected ')'")
                if len(sub_expr) == 1:
                    return sub_expr[0]  # Unwrap single expressions
                return sub_expr
            elif token in ['not', 'and', 'or']:
                expr = [token]
                while tokens and tokens[0] not in [')', 'and', 'or']:
                    expr.append(parse_expression())
                return expr
            else:
                return token  # Variable

        expr = []
        while tokens:
            expr.append(parse_expression())
        return expr

    tokens = tokenize(formula_str)
    parsed_formula = parse(tokens)
    if tokens:
        raise SyntaxError("Unexpected tokens left")
    return parsed_formula



# Example usage
dataset = [
    "!(!A1&&A2)",
    "!(A0||A1)",
    "A1||((A2&&A0)&&A1)",
    "(A1||(A1&&A0))||A2",
    "!A0",
    "!A1",
    "!A2",
    "!A1&&(A2||A0)",
    "A1&&A0",
    "(A1||A1)&&(A2&&A0)"
]

transformer = TseitinTransformer()
for formula_str in dataset:
    parsed_formula = parse_formula(formula_str)
    transformer.transform(parsed_formula)

dimacs_cnf = transformer.to_dimacs()
print(dimacs_cnf)