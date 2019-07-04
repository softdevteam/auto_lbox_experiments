
# php files + loc
PHPFILES=$(cd ../phpfiles; ls -1 | wc -l | xargs printf "%'d")
PHPLOC=$(find ../phpfiles/ -name '*.php' | xargs wc -l | grep total | tr -d \[:alpha:\] | tr -d \[:space:\] | xargs printf "%'d")
# java files + loc
JAVAFILES=$(cd ../javastdlib5; find . -name "*.java" | wc -l | xargs printf "%'d")
JAVALOC=$(find ../javastdlib5/ -name '*.java' | xargs wc -l | grep "total" | tr -d \[:alpha:\] | paste -sd+ | bc | xargs printf "%'d")
# lua files + loc
LUAFILES=$(cd ../lua/testes/; find . -name "*.lua" | wc -l | xargs printf "%'d")
LUALOC=$(find ../lua/testes/ -name '*.lua' | xargs wc -l | grep "total" | tr -d \[:alpha:\] | paste -sd+ | bc | xargs printf "%'d")
# sqlfiles + test + loc
SQLFILES=$(cd ../sqlite/test/; find . -name "*.test" | wc -l | xargs printf "%'d")
SQLTESTS=$(cd ../sqlfiles/; find . -name "*.sql" | wc -l | xargs printf "%'d")
SQLLOC=$(find ../sqlfiles/ -name '*.sql' | xargs sed s/\\r/\\n/g | wc -l | xargs printf "%'d")

# php exprs + funcs
PHPFUNCS=$(cat ../phpfuncs.json | sed 2d | wc -l | xargs printf "%'d")
PHPEXPRS=$(cat ../phpexprs.json | sed 2d | wc -l | xargs printf "%'d")
# java exprs + funcs
JAVAFUNCS=$(cat ../javafuncs.json | sed 2d | wc -l | xargs printf "%'d")
JAVAEXPRS=$(cat ../javaexprs.json | sed 2d | wc -l | xargs printf "%'d")
# lua exprs + funcs
LUAFUNCS=$(cat ../luafuncs.json | sed 2d | wc -l | xargs printf "%'d")
LUAEXPRS=$(cat ../luaexprs.json | sed 2d | wc -l | xargs printf "%'d")
# sql statements
SQLSTMTS=$(cat ../sqlstmts.json | sed 2d | wc -l | xargs printf "%'d")

echo "\\newcommand{\\corpusphpfiles}{$PHPFILES\\xspace}"
echo "\\newcommand{\\corpusphploc}{$PHPLOC\\xspace}"
echo "\\newcommand{\\corpusjavafiles}{$JAVAFILES\\xspace}"
echo "\\newcommand{\\corpusjavaloc}{$JAVALOC\\xspace}"
echo "\\newcommand{\\corpusluafiles}{$LUAFILES\\xspace}"
echo "\\newcommand{\\corpuslualoc}{$LUALOC\\xspace}"
echo "\\newcommand{\\corpussqlfiles}{$SQLFILES\\xspace}"
echo "\\newcommand{\\corpussqltests}{$SQLTESTS\\xspace}"
echo "\\newcommand{\\corpussqlloc}{$SQLLOC\\xspace}"
echo "\\newcommand{\\corpusphpexprs}{$PHPEXPRS\\xspace}"
echo "\\newcommand{\\corpusphpfuncs}{$PHPFUNCS\\xspace}"
echo "\\newcommand{\\corpusjavaexprs}{$JAVAEXPRS\\xspace}"
echo "\\newcommand{\\corpusjavafuncs}{$JAVAFUNCS\\xspace}"
echo "\\newcommand{\\corpusluaexprs}{$LUAEXPRS\\xspace}"
echo "\\newcommand{\\corpusluafuncs}{$LUAFUNCS\\xspace}"
echo "\\newcommand{\\corpussqlstmts}{$SQLSTMTS\\xspace}"
