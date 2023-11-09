"""
Copyright (c) <2023> <Andreas Niskanen, University of Helsinki>



Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:



The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.



THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
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

	def __repr__(self):
		string = (self.depth * " ") + ("-" if self.negation else "+") + " " + self.label + "\n"
		for formula in self.children:
			string += str(formula)
		return string

	def to_nnf(self):
		if self.is_atom:
			return
		if not self.negation:
			return
		self.negation = False
		if self.label == "&&":
			self.label = "||"
			for formula in self.children:
				formula.negation = not formula.negation
				formula.to_nnf()
		elif self.label == "||":
			self.label = "&&"
			for formula in self.children:
				formula.negation = not formula.negation
				formula.to_nnf()
		elif self.label == "=>":
			self.label = "&&"
			assert(len(self.children) == 2)
			l = self.children[0]
			r = self.children[1]
			r.negation = not r.negation
			l.to_nnf()
			r.to_nnf()
		elif self.label == "<=>":
			self.label = "^^"
			for formula in self.children:
				formula.negation = not formula.negation
				formula.to_nnf()
		elif self.label == "^^":
			self.label = "<=>"
			for formula in self.children:
				formula.negation = not formula.negation
				formula.to_nnf()

	# Returns a CNF which is equisatisfiable with the formula via the Tseitin encoding.
	def to_cnf(self, atom_vars, var_counter, unique=False, occs={}):
		clauses = []
		if self.is_atom:
			return clauses
		for formula in self.children:
			if not formula.is_atom:
				formula.tseitin_var = next(var_counter)
			else:
				if unique and formula.label != top and formula.label != bot:
					formula.tseitin_var = next(var_counter)
					occs[formula.label].append(formula.tseitin_var)
				else:
					formula.tseitin_var = atom_vars[formula.label]
			formula.tseitin_lit = (-1 if formula.negation else 1) * formula.tseitin_var
		clauses = []
		if self.label == "&&":
			clauses.append([self.tseitin_var] + [-formula.tseitin_lit for formula in self.children])
			for formula in self.children:
				clauses.append([-self.tseitin_var, formula.tseitin_lit])
		elif self.label == "||":
			clauses.append([-self.tseitin_var] + [formula.tseitin_lit for formula in self.children])
			for formula in self.children:
				clauses.append([self.tseitin_var, -formula.tseitin_lit])
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

class CNFFormula:

	def __init__(self, input_clauses=None):
		self.atoms = set()
		self.clauses = input_clauses
		self.is_atom = False
		self.negation = False
		self.is_hard = False
		if input_clauses is not None:
			self.is_atom = len(self.clauses) == 1 and len(self.clauses[0]) == 1
			for clause in input_clauses:
				for lit in clause:
					self.atoms.add(abs(lit))
			if self.is_atom:
				self.label = abs(self.clauses[0][0])
				self.negation = self.clauses[0][0] < 0

	def __repr__(self):
		string = ""
		for clause in self.clauses:
			string += " ".join(map(str, clause)) + " 0\n"
		return string

	def to_cnf(self, atom_vars, var_counter, unique=False, occs={}):
		if self.is_atom and not self.is_hard:
			return []
		new_clauses = []
		for clause in self.clauses:
			if not unique:
				new_clause = [atom_vars[lit] if lit > 0 else -atom_vars[-lit] for lit in clause]
			else:
				new_clause = []
				for lit in clause:
					new_var = next(var_counter)
					new_lit = new_var if lit > 0 else -new_var
					occs[abs(lit)].append(new_var)
					new_clause.append(new_lit)
			if not self.is_hard:
				new_clause = [-self.tseitin_var] + new_clause
			new_clauses.append(new_clause)
		return new_clauses

class KnowledgeBase:

	def __init__(self, input_file=None, file_format="pl", nnf=False):
		self.format = file_format
		self.formulas = []
		self.atoms = set()
		self.var_counter = itertools.count(1)
		if self.format == "pl":
			parser = lark.Lark(grammar, parser="lalr")
			for i, line in enumerate(input_file):
				if len(line) == 0:
					continue
				res = parser.parse(line)
				self.formulas.append(Formula(res))
			if nnf:
				for formula in self.formulas:
					formula.to_nnf()
		elif self.format == "cnf":
			for line in input_file:
				if line.startswith("p") or line.startswith("c"):
					continue
				clause = list(map(int, line.split()))[:-1]
				self.formulas.append(CNFFormula([clause]))
		elif self.format == "gcnf":
			clause_groups = {}
			for i, line in enumerate(input_file):
				if line.startswith("p") or line.startswith("c"):
					continue
				head, *tail = line.split()
				index = int(head[1:-1])
				clause = list(map(int, tail))[:-1]
				if index in clause_groups:
					clause_groups[index].append(clause)
				else:
					clause_groups[index] = [clause]
			for index in sorted(clause_groups.keys()):
				if index == 0:
					self.hard = CNFFormula(clause_groups[index])
					self.hard.is_hard = True
					self.atoms.update(self.hard.atoms)
				else:
					self.formulas.append(CNFFormula(clause_groups[index]))
			# for now, add atoms from hard constraints to formula atoms
			if self.hard is not None:
				for formula in self.formulas:
					formula.atoms.update(self.hard.atoms)
		for i, formula in enumerate(self.formulas):
			self.atoms.update(formula.atoms)
		self.atoms = sorted(list(self.atoms))

	# Returns a group CNF encoding of a given knowledge base. If `atom_names` is
	# - "global": considers each formula in the knowledge base as is;
	# - "local":  considers a copy F' of each formula F in the knowledge base, replacing atom x is by variable x_F;
	# - "unique": considers a copy Fo of each formula F in the knowledge base, replacing ith occurrence of atom x by variable x_i.
	def to_group_cnf(self, atom_names="global"):
		hard_clauses = []
		soft_lits = []
		self.atom_vars = { atom : next(self.var_counter) for atom in self.atoms }
		if self.format == "pl":
			if top in self.atoms:
				hard_clauses.append([self.atom_vars[top]])
			if bot in self.atoms:
				hard_clauses.append([-self.atom_vars[bot]])
		if atom_names == "global":
			if self.format == "gcnf":
				hard_clauses.extend(self.hard.to_cnf(self.atom_vars, self.var_counter))
			for formula in self.formulas:
				if not formula.is_atom:
					formula.tseitin_var = next(self.var_counter)
				else:
					formula.tseitin_var = self.atom_vars[formula.label]
				formula.tseitin_lit = (-1 if formula.negation else 1) * formula.tseitin_var
				hard_clauses.extend(formula.to_cnf(self.atom_vars, self.var_counter))
				soft_lits.append(formula.tseitin_lit)
		elif atom_names == "local":
			for formula in self.formulas:
				formula.atom_vars = { atom : next(self.var_counter) for atom in formula.atoms if atom != top and atom != bot }
				if top in self.atoms:
					formula.atom_vars[top] = self.atom_vars[top]
				if bot in self.atoms:
					formula.atom_vars[bot] = self.atom_vars[bot]
				if self.format == "gcnf":
					hard_clauses.extend(self.hard.to_cnf(formula.atom_vars, self.var_counter))
				#formula.atom_vars = { atom : next(self.var_counter) for atom in self.atoms }
				if not formula.is_atom:
					formula.tseitin_var = next(self.var_counter)
				else:
					if formula.label == top or formula.label == bot:
						formula.tseitin_var = self.atom_vars[formula.label]
					else:
						formula.tseitin_var = formula.atom_vars[formula.label]
				formula.tseitin_lit = (-1 if formula.negation else 1) * formula.tseitin_var
				hard_clauses.extend(formula.to_cnf(formula.atom_vars, self.var_counter))
				soft_lits.append(formula.tseitin_lit)
		elif atom_names == "unique":
			if self.format == "gcnf":
				hard_clauses.extend(self.hard.to_cnf(self.atom_vars, self.var_counter))
			occs = { atom : [] for atom in self.atoms }
			for formula in self.formulas:
				if self.format == "pl" and (formula.label == top or formula.label == bot):
					formula.tseitin_var = self.atom_vars[formula.label]
				else:
					formula.tseitin_var = next(self.var_counter)
					if formula.is_atom and formula.label != top and formula.label != bot:
						occs[formula.label].append(formula.tseitin_var)
				formula.tseitin_lit = (-1 if formula.negation else 1) * formula.tseitin_var
				hard_clauses.extend(formula.to_cnf(self.atom_vars, self.var_counter, True, occs))
				soft_lits.append(formula.tseitin_lit)
			self.occurrences = occs
		return hard_clauses, soft_lits

def print_gcnf(kb):
	hard, soft = kb.to_group_cnf()
	n_vars = next(kb.var_counter)-1
	n_clauses = len(hard) + len(soft)
	n_groups = len(soft)
	for atom in kb.atoms:
		print("c " + atom + " = " + str(kb.atom_vars[atom]))
	for i, lit in enumerate(soft):
		print("c F" + str(i+1) + " = " + str(lit))
	print("p gcnf " + str(n_vars) + " " + str(n_clauses) + " " + str(n_groups))
	for clause in hard:
		print("{0} " + " ".join(map(str, clause)) + " 0")
	for i, lit in enumerate(soft):
		print("{" + str(i+1) + "} " + str(lit) + " 0")

def print_wcnf(kb):
	hard, soft = kb.to_group_cnf()
	n_vars = next(kb.var_counter)-1
	n_clauses = len(hard) + len(soft)
	top = len(soft)+1
	for atom in kb.atoms:
		print("c " + atom + " = " + str(kb.atom_vars[atom]))
	for i, lit in enumerate(soft):
		print("c F" + str(i+1) + " = " + str(lit))
	print("p wcnf " + str(n_vars) + " " + str(n_clauses) + " " + str(top))
	for i, lit in enumerate(soft):
		print("1 " + str(lit) + " 0")
	for clause in hard:
		print(str(top) + " " + " ".join(map(str, clause)) + " 0")

if __name__ == "__main__":
	filename = sys.argv[1]
	kb = KnowledgeBase(open(filename).read().split("\n"))
	#print_gcnf(kb)
	#print_wcnf(kb)
	print("KB atoms: " + str(kb.atoms))
	print("KB formulas: " + str(kb.formulas))
	print("KB format: " + str(kb.format))