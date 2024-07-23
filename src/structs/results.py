
def get_results_for_verification():
    pass

def calc_best_HS_val(HSTree, index):
    random_values = get_random_values()
    incon_values = get_incon_values()
    leafs_random = {}
    leafs_incon = {}

    for _,leaf in HSTree.leaf_nodes:
        HS = HSTree.get_hitting_set_for_leaf(leaf)
        random_HS_value = sum(random_values[element] for element in HS.get_elements())
        incon_HS_value = sum(incon_values[element] for element in HS.get_elements())
        
        leafs_random[leaf] = random_HS_value
        leafs_incon[leaf] = incon_HS_value
    
    if index == 0:
        # Find the maximum values
        best_random_leaf = max(leafs_random, key=leafs_random.get)
        best_random_card = len(HSTree.get_hitting_set_for_leaf(best_random_leaf).get_elements())

        best_incon_leaf = max(leafs_incon, key=leafs_incon.get)
        best_incon_card = len(HSTree.get_hitting_set_for_leaf(best_incon_leaf).get_elements())  
    
    if index == -1:
        best_random_leaf = min(leafs_random, key=leafs_random.get)
        best_random_card = len(HSTree.get_hitting_set_for_leaf(best_random_leaf).get_elements())
        best_incon_leaf = min(leafs_incon, key=leafs_incon.get)
        best_incon_card = len(HSTree.get_hitting_set_for_leaf(best_incon_leaf).get_elements())  

    best_random = leafs_random[best_random_leaf]
    best_incon = leafs_incon[best_incon_leaf]

    return best_random, best_random_card, best_incon, best_incon_card

def get_ranked_node(HSTree, index):
    sorted_leaf_nodes = sorted(
        HSTree.leaf_nodes,
        key=lambda item: len(hitting_set_tree.get_hitting_set_for_leaf(item[1]).get_elements())
    )
    return sorted_leaf_nodes[index]