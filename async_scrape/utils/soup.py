"""All methods relating to beautiful soup"""

def tree_find_all(soup, find_params:list):
    """Will descend tree collecting all results
    
    params are in format:
    [tag, {attrs}]
    """
    soups = [soup]
    for params in find_params:
        out = []
        for s in soups: 
            #Find all in current soup
            mini_soup = s.find_all(params[0], attrs=params[1])
            out.extend(mini_soup)
        soups = out.copy()
    return soups