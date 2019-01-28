import sys, re, os, json
from grammars.grammars import python
from extractor import find_subtree, remove_tabs_newlines

def expr_filter(n):
    return n.symbol.name == "testlist" and n.left_sibling()

if __name__ == "__main__":
    output = sys.argv[1]
    results = []
    folder = "../../../flowblade/flowblade-trunk/Flowblade/"
    for filename in os.listdir(folder):
        if not os.path.splitext(filename)[1] == ".py":
            continue
        with open(os.path.join(folder, filename)) as f:
            content = f.read()
        # remove html
        content = content.replace("\n", "\r")
        expr = find_subtree(python, content, expr_filter)
        sys.stdout.flush()
        if expr:
            print filename, ":", len(expr)
            for e in expr:
                try:
                    e.decode("utf8")
                    e = remove_tabs_newlines(e)
                    results.append(e)
                except UnicodeDecodeError:
                    # we can't deal with unicode yet
                    continue
        else:
            print filename, "x"

    with open(output, "w") as f:
        json.dump(results, f, indent=0)
