from lark import Lark, Token
import itertools

# Define the grammar for the parser
grammar = """
    ?start: formula
    ?formula: equiv_formula
    ?equiv_formula: xor_formula (LEQUIV xor_formula)?
    ?xor_formula: impl_formula (LXOR impl_formula)?
    ?impl_formula: or_formula (LIMPLIES or_formula)?
    ?or_formula: and_formula (LOR and_formula)*
    ?and_formula: not_formula (LAND not_formula)*
    ?not_formula: (LNOT)? subformula
    ?subformula: NAME -> atom
        | LBRACE formula RBRACE

    LBRACE: "("
    RBRACE: ")"
    LNOT: "!"
    LAND: "&&"
    LOR: "||"
    LIMPLIES: "=>"
    LXOR: "^^"
    LEQUIV: "<=>"

    %import common.CNAME -> NAME
    %import common.WS_INLINE
    %ignore WS_INLINE
"""

# Parser initialization
parser = Lark(grammar, parser="lalr")

# Dataset of logical expressions
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

# Function to generate Tseitin variables
def generate_tseitin_var(var_counter):
    return f"z{next(var_counter)}"

# Function to convert a parsed formula to CNF using Tseitin transformation
def formula_to_cnf(parsed_formula, var_counter):
    # Check if the parsed_formula is a Token (like an atom or an operator)
    if isinstance(parsed_formula, Token):
        if parsed_formula.type == "NAME":  # If it's a NAME token (i.e., an atom), return it directly
            return parsed_formula.value, []
        else:
            return "", []  # For other types of tokens (operators), return an empty string and no clauses

    # Generate a new Tseitin variable for this subformula
    tseitin_var = generate_tseitin_var(var_counter)

    # Process children and collect clauses
    clauses = []
    child_vars = []
    for child in parsed_formula.children:
        if isinstance(child, Token) and child not in ["&&", "||"]:
            continue  # Skip logical operators and handle only subformulas
        child_var, child_clauses = formula_to_cnf(child, var_counter)
        if child_var:  # Add non-empty child_vars (ignoring empty strings from operators)
            child_vars.append(child_var)
            clauses.extend(child_clauses)

    # Add clauses based on the logical operator
    if parsed_formula.data == "and_formula":
        # Tseitin var is true iff all children are true
        clauses.append([tseitin_var] + [f"-{var}" for var in child_vars])
        for var in child_vars:
            clauses.append([f"-{tseitin_var}", var])

    elif parsed_formula.data == "or_formula":
        # Tseitin var is true iff any child is true
        clauses.append([f"-{tseitin_var}"] + child_vars)
        for var in child_vars:
            clauses.append([tseitin_var, f"-{var}"])

    return tseitin_var, clauses

# Parse each formula in the dataset and convert to CNF
cnf_clauses = []
var_counter = itertools.count(1)
for formula in dataset:
    parsed_formula = parser.parse(formula)
    _, formula_clauses = formula_to_cnf(parsed_formula, var_counter)
    cnf_clauses.extend(formula_clauses)

# Flatten and sort the clauses for readability
flat_clauses = sorted([" ".join(clause) for clause in cnf_clauses])

# Print the resulting CNF clauses
print("CNF Clauses:")
for clause in flat_clauses:
    print(clause)
