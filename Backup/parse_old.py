"""
Copyright (c) <2023> <Andreas Niskanen, University of Helsinki>
"""

import itertools, sys
import lark

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
		| LTOP -> true | LBOT -> false
		| LBRACE formula RBRACE

	LBRACE: "("
	RBRACE: ")"
	LTOP: "+"
	LBOT: "-"
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

top = "+"
bot = "-"
all_connectives = ["&&", "||", "=>", "^^", "<=>"]

class Formula:

	def __init__(self, input_formula=None, depth=0):
		self.depth = depth
		self.label = None
		self.negation = False
		self.children = []
		self.is_atom = False
		self.atoms = set()
		if input_formula is not None:
			item = input_formula
			while item.data == "subformula" or item.data == "not_formula":
				if item.data == "not_formula":
					assert(len(item.children) == 2)
					self.negation = not self.negation
					item = item.children[1]
				if item.data == "subformula":
					assert(len(item.children) == 3)
					item = item.children[1]
			if item.data in ["and_formula", "or_formula", "impl_formula", "xor_formula", "equiv_formula"]:
				connectives = [elem for elem in item.children if elem in all_connectives]
				assert(all(elem == connectives[0] for elem in connectives))
				self.label = connectives[0]
				self.children = [Formula(elem, self.depth+1) for elem in item.children if elem != self.label]
				for formula in self.children:
					self.atoms.update(formula.atoms)
			else:
				assert(item.data == "atom" or item.data == "true" or item.data == "false")
				assert(len(item.children) == 1)
				self.label = item.children[0].value
				self.is_atom = True
				self.atoms.add(self.label)
		print("Formula init depth: " + str(self.depth))
		print("Formula init label: " + str(self.label))
		print("Formula init negation: " + str(self.negation))
		print("Formula init children: " + str(self.children))
		print("Formula init is_atom: " + str(self.is_atom))
		print("Formula init atoms: " + str(self.atoms))

	def __repr__(self):
		string = (self.depth * " ") + ("-" if self.negation else "+") + " " + self.label + "\n"
		for formula in self.children:
			string += str(formula)
		return string

	# Returns a CNF which is equisatisfiable with the formula via the Tseitin encoding.
	def to_cnf(self, atom_vars, var_counter, unique=False, occs={}):
		print("Formula_tocnf: " + str(atom_vars))
		clauses = []
		if self.is_atom:
			return clauses
		for formula in self.children:
			if not formula.is_atom:
				formula.tseitin_var = next(var_counter)
				print("Formula tocnf 1 var_counter: " + str(var_counter))
			else:
				if unique and formula.label != top and formula.label != bot:
					formula.tseitin_var = next(var_counter)
					occs[formula.label].append(formula.tseitin_var)
					print("Formula tocnf 2 occs: " + str(occs))
				else:
					formula.tseitin_var = atom_vars[formula.label]
			formula.tseitin_lit = (-1 if formula.negation else 1) * formula.tseitin_var
		clauses = []
		if self.label == "&&":
			clauses.append([self.tseitin_var] + [-formula.tseitin_lit for formula in self.children])
			print("Formula tocnf clauses after AND 1: " + str(clauses))
			for formula in self.children:
				clauses.append([-self.tseitin_var, formula.tseitin_lit])
				print("Formula tocnf clauses after AND 2: " + str(clauses))
		elif self.label == "||":
			clauses.append([-self.tseitin_var] + [formula.tseitin_lit for formula in self.children])
			print("Formula tocnf clauses after OR 1: " + str(clauses))
			for formula in self.children:
				clauses.append([self.tseitin_var, -formula.tseitin_lit])
				print("Formula tocnf clauses after OR 2: " + str(clauses))
		elif self.label == "=>":
			assert(len(self.children) == 2)
			l = self.children[0]
			r = self.children[1]
			clauses.append([-self.tseitin_var, -l.tseitin_lit, r.tseitin_lit])
			clauses.append([self.tseitin_var, l.tseitin_lit])
			clauses.append([self.tseitin_var, -r.tseitin_lit])
		elif self.label == "<=>":
			assert(len(self.children) == 2)
			l = self.children[0]
			r = self.children[1]
			clauses.append([self.tseitin_var, l.tseitin_lit, r.tseitin_lit])
			clauses.append([self.tseitin_var, -l.tseitin_lit, -r.tseitin_lit])
			clauses.append([-self.tseitin_var, l.tseitin_lit, -r.tseitin_lit])
			clauses.append([-self.tseitin_var, -l.tseitin_lit, r.tseitin_lit])
		elif self.label == "^^":
			assert(len(self.children) == 2)
			l = self.children[0]
			r = self.children[1]
			clauses.append([-self.tseitin_var, l.tseitin_lit, r.tseitin_lit])
			clauses.append([-self.tseitin_var, -l.tseitin_lit, -r.tseitin_lit])
			clauses.append([self.tseitin_var, l.tseitin_lit, -r.tseitin_lit])
			clauses.append([self.tseitin_var, -l.tseitin_lit, r.tseitin_lit])
		for formula in self.children:
			clauses.extend(formula.to_cnf(atom_vars, var_counter, unique, occs))
		return clauses

class KnowledgeBase:

	def __init__(self, input_file=None, file_format="pl"):
		self.format = file_format
		self.formulas = []
		self.atoms = set()
		self.var_counter = itertools.count(-1)
		if self.format == "pl":
			parser = lark.Lark(grammar, parser="lalr")
			for i, line in enumerate(input_file):
				if len(line) == 0:
					continue
				res = parser.parse(line)
				self.formulas.append(Formula(res))
		        # Collect all atoms from the formulas
		for formula in self.formulas:
			self.atoms.update(formula.atoms)
		
		self.atom_vars = {atom: next(self.var_counter) for atom in self.atoms}
		print("kb var_counter 1: " + str(self.var_counter))
	
	def to_cnf(self):
		hard_clauses = []
		self.atom_vars = {atom: next(self.var_counter) for atom in self.atoms}

		print("kb.tocnf atom_vars: " + str(self.atom_vars))

		if self.format == "pl":
			# Handling special atoms 'top' and 'bot' if present
			if top in self.atoms:
				hard_clauses.append([self.atom_vars[top]])
			if bot in self.atoms:
				hard_clauses.append([-self.atom_vars[bot]])
		
		print("kb atoms: " + str(self.atoms))
		print("kb var_counter: " + str(self.var_counter))
		print("kb.to_cnf_hard_clauses: "+ str(hard_clauses))

		# Convert each formula to CNF and add to hard clauses
		for formula in self.formulas:
			if not formula.is_atom:
				formula.tseitin_var = next(self.var_counter)
			else:
				formula.tseitin_var = self.atom_vars[formula.label]
			formula.tseitin_lit = (-1 if formula.negation else 1) * formula.tseitin_var
			print("kb.to_cnf forumla.tseitin_lit: " + str(formula.tseitin_lit))
			hard_clauses.extend(formula.to_cnf(self.atom_vars, self.var_counter))
			print("kb.to_cnf formula.to_cnf: " + str(self.atom_vars) + " " + str(self.var_counter))

		return hard_clauses

def print_cnf(kb):
    hard_clauses = kb.to_cnf()
    n_vars = len(kb.atom_vars)
    n_clauses = len(hard_clauses)
    
    """
    for atom in kb.atoms:
        print("c " + atom + " = " + str(kb.atom_vars[atom]))
    for i, lit in enumerate(hard_clauses):
        print("c F" + str(i+1) + " = " + str(lit))
	"""
    
	# Print header
    print("p cnf {} {}".format(n_vars, n_clauses))

    # Print each clause
    for clause in hard_clauses:
        print(" ".join(map(str, clause)) + " 0")

if __name__ == "__main__":
	filename = sys.argv[1]
	kb = KnowledgeBase(open(filename).read().split("\n"))
	print("kb.formulas: " + str(kb.formulas))
	print_cnf(kb)

"""
def convert_wcnf_to_cnf(wcnf_filename, cnf_filename):
    with open(wcnf_filename, 'r') as wcnf_file, open(cnf_filename, 'w') as cnf_file:
        for line in wcnf_file:
            if line.startswith('p wcnf'):
                # Change 'p wcnf' to 'p cnf'
                parts = line.split()
                parts[1] = 'cnf'
                cnf_file.write(' '.join(parts) + '\n')
            elif line[0].isdigit():
                # Remove weights from the clauses
                _, *clause = line.split()
                cnf_file.write(' '.join(clause) + '\n')
            else:
                cnf_file.write(line)
def write_gcnf_to_file(kb, filename):
    hard, soft = kb.to_group_cnf()
    n_vars = next(kb.var_counter) - 1
    n_clauses = len(hard) + len(soft)
    n_groups = len(soft)

    with open(filename, 'w') as file:
        for atom in kb.atoms:
            file.write("c " + atom + " = " + str(kb.atom_vars[atom]) + "\n")
        for i, lit in enumerate(soft):
            file.write("c F" + str(i+1) + " = " + str(lit) + "\n")
        file.write("p gcnf " + str(n_vars) + " " + str(n_clauses) + " " + str(n_groups) + "\n")
        for clause in hard:
            file.write(" ".join(map(str, clause)) + " 0\n")
        for i, lit in enumerate(soft):
            file.write("{" + str(i+1) + "} " + str(lit) + " 0\n")

def write_wcnf_to_file(kb, filename):
    hard, soft = kb.to_group_cnf()
    n_vars = next(kb.var_counter) - 1
    n_clauses = len(hard) + len(soft)
    top = len(soft) + 1

    with open(filename, 'w') as file:
        for atom in kb.atoms:
            file.write("c " + atom + " = " + str(kb.atom_vars[atom]) + "\n")
        for i, lit in enumerate(soft):
            file.write("c F" + str(i+1) + " = " + str(lit) + "\n")
        file.write("p wcnf " + str(n_vars) + " " + str(n_clauses) + " " + str(top) + "\n")
        for i, lit in enumerate(soft):
            file.write("1 " + str(lit) + " 0\n")
        for clause in hard:
            file.write(str(top) + " " + " ".join(map(str, clause)) + " 0\n")

def normalize_path(path):
    return path.replace(os.sep, '_').replace(':', '')
"""