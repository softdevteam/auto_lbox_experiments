import os, glob

folder = "wordpress/"
ext = "*.php"
for d in os.walk(folder):
    for f in d[2]:
        if os.path.splitext(f)[1] == ".php":
            filename = os.path.join(d[0], f)
            with open(filename, "r") as f:
                content = f.read()
            if content.count("<?php") > 1:
                continue
            with open("phpfiles/{}".format(os.path.basename(filename)), "w") as f:
                f.write(content.replace("<?php", ""))
