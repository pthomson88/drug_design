#These three functions are involved in returning a unique key
#checks for a clash then if there is increments the integer at the end of the key until there is no clash
def key_increment(key_string, **dictionary):
    clash = clash_check(key_string, **dictionary)
    n = 1
    new_key_string = key_string
    while clash == True:
        new_key_string = update_key(key_string, n)
        clash = clash_check(new_key_string, **dictionary)
        n = n + 1
    return new_key_string

def clash_check(key_string, **dictionary):
    clash = False
    for key in dictionary:
        if key_string == key:
            clash  = True
    return clash

def update_key(key_string, n):
    new_key_string = key_string + str(n)
    return new_key_string

#this function returns the next (or k next) key in the dictionary
def get_shifted_key(d:dict, k:str, offset:int) -> str:
    l = list(d.keys())
    if k in l:
        i = l.index(k) + offset
        if 0 <= i < len(l):
            return l[i]
    return None
