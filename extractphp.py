import sys, re, os, json
from grammars.grammars import lang_dict
from extractor import find_subtree, remove_tabs_newlines

php = lang_dict["PHP"]
MAX_CHAR_LENGTH = 5000

def expressions_filter(n):
    return n.symbol.name == "expr_without_variable" and n.children[0].symbol.name == "expr"

def functions_filter(n):
    #if n.symbol.name == "function_declaration_statement":
    #    return True
    if n.symbol.name == "class_statement":
        return n.children[1].symbol.name == "function"
    return False

RE_HTML = re.compile("\?>(.|\n)*?<\?php")
RE_CMT = re.compile(r"}(\s|\\r)*/\*.*?\*/$", re.MULTILINE)
if __name__ == "__main__":
    target = sys.argv[1]
    output = sys.argv[2]
    results = []
    folder = "../../../wordpress/wp-includes/"
    for filename in os.listdir(folder):
        if not filename.endswith(".php"):
            continue
        with open(folder + filename) as f:
            content = f.read()
        # remove html
        content = RE_HTML.sub("", content)
        content = content.replace("\n", "\r")
        if content.startswith("<?php"):
            content = content[5:]
        if content.endswith("?>"):
            content = content[:-2]
        if target == "expressions":
            cond = expressions_filter
        elif target == "functions":
            cond = functions_filter
        expr = find_subtree(php, content, cond)
        if expr: 
            print filename, ":", len(expr)
            # Remove comments at the end of the expression/function
            # Exclude functions > 1000 chars
            for e in expr:
                e = RE_CMT.sub("}", e)
                # Exclude long fragments to cut down the overall runtime of the
                # experiment
                if len(e) < MAX_CHAR_LENGTH:
                    if target == "expressions":
                        e = remove_tabs_newlines(e)
                    results.append(e)
        else:
            print filename, ": x"
    print "Total:", len(results)

    with open(output, "w") as f:
        json.dump(results, f, indent=0)
