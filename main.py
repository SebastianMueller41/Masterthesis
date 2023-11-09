from pysat.solvers import Solver
import parse

# Assuming 'clauses' is a list of lists, where each sublist represents a clause,
# and each integer in a sublist represents a literal (negative for NOT, positive for the variable itself)
clauses = parse.kb.formulas

# Initialize the solver
solver = Solver()

# Add the clauses to the solver
for clause in clauses:
    solver.add_clause(clause)

# Solve the problem
is_satisfiable = solver.solve()

# Output the result
if is_satisfiable:
    print("SATISFIABLE")
    model = solver.get_model()
    print("Model:", model)
else:
    print("UNSATISFIABLE")

# Don't forget to delete the solver to free resources
solver.delete()
