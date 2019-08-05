import sys, re, os, json
from grammars.grammars import lang_dict
from extractor import find_subtree, remove_tabs_newlines

java = lang_dict["Java"]

import re
RE_CMT = re.compile(r"}(\s|\\r)*/\*.*?\*/$", re.MULTILINE)

import glob
if __name__ == "__main__":
    target = sys.argv[1]
    output = sys.argv[2]
    results = []
    folder = "../../../javastdlib5/"
    for filename in glob.iglob(folder+'**/**/*.java'):
        if not filename.endswith(".java"):
            continue
        with open(filename) as f:
            content = f.read()
        content = content.replace("\n", "\r")
        if target == "functions":
            cond = lambda x: x.symbol.name == "method_declaration"
        elif target == "expressions":
            cond = lambda x: x.symbol.name == "assignment_expression"
        expr = find_subtree(java, content, cond)
        if expr:
            print filename, ":", len(expr)
            for e in expr:
                try:
                    e.decode("utf8")
                    if target == "expressions":
                        e = remove_tabs_newlines(e)
                    else:
                        e = RE_CMT.sub("}", e)
                    results.append(e)
                except UnicodeDecodeError:
                    # we can't deal with unicode yet
                    continue
        else:
            print filename, "x"
    print "Total:", len(results)

    with open(output, "w") as f:
        json.dump(results, f, indent=0)
