#!/usr/bin/env python2
import os, sys
import json

bench_names = {
    "java15lua5_3": "JavaLua",
    "java15php": "JavaPHP",
    "java15sqlite": "JavaSQL",
    "lua5_3java15": "LuaJava",
    "lua5_3php": "LuaPHP",
    "lua5_3sqlite": "LuaSQL",
    "phplua5_3": "PHPLua",
    "phpjava15": "PHPJava",
    "phpsqlite": "PHPSQL",
    "sqlitejava15": "SQLJava",
    "sqlitelua5_3": "SQLLua",
    "sqlitephp": "SQLPHP",
}

heu_names = {
    "all": "All",
    "hist": "Parse tree",
    "stack": "Stack",
    "line": "Line",
}

EXPERIMENT_DIR = "../logs_paper/"

class TableMaker:

    def __init__(self, folders):
        self.makros = []
        self.corpus = {}
        self.inslen = {}
        self.get_benchmarks(folders[0])
        rows = []
        for folder in folders:
            data, corpus = self.parse(folder)
            inslen = self.parse_length(folder)
            self.corpus[folder] = corpus
            rows.append(self.make_row(folder, data))
        table = self.make_table(rows)
        print(table)
        # add makros
        with open("experimentstats.tex", "a") as f:
            f.write("\n".join(self.makros))
            f.write("\n")

    def parse(self, heuristic):
        data = {}
        corpus = {}
        for c in self.benchmarks:
            totale = totalf = 0
            # collect data from expression benchmarks
            data[c], totale = self.collect_stats_from_faillog("{}/{}/{}".format(EXPERIMENT_DIR, heuristic, c))
            if os.path.isdir("{}/func_{}/".format(EXPERIMENT_DIR, heuristic)):
                # add data from function benchmarks
                funcdata, totalf = self.collect_stats_from_faillog("{}/func_{}/{}".format(EXPERIMENT_DIR, heuristic, c))
                for k in funcdata:
                    data[c][k] = (data[c][k] + funcdata[k]) / 2
            corpus[c] = totale + totalf
        return data, corpus

    def parse_length(self, heuristic):
        data = {}
        for c in self.benchmarks:
            clen = c.replace("log.json", "len.json")
            with open("{}/{}/{}".format(EXPERIMENT_DIR, heuristic, clen)) as f:
                data[c] = json.load(f)
        return data

    def collect_stats_from_faillog(self, filename):
        filename = filename.replace("log.json", "fail.json")
        if not os.path.exists(filename):
            return {}, 0
        d = {
            "valid": 0,
            "invalid": 0,
            "novalid": 0,
            "noerror": 0,
            "nomulti": 0,
            "validsame": 0,
            "invalidsame": 0,
            "validdiff": 0,
            "invaliddiff": 0

        }
        with open(filename) as f:
            insdata = json.load(f)
        with open(filename.replace("fail.json", "len.json")) as f2:
            inslen = json.load(f2)

        #print(filename)
        for i, entry in enumerate(insdata):
            if entry[0] == "ok":
                d["valid"] += 1
                if inslen[i][0] == inslen[i][1]:
                    d["validsame"] += 1
                else:
                    d["validdiff"] += 1
            elif entry[0] == "inerr":
                d["invalid"] += 1
                if inslen[i][0] == inslen[i][1]:
                    d["invalidsame"] += 1
                else:
                    d["invaliddiff"] += 1
            elif entry[0] == "multi":
                d["nomulti"] += 1
            elif entry[0] == "error":
                d["noerror"] += 1
            elif entry[0] == "valid":
                d["novalid"] += 1

        assert len(insdata) == len(inslen)
        total = len(insdata)
        if total > 0:
            for key in d:
                d[key] = float(d[key]) / total
        return d, total

    def collect_stats(self, filename):
        if not os.path.exists(filename):
            return {}, 0
        d = {}
        with open(filename) as f:
            l = json.load(f)
            with open(filename.replace("log.json", "len.json")) as f2:
                l2 = json.load(f2)
            total   = sum([sum(x) for x in l])
            valid   = sum([x[0] for x in l])
            invalid = sum([x[1] for x in l])
            novalid = sum([x[2] for x in l])
            noerror = sum([x[3] for x in l])
            nomulti = sum([x[4] for x in l])
            # collect lengths for valid/invalid
            validsame = validdiff = invalidsame = invaliddiff = 0
            for i in xrange(len(l)):
                if l2[i][0] == l2[i][1]:
                    validsame += l[i][0]
                    invalidsame += l[i][1]
                else:
                    validsame += l[i][0]
                    invaliddiff += l[i][1]
            assert validsame + validdiff == valid
            assert invalidsame + invaliddiff == invalid
            assert invalidsame == 0
            d["valid"]   = float(valid)   / total
            d["invalid"] = float(invalid) / total
            d["novalid"] = float(novalid) / total
            d["noerror"] = float(noerror) / total
            d["nomulti"] = float(nomulti) / total
            d["validsame"]   = float(validsame)   / total
            d["invalidsame"] = float(invalidsame) / total
            d["validdiff"]   = float(validdiff)   / total
            d["invaliddiff"] = float(invaliddiff) / total
        return d, total

    def get_benchmarks(self, heuristic):
        l = []
        for _, _, files in os.walk("{}/{}".format(EXPERIMENT_DIR, heuristic)):
            for f in files:
                if f.endswith("_log.json"):
                    l.append(f)
        l.sort()
        self.benchmarks = l

    def cell_alignment(self):
        raise NotImplemented

    def make_row(self):
        raise NotImplemented

    def make_header(self):
        raise NotImplemented

    def make_table(self, rows):
        cellalign = self.cell_alignment()
        header = self.make_header()
        s = """\\begin{{tabular}}{{l {cellalign}}}
    \\toprule
    {header} \\\\
    \\midrule
{rows}
    \\bottomrule
\end{{tabular}}
        """.format(cellalign=cellalign, header=header, rows = "\n".join(rows))
        return s

class Valid(TableMaker):

    def make_row(self, folder, data):
        l = []
        overall = 0
        for comp in self.benchmarks:
            wanted = data[comp]["valid"] + data[comp]["novalid"] + data[comp]["nomulti"]
            overall += wanted
            l.append("{:.1f}\%".format(wanted * 100))
            self.add_makro(folder, comp, l[-1])
        l.append("{:.1f}\%".format(overall / len(l) * 100))
        self.add_makro(folder, "overall", l[-1])
        return "    {} & {} \\\\".format(heu_names[folder], " & ".join(l))

    def cell_alignment(self):
        return " c " * (len(self.benchmarks) + 1)

    def make_header(self):
        bs = ["\\rotatebox{{65}}{{{}}}".format(bench_names[b[:-9]]) for b in self.benchmarks] # remove '_log.json'
        return "    & {} & \\rotatebox{{65}}{{Overall}}".format(" & ".join(bs))

    def make_totalrow(self):
        overall = sum(self.corpus["all"].values())
        self.makros.append("\\newcommand{{\\totalinsertions}}{{{:,}\\xspace}}".format(overall))
        return "\# Tests & {} & {:,} \\\\".format(" & ".join([str(self.corpus["all"][b]) for b in self.benchmarks]), overall)

    def make_table(self, rows):
        cellalign = self.cell_alignment()
        header = self.make_header()
        totals = self.make_totalrow()
        s = """\\begin{{tabular}}{{l {cellalign}}}
    \\toprule
    {header} \\\\
    \\midrule
    {totals}
    \\midrule
{rows}
    \\bottomrule
\end{{tabular}}
        """.format(cellalign=cellalign, header=header, totals=totals, rows = "\n".join(rows))
        return s

    def add_makro(self, heu, bench, value):
        if bench != "overall":
            bench = bench_names[bench[:-9]].lower()
        self.makros.append("\\newcommand{{\\valid{heu}{bench}}}{{{value}\\xspace}}".format(heu=heu, bench=bench, value=value))

class Breakdown(TableMaker):

    def make_row(self, folder, data):
        l = []
        for x in ["validsame", "validdiff", "invaliddiff", "novalid", "noerror", "nomulti"]:
            total = 0
            for bench in data:
                total += data[bench][x]
            l.append("{:.1f}\%".format(total / len(data) * 100))
            self.add_makro(folder, x, l[-1])
        return "    {} & {} \\\\".format(heu_names[folder], " & ".join(l))

    def cell_alignment(self):
        return " c " * 7

    def make_header(self):
        l = []
        for label in ["Complete insertion\\\\(No errors)", "Partial insertion\\\\(No errors)", "Partial insertion\\\\(Errors)", "No insertion\\\\(Valid)", "No insertion\\\\(Errors)", "No insertion\\\\(Multi)"]:
            l.append("\multicolumn{1}{p{2cm}}{\centering %s}" % label)
        return "    & {}".format(" & ".join(l))

    def add_makro(self, heu, outcome, value):
        self.makros.append("\\newcommand{{\\breakdown{heu}{outcome}}}{{{value}\\xspace}}".format(heu=heu, outcome=outcome, value=value))

class BenchmarkBreakdown(TableMaker):

    def __init__(self, folder):
        self.get_benchmarks(folder)
        data, _ = self.parse(folder)
        rows = self.make_rows(data)
        table = self.make_table(rows)
        print(table)

    def make_rows(self, data):
        rows = []
        for bench in self.benchmarks:
            l = []
            for x in ["validsame", "validdiff", "invaliddiff", "novalid", "noerror", "nomulti"]:
                l.append("{:.1f}\%".format(data[bench][x] * 100))
            rows.append("    {} & {} \\\\".format(bench_names[bench[:-9]], " & ".join(l)))
        return rows

    def cell_alignment(self):
        return " c " * 7

    def make_header(self):
        l = []
        for label in ["Complete insertion\\\\(No errors)", "Partial insertion\\\\(No errors)", "Partial insertion\\\\(Errors)", "No insertion\\\\(Valid)", "No insertion\\\\(Errors)", "No insertion\\\\(Multi)"]:
            l.append("\multicolumn{1}{p{2cm}}{\centering %s}" % label)
        return "    & {}".format(" & ".join(l))

if __name__ == "__main__":
    tabletype = sys.argv[1]
    if tabletype == "valid":
        Valid(sys.argv[2:])
    elif tabletype == "breakdown":
        Breakdown(sys.argv[2:])
    elif tabletype == "benchmark":
        BenchmarkBreakdown(sys.argv[2])
