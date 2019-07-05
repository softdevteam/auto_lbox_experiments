from treemanager import TreeManager
from grammar_parser.gparser import Nonterminal, Terminal

def next_node(node):
    while(node.right is None):
        node = node.parent
    return node.right

def subtree_to_text(subtree):
    l = []
    if subtree.children:
        for child in subtree.children:
            l.append(subtree_to_text(child))
    elif type(subtree.symbol) is Terminal:
        l.append(subtree.symbol.name)
    return "".join(l)

def remove_tabs_newlines(inp,replnl=""):
    return inp.replace("\r",replnl).replace("\t", "").replace("\n", replnl)

def find_nonterms_by_name(tm, cond):
    l = []
    bos = tm.get_bos()
    eos = tm.get_eos()
    node = bos.right_sibling()
    while node is not eos:
        if cond(node):
            l.append(node)
            # don't traverse this node for further expressions as those are
            # already included
            node = next_node(node)
            continue
        if node.children:
            node = node.children[0]
            continue
        node = next_node(node)
    return l

def find_subtree(grammar, program, cond):
    parser, lexer = grammar.load()
    treemanager = TreeManager()
    treemanager.add_parser(parser, lexer, grammar.name)
    try:
        treemanager.import_file(program)
    except Exception:
        return None
    if parser.last_status is False:
        return None

    # find all sub expressions
    l = find_nonterms_by_name(treemanager, cond)
    return [subtree_to_text(st).rstrip() for st in l]
