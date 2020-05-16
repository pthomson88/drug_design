from drug_design.similarity import levenshtein

def simcheck(a,b):
    test=similarity.levenshtein(a,b)
    return(test)
test=simcheck("c","d")
print(test)
