import re, os, json

re_stmt = re.compile("{\s*((DELETE|SELECT|PRAGMA|INSERT|UPDATE|CREATE|DROP|ALERT|BEGIN|ATTACH)([^}]*))\s*}", re.MULTILINE)
result = []

for filename in os.listdir("sqlite/test"):
    if not filename.endswith("test"):
        continue
    with open("sqlite/test/{}".format(filename)) as f:
        source = f.read()
        for m in re_stmt.finditer(source):
            c = m.group(1)
            lines = m.group(1).splitlines()
            if lines:
                # Test if program is valid in SQL
                s = "\n".join(lines)
                s = s.replace("\n", "\r") # Eco grammar compatiblity fix
                result.append("\n".join(lines))

with open("sqltests.json", "w") as output:
    json.dump(result, output, indent=0)
