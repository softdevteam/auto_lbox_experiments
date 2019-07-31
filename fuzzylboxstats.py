import random, json, glob, os, time
from grammars.grammars import lang_dict, EcoFile
from treemanager import TreeManager
from grammar_parser.gparser import Nonterminal, Terminal
from incparser.astree import MultiTextNode

# helper functions

debug = False
MAX_FILES = 100

def next_node(node):
    while(node.right is None):
        node = node.parent
    return node.right

def prev_node(node):
    while(node.left is None):
        node = node.parent
    return node.left

def subtree_to_text(subtree):
    l = []
    if subtree.children:
        for child in subtree.children:
            l.append(subtree_to_text(child))
    elif type(subtree.symbol) is Terminal:
        l.append(subtree.symbol.name)
    return "".join(l).replace("\r", "").replace("\t", "").replace("\n", "")

def truncate(string):
    if len(string) > 40:
        return repr(string[:20] + "..." + string[-20:])
    else:
        return repr(string)

def validnonterm(node, symbol):
    if not isinstance(node.symbol, Nonterminal):
        return False
    if node.symbol.name != symbol:
        return False
    if node.symbol.name == "class_statement": # PHP func
        return node.children[1].symbol.name == "function"
    elif node.symbol.name == "expr_without_variable": # PHP expr
        return node.children[0].symbol.name == "expr"
    elif node.symbol.name == "testlist": # Python expr
        # Only replace RHS of expressions, because there's currently a bug that
        # keeps indentation terminals from being inserted before language boxes
        return node.left_sibling() is not None
    elif node.symbol.name == "stat": # Lua func
        if node.children:
            if node.children[0].symbol.name == "function":
                return True
            if node.children[0].symbol.name == "local" and node.children[2].symbol.name == "function":
                return True
        return False
    return True

class FuzzyLboxStats:

    def __init__(self, main, sub):
        parser, lexer = main.load()
        self.lexer = lexer
        self.parser = parser
        self.ast = parser.previous_version
        self.treemanager = TreeManager()
        self.treemanager.add_parser(parser, lexer, main.name)
        self.treemanager.option_autolbox_insert = True
        self.langname = main.name

        parser.setup_autolbox(main.name, lexer)
        self.sub = sub

        self.inserted = 0
        self.log = []

    def load_main(self, filename):
        self.filename = filename
        f = open(filename, "r")
        self.content = f.read()
        f.close()
        self.content.replace("\n", "\r")
        self.treemanager.import_file(self.content)
        self.mainexprs = self.find_nonterms_by_name(self.treemanager, self.main_repl_str)
        self.minver = self.treemanager.version

    def reset(self):
        self.parser.reset()
        self.ast = self.parser.previous_version
        self.treemanager = TreeManager()
        self.treemanager.add_parser(self.parser, self.lexer, self.langname)
        self.treemanager.import_file(self.content)
        self.treemanager.option_autolbox_insert = True
        self.mainexprs = self.find_nonterms_by_name(self.treemanager, self.main_repl_str)

    def load_expr(self, filename):
        f = open(filename, "r")
        content = f.read()
        f.close()
        self.replexprs = self.find_expressions(content, self.sub_repl_str)

    def load_expr_from_json(self, filename):
        import json
        with open(filename) as f:
            self.replexprs = json.load(f)

    def set_replace(self, main, sub):
        self.main_repl_str = main
        self.sub_repl_str = sub

    def find_nonterms_by_name(self, tm, name):
        l = []
        bos = tm.get_bos()
        eos = tm.get_eos()
        node = bos.right_sibling()
        while node is not eos:
            if validnonterm(node, name):
                l.append(node)
                node = next_node(node)
                continue
            if node.children:
                node = node.children[0]
            else:
                node = next_node(node)
        return l

    def find_expressions(self, program, expr):
        parser, lexer = self.sub.load()
        treemanager = TreeManager()
        treemanager.add_parser(parser, lexer, self.sub.name)
        treemanager.import_file(program)

        # find all sub expressions
        l = self.find_nonterms_by_name(treemanager, expr)
        return [subtree_to_text(st).rstrip() for st in l]

    def insert_python_expression(self, expr):
        for c in expr:
            self.treemanager.key_normal(c)

    def delete_expr(self, expr):
        # find first term and last term
        # select + delete
        node = expr
        while type(node.symbol) is Nonterminal:
            if node.children:
                node = node.children[0]
            else:
                node = next_node(node)
        first = node
        if isinstance(first, MultiTextNode):
            first = first.children[0]

        node = expr
        while type(node.symbol) is Nonterminal:
            if node.children:
                node = node.children[-1]
            else:
                node = prev_node(node)
        while node.lookup == "<ws>" or node.lookup == "<return>":
            node = node.prev_term
        last = node
        if isinstance(last, MultiTextNode):
            last = last.children[-1]

        if first.deleted or last.deleted:
            return None

        self.treemanager.select_nodes(first, last)
        deleted = self.treemanager.copySelection()
        self.treemanager.deleteSelection()
        return deleted

    def multi_len(self, autos):
        r = []
        for start, end, _, _ in autos:
            l = 0
            while start is not end:
                l += len(start.symbol.name)
                start = start.next_term
            r.append(l)
        return r

    def run(self, main_samples=None, sub_samples=None):
        assert len(self.treemanager.parsers) == 1

        ops = self.main_repl_str, len([subtree_to_text(x) for x in self.mainexprs])
        preversion = self.treemanager.version

        inserted_error = 0
        inserted_valid = 0
        noinsert_error = 0
        noinsert_valid = 0
        noinsert_multi = 0

        # pick random exprs from main
        if not main_samples:
            samplesize = 10
            if len(self.mainexprs) < 10:
                samplesize = len(self.mainexprs)
            sample = random.sample(range(len(self.mainexprs)), samplesize) # store this for repeatability
            exprchoices = [self.mainexprs[i] for i in sample]
            self.main_samples = sample
        else:
            self.main_samples = main_samples
            exprchoices = [self.mainexprs[i] for i in main_samples]

        if not sub_samples:
            # pick random exprs from sub
            sample = random.sample(range(len(self.replexprs)), len(exprchoices))
            replchoices = [self.replexprs[i] for i in sample]
            self.sub_samples = sample
        else:
            self.sub_samples = sub_samples
            replchoices = [self.replexprs[i] for i in sub_samples]

        for i in range(len(exprchoices)):
            e = exprchoices[i]
            if e.get_root() is None:
                continue
            before = len(self.treemanager.parsers)
            deleted = self.delete_expr(e)
            mboxes = None
            ilength = None
            if deleted:
                choice = replchoices[i].strip()
                choice_len = len(choice)
                if debug: print "  Replacing '{}' with '{}':".format(repr(truncate(deleted)), repr(choice))
                start = time.time()
                cursor = self.treemanager.cursor
                if cursor.node.lookup != "<ws>":
                    # Insert a leading space in situations like `return(x)`.
                    choice = " " + choice
                if cursor.node.symbol.name[cursor.pos:] == "" and cursor.node.next_term.lookup != "<ws>":
                    # Insert trailing space if there is none
                    choice = choice + " "
                self.insert_python_expression(choice)
                itime = time.time() - start
                valid = self.parser.last_status
                if before == len(self.treemanager.parsers):
                    if len(self.parser.error_nodes) > 0 and self.parser.error_nodes[0].autobox and len(self.parser.error_nodes[0].autobox) > 1:
                        noinsert_multi += 1
                        result = "No box inserted (Multi)"
                        outcome = "multi"
                        mboxes = self.multi_len(self.parser.error_nodes[0].autobox)
                    elif valid:
                        noinsert_valid += 1
                        result = "No box inserted (Valid)"
                        outcome = "valid"
                    else:
                        noinsert_error += 1
                        result = "No box inserted (Error)"
                        outcome = "error"
                else:
                    result = "Box inserted"
                    innervalid = self.treemanager.parsers[-1][0].last_status
                    self.inserted += 1
                    recent_box = self.treemanager.parsers[-1][0].previous_version.parent
                    lbox_len = self.lbox_length(recent_box)
                    ilength = (lbox_len, choice_len)
                    if valid and innervalid:
                        inserted_valid += 1
                        outcome = "ok"
                    else:
                        inserted_error += 1
                        outcome = "inerr"
                if debug: print "    => {} ({})".format(result, valid)
                nlboxes = len(self.treemanager.parsers)
                self.log.append([self.filename, repr(deleted), repr(choice), outcome, itime, mboxes, ilength, nlboxes])
            else:
                if debug: print "Replacing '{}' with '{}':\n    => Already deleted".format(truncate(subtree_to_text(e)), truncate(choice))
            self.undo(self.minver)
            exprchoices = [self.mainexprs[i] for i in self.main_samples]
        if debug:
            print("Boxes inserted: {}/{}".format(self.inserted, ops))
            print("Valid insertions:", inserted_valid)
            print("Invalid insertions:", inserted_error)
            print("No insertion (valid):", noinsert_valid)
            print("No insertion (error):", noinsert_error)
            print("No insertion (multi):", noinsert_multi)
        return (inserted_valid, inserted_error, noinsert_valid, noinsert_error, noinsert_multi)

    def undo(self, version):
        # reset everything
        self.reset()
        return
        while self.treemanager.version != version:
            before = self.treemanager.version
            self.treemanager.version -= 1
            self.treemanager.recover_version("undo", self.treemanager.version + 1)
            self.treemanager.cursor.load(self.treemanager.version, self.treemanager.lines)
            if before == self.treemanager.version:
                exit("Error")

    def lbox_length(self, root):
        l = []
        node = root.children[0]
        eos = root.children[-1]
        while node is not eos:
            if not node.deleted:
                l.append(node.symbol.name)
            node = node.next_term
        s = "".join(l).strip()
        return len(s)

def run_multi(name, main, sub, folder, ext, exprs, mrepl, srepl=None, config=None):
    if config:
        run_config(name, main, sub, config, exprs, mrepl)
        return
    runcfg = []
    results = []
    log = []
    files = [y for x in os.walk(folder) for y in glob.glob(os.path.join(x[0], ext))]
    if len(files) > MAX_FILES:
        # let's limit files to 200 for now
        files = random.sample(files, MAX_FILES)
    i = 0
    for filename in files:
        c, r, l = run_single(filename, main, sub, exprs, mrepl, srepl)
        if c is None:
            continue
        runcfg.append(c)
        results.append(r)
        log.extend(l)
        i = i + sum(r)
        if i > 1000:
            # abort after 1000 insertions
            break
    with open("{}_run.json".format(name), "w") as f: json.dump(runcfg, f, indent=0)
    with open("{}_log.json".format(name), "w") as f: json.dump(log, f, indent=0)
    print

def run_single(filename, main, sub, exprs, mrepl, srepl, msample=None, ssample=None):
    if debug: print("Runsingle:", filename)
    fuz = FuzzyLboxStats(main, sub)
    fuz.set_replace(mrepl, srepl)
    try:
        fuz.load_main(filename)
        fuz.load_expr_from_json(exprs)
        r = fuz.run(msample, ssample)
    except Exception, e:
        # Errors here point to a bug in Eco, so it's better to just exclude
        # this file from the experiment.
        print(e)
        sys.stdout.write("s")
        sys.stdout.flush()
        return None, None, None
    if r[1] > 0 or r[3] > 0:
        # insert_error and noinsert_error
        sys.stdout.write("x")
        sys.stdout.flush()
    else:
        sys.stdout.write(".")
        sys.stdout.flush()
    config = (filename, fuz.main_samples, fuz.sub_samples)
    return config, r, fuz.log

def run_config(name, main, sub, configdir, exprs, mrepl, srepl=None):
    with open("{}/{}_run.json".format(configdir, name)) as f:
        runcfg = []
        log = []
        config = json.load(f)
        for filename, msample, ssample in config:
            c, r, l = run_single(filename, main, sub, exprs, mrepl, srepl, msample, ssample)
            if c is None:
                continue
            runcfg.append(c)
            log.extend(l)
        with open("{}_run.json".format(name), "w") as f: json.dump(runcfg, f, indent=0)
        with open("{}_log.json".format(name), "w") as f: json.dump(log, f, indent=0)
        print

def create_composition(smain, ssub, mainexpr, gmain, gsub, subexpr, histtok):
    sub = EcoFile(ssub, "grammars/" + gsub, ssub)
    if subexpr:
        sub.name = sub.name + " expr"
        sub.change_start(subexpr)

    main = EcoFile(smain + " + " + ssub, "grammars/" + gmain, smain)
    main.auto_limit_new = histtok
    main.add_alternative(mainexpr, sub)
    lang_dict[main.name] = main
    lang_dict[sub.name] = sub

    return main

if __name__ == "__main__":
    import sys
    import config
    args = sys.argv
    wd = "/home/lukas/research/auto_lbox_experiments/"

    if len(args) < 8:
        print("Missing arguments.\nUsage: python2 fuzzylboxstats.py MAINGRM MAINRULE SUBGRM SUBRULE FILES EXTENSION REPLACMENTS HISTORICTOKEN HEURISTIC [RERUNDIR]")
        exit()

    maingrm = args[1]
    mainrule = args[2]
    subgrm = args[3]
    subrule = args[4]
    files = args[5]
    ext = args[6]
    repl = args[7]
    if args[8] == "True":
        histtok = True
    else:
        histtok = False
    if args[9] == "all":
        config.AUTOLBOX_HEURISTIC_LINE = True
        config.AUTOLBOX_HEURISTIC_HIST = True
        config.AUTOLBOX_HEURISTIC_STACK = True
    elif args[9] == "line":
        config.AUTOLBOX_HEURISTIC_LINE = True
        config.AUTOLBOX_HEURISTIC_HIST = False
        config.AUTOLBOX_HEURISTIC_STACK = False
    elif args[9] == "hist":
        config.AUTOLBOX_HEURISTIC_LINE = False
        config.AUTOLBOX_HEURISTIC_HIST = True
        config.AUTOLBOX_HEURISTIC_STACK = False
    elif args[9] == "stack":
        config.AUTOLBOX_HEURISTIC_LINE = False
        config.AUTOLBOX_HEURISTIC_HIST = False
        config.AUTOLBOX_HEURISTIC_STACK = True

    if len(args) > 10:
        rerunconfig = wd + args[10]
    else:
        rerunconfig = None
    if subrule == "None":
        subrule = None

    comp = create_composition("Main", "Sub", mainrule, maingrm, subgrm, subrule, histtok)
    name = maingrm[:-4] + subgrm[:-4]
    run_multi(name, comp, None, "{}/{}/".format(wd, files), '*.{}'.format(ext), "{}/{}".format(wd, repl), mainrule, subrule, rerunconfig)
