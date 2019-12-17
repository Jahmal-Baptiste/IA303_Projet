import boolean, numpy as np
from dpll    import DPLL
from tseitin import tseitin
algebra = boolean.BooleanAlgebra()

#--------------------------------------------------------------------------------------------
# création d'un fichier .cnf
file_name  = 'fichier_type.cnf'
commentary = '' #commentaires à mettre dans le fichier .cnf
expression = 'a & b' #expression booléenne sur laquelle travailler


### Lire une formule logique sous forme d’une chaîne de caractères
f = algebra.parse(expression)


### Transformer cette formule en CNF
cnf = algebra.cnf(f)


###==========================================================================================
### Traduire la formule CNF dans le format DIMACS
def get_str(variable, variables):
    '''
    Retourne le numéro de la variable considérée, accompagné de son signe.
    Cette fonction sert à traduire le formalisme de boolean à celui du format DIMACS.
    '''
    sign = '+' #signe par défaut d'une variable
    if type(variable) == boolean.boolean.NOT: #si la variable est 
        variable = variable.args[0]
        sign = '-'
    for k in range(len(variables)):
        if variable == variables[k]:
            if sign == '-':
                return sign + str(k+1)
            return str(k+1)

variables = f.get_symbols()
clauses   = cnf.args
n, c      = len(variables), len(clauses)

dimacs    = 'c {0}\nc {1}\np cnf {2} {3}'.format(file_name, commentary, str(n), str(c))
for i in range(c):
    dimacs += '\n'
    if type(clauses[i]) == boolean.boolean.Symbol:
        variable  = clauses[i]
        dimacs   += get_str(variable, variables)
        dimacs   += ' '
    else:
        num = len(clauses[i])
        for j in range(num):
            variable  = clauses[i].args[j]
            dimacs   += get_str(variable, variables)
            dimacs   += ' '
    dimacs += '0'

dimacs_file = open(file_name, 'w')
dimacs_file.write(dimacs)
dimacs_file.close()


###==========================================================================================
###==========================================================================================
### Coder l’algorithme DPLL pour résoudre la formule logique donnée dans le format DIMACS

#--------------------------------------------------------------------------------------------
# transformation du fichier DIMACS en array numpy
dimacs_file  = open(file_name, 'r')
dimacs_lines = dimacs_file.readlines()
n, c, l0     = 0, 0, 0
for l in range(len(dimacs_lines)):
    line = dimacs_lines[l].split(' ')
    if line[0] == 'p':
        n, c = int(line[2]), int(line[3])
        l0   = l + 1
        break

F = np.zeros((c, n), dtype=int)
M = np.zeros(n,      dtype=int)

for l in range(l0, len(dimacs_lines)):
    i    = l-l0
    line = dimacs_lines[l].split(' ')
    for j in range(len(line)-1):
        variable_str = line[j]
        value        = int(variable_str)
        sign         = 1
        if variable_str[0] == '-':
            sign     = -1
        variable       = int(np.abs(value))-1
        F[i][variable] = sign

#--------------------------------------------------------------------------------------------
# utilisation de l'algorithme

SATvalue, M = DPLL(F, M)
print(str(SATvalue) + ' ' + str(M))

###==========================================================================================
###==========================================================================================
### Extension : transformation de Tseitin

cnf = tseitin(f)
print(cnf)