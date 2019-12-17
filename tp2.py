import numpy as np
SAT    = 1
UNSAT  = 0
answer = ['UNSAT', 'SAT']

#============================================================================================
def DPLL(F, M):
    SATvalue     = SATTest(F, M)
    if SATvalue != -1:
        return SATvalue, M
    
    print('Before propag:\nF:\n' + str(F) + '\nM:\n' + str(M) + '\n')
    F, M         = UnitPropagate(F, M)
    print ('After propag:\nF:\n' + str(F) + '\nM:\n' + str(M) + '\n')
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


#============================================================================================
#============================================================================================
if __name__ == "__main__":
    #--------------------------------------------------
    F   = np.array([[-1, 1, -1],
                    [-1, -1, 1]], dtype=int)
    M   = np.zeros(3, dtype=int)
    res = DPLL(F, M)
    print(answer[res[0]] + ', ' + str(res[1]) + '\n')

    #--------------------------------------------------
    F   = np.array([[0, 0, 1],
                    [1, 1, 0]], dtype=int)
    M   = np.zeros(3, dtype=int)
    res = DPLL(F, M)
    print(answer[res[0]] + ', ' + str(res[1]) + '\n')
    
    #--------------------------------------------------
    F   = np.array([[ 1,  1,  0,  0],
                    [ 0,  1, -1,  1],
                    [-1, -1,  0,  0],
                    [-1,  0, -1, -1],
                    [ 1,  0,  0,  0]], dtype=int)
    M   = np.zeros(4, dtype=int)
    res = DPLL(F, M)
    print(answer[res[0]] + ', ' + str(res[1]))