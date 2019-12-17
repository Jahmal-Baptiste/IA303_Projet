import boolean, numpy as np
algebra = boolean.BooleanAlgebra()

#--------------------------------------------------------------------------------------------
# création d'un fichier .cnf
file_name  = 'fichier_type.cnf'
commentary = '' #commentaires à mettre dans le fichier .cnf
expression = '' #expression booléenne sur laquelle travailler


### Lire une formule logique sous forme d’une chaîne de caractères

parsed  = algebra.parse(expression)


### Transformer cette formule en CNF
cnf = algebra.cnf(parsed)


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

variables = parsed.get_symbols()
clauses   = cnf.args
n, c      = len(variables), len(clauses)

dimacs    = 'c {0}\nc {1}\np cnf {2} {3}'.format(file_name, commentary, str(n), str(c))
for i in range(c):
    dimacs += '\n'
    for j in range(len(clauses[i])):
        variable  = clauses[i].args[j]
        dimacs   += get_str(variable, variables)
        dimacs   += ' '
    dimacs       += '0'

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
    line = dimacs_lines[l]
    if line[0] == 'p':
        n, c = line[2], line[3]
        break

F = np.zeros((c, n), dtype=int)
M = np.zeros(n,      dtype=int)

for l in range(l0, len(dimacs_lines)):
    i = l-l0
    for j in range(len(dimacs_lines[l])-1):
        variable_str = dimacs_lines[l][j]
        sign = 1
        if variable_str[0] == '-':
            sign = -1
        variable       = int(np.abs(variable_str))-1
        F[i][variable] = sign

#--------------------------------------------------------------------------------------------
# variables globales pour l'algorithme DPLL
SAT    = 1
UNSAT  = 0
answer = ['UNSAT', 'SAT']

#============================================================================================
# algorithme
def DPLL(F, M):
    SATvalue     = SATTest(F, M)
    if SATvalue != -1:
        return SATvalue, M
    
    F, M         = UnitPropagate(F, M)
    SATvalue     = SATTest(F, M)
    if SATvalue != -1:
        return SATvalue, M
    
    not_assigned = np.abs(M) - 1                  #vaut 0 où les variables sont assignées et -1 pour les autres
    l            = np.nonzero(not_assigned)[0][0] #première varialble non-assignée
    M[l]         = 1                              #assignation de cette variable à 1
    if DPLL(F, M)[0] == SAT:
        return SAT, M
    
    F[:, l] = -F[:, l]
    M[l]    = -1
    return DPLL(F, M)

#--------------------------------------------------------------------------------------------
def UnitPropagate(F, M):
    '''
    F est une formule CNF - un tableau donc.
    M est un modèle - une ligne donc.
    '''
    hec  = HasEmptyClause(F) #booléen
    c, l = UnitClause(F, M)  #première clause unitaire qui apparaît
    while hec == False and c > -1:
        M[l]     = F[c, l]                  #attribution de la bonne valeur dans le moddèle
        F[:, l] *= F[c, l]                  #propagation
        F[:, l]  = np.heaviside(F[:, l], 0) #élimination des valeurs négatives
        ##actualisation pour la boucle :
        hec      = HasEmptyClause(F)
        c, l     = UnitClause(F, M)

    return F, M

#============================================================================================
def UnitClause(F, M):
    '''
    Retourne la prmière clause unitaire trouvée dans le CNF.
    Les clauses vraies sont ignorées.
    '''
    for c in range(F.shape[0]):
        if IsTrue(c, F, M) < 1:
            F_c    = np.copy(F[c, :])
            F_c    = np.abs(F_c) - np.abs(M)
            F_c    = np.heaviside(F_c, 0)
            valued = np.nonzero(F_c)[0]     #indices des valeurs attribuées
            if valued.shape[0] == 1:
                return c, valued[0]
    return -1, -1 #aucune clause unitaire n'a été trouvée

#--------------------------------------------------------------------------------------------
def HasEmptyClause(F):
    '''Retourne le booléen disant s'il y a une clause vide'''
    for c in range(F.shape[0]):
        if np.sum(np.abs(F[c, :])) == 0: #nombre de variables valuées dans cette clause
            return True
    return False

#--------------------------------------------------------------------------------------------
def SATTest(F, M):
    '''
    Retourne la valeur du test de validité ou -1 si rien ne peut être conclu.
    '''
    num_clauses      = F.shape[0]
    num_true_clauses = 0
    for c in range(num_clauses):
        c_truth = IsTrue(c, F, M)
        if   c_truth == 0: #une des clauses est fausse
            return UNSAT
        elif c_truth == -1: #une des clauses n'est pas valuée
            break
        num_true_clauses += 1
    if num_true_clauses == num_clauses: #toutes les clauses sont vraies
        return SAT
    return -1

#--------------------------------------------------------------------------------------------
def IsTrue(c, F, M):
    '''
    Retourne le booléen (0 ou 1) disant si la clause c est vraie, lorsque c'est possible.
    Retourne -1 si la clause n'est pas valuée.
    '''
    valued_clause    = F[c, :]*np.abs(M)
    clause_value     = np.max(valued_clause)
    if clause_value == 1:
        return 1      #clause vraie
    for l in range(F.shape[1]):
        if F[c, l] != 0 and M[l] == 0:
            return -1 #clause non valuée
    return 0          #clause fausse


###==========================================================================================
###==========================================================================================
### Extension : transformation de Tseitin

def tseitin(f):
    if type(f) == boolean.boolean.Symbol:
        return f, f #impossible d'avoir une expression vide pour c...
    
    elif type(f) == boolean.boolean.NOT:
        nonf = (~f).demorgan() #pour simplifier la double négation
        p, c = tseitin(nonf)
        return (~p).demorgan(), c
    
    else:
        f1 = f.args[0]
        f2 = f.args[1]
        n  = len(f.args)
        for k in range(2, n):
            f2 = f2 | f.args[k]
        
        p1, c1 = tseitin(f1) #comme définis dans l'algorithme
        p2, c2 = tseitin(f2) #comme définis dans l'algorithme

        variables = f.get_symbols() #liste des variables
        names     = []              #liste des str des variables
        for variable in variables:
            names.append(variable.obj)
        new_variable_name = 'p0'
        name_number       = 0
        while new_variable_name in names:
            name_number      += 1
            new_variable_name = 'p' + str(name_number)

        p = algebra.parse(new_variable_name)

        if f.operator == '|':
            p_  = ~p | p1 | p2
            p_1 = p  | (~p1).demorgan()
            p_2 = p  | (~p2).demorgan()
            c   = p_ & p_1 & p_2 & c1 & c2
            return p, c
        
        elif f.operator == '&':
            p_  = p  | (~p1).demorgan() | (~p2).demorgan()
            p_1 = ~p | p1
            p_2 = ~p | p2
            c   = p_ & p_1 & p_2 & c1 & c2
            return p, c