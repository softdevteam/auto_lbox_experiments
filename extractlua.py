import sys, re, os, json
from grammars.grammars import lang_dict
from extractor import find_subtree, remove_tabs_newlines

lua = lang_dict["Lua 5.3"]

def expr_filter(n):
    return n.symbol.name == "explist"

def func_filter(n):
    if n.symbol.name == "stat" and n.children:
        if n.children[0].symbol.name == "function":
            return True
        if n.children[0].symbol.name == "local" and n.children[2].symbol.name == "function":
            return True
    return False

filters = {}
filters["expressions"] = expr_filter
filters["functions"] = func_filter

RE_CMT = re.compile("--([^\r]*)")

if __name__ == "__main__":
    target = sys.argv[1]
    output = sys.argv[2]
    results = []
    folder = "../../../lua/testes/"
    for filename in os.listdir(folder):
        if not filename.endswith(".lua"):
            continue
        with open(folder + filename) as f:
            content = f.read()
        if content.startswith("#"):
            # remove #!
            content = content[content.find("\n")+1:]
        content = content.replace("\n", "\r")
        expr = find_subtree(lua, content, filters[target])
        if expr:
            print filename, ":", len(expr)
            for e in expr:
                try:
                    e.decode("utf8")
                    if target == "expressions":
                        e = RE_CMT.sub("", e)
                        e = remove_tabs_newlines(e, replnl=" ")
                    if e.startswith("[["):
                        # ignore long bracket strings, e.g. [[string]]
                        continue
                    results.append(e)
                except UnicodeDecodeError:
                    # we can't deal with unicode yet
                    continue
        else:
            print filename, "x"
    print "Total:", len(results)

    with open(output, "w") as f:
        json.dump(results, f, indent=0)
