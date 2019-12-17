import boolean
algebra = boolean.BooleanAlgebra()

def tseitin(f):
    if type(f) == boolean.boolean.Symbol and len(f.get_symbols()) == 1:
        return f, f #impossible d'avoir une expression vide pour c...
    
    elif type(f) == boolean.boolean.NOT:
        nonf = (~f).demorgan() #pour simplifier la double négation
        p, c = tseitin(nonf)
        return (~p).demorgan(), c
    
    else:
        f1 = f.args[0]
        f2 = f.args[1]
        n  = len(f.args)
        if n > 2:
            for k in range(1, n-2):
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
            name_number += 1
            new_variable_name = 'p' + str(name_number)

        p = algebra.parse(new_variable_name)

        if f.operator == '|':
            c = algebra.parse('c') #TODO: écrire la bonne formule
            return p, c
        if f.operator == '&':
            c = algebra.parse('c') #TODO: écrire la bonne formule
            return p, c