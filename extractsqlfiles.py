import os, json

with open("sqlstmts.json") as f:
    l = json.load(f)
exprs = ["CHECK", "ON", "LIMIT", "KEY", "HAVING", "FOLLOWING", "PRECEDING", "ELSE", "WHEN", "WHERE",
         "VALUES", "INTO", "DEFAULT", "ATTACH", "DETACH", "COLLATE", "ORDER", "CAST", "ID", "INDEXED"]

i = 0
for s in l:
    for e in exprs:
        if s.find(e) > -1:
            with open("sqlfiles/{}.sql".format(i), "w") as f:
                try:
                    f.write(s)
                except UnicodeEncodeError:
                    continue
    i += 1
