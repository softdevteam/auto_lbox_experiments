RERUNDIR=
HISTOK=True
HEURISTIC=all

all: luastmts.json javastmts.json phpstmts.json sqlstmts.json phpfiles/about.php sqlfiles/99.sql
	cd eco/lib/eco; pypy fuzzylboxstats.py lua ../../../log_limit_on_090419
	cd eco/lib/eco; pypy fuzzylboxstats.py java ../../../log_limit_on_090419
	cd eco/lib/eco; pypy fuzzylboxstats.py php ../../../log_limit_on_090419
	cd eco/lib/eco; pypy fuzzylboxstats.py sql ../../../log_limit_on_090419

	mkdir -p log/
	mv eco/lib/eco/*_log.json log/
	mv eco/lib/eco/*_fail.json log/
	mv eco/lib/eco/*_run.json log/

comp_exprs: java_expr php_expr lua_expr sql_expr
	mkdir -p log_exprs
	mv eco/lib/eco/*.json log_exprs

comp_funcs: java_func php_func lua_func
	mkdir -p log_funcs
	mv eco/lib/eco/*.json log_funcs

# Compose functions

java_func: javastdlib5 phpfuncs.json luafuncs.json
	cd eco/lib/eco; pypy fuzzylboxstats.py java15.eco method_declaration php.eco    class_statement javastdlib5/ java phpfuncs.json $(HISTOK) $(HEURISTIC) $(RERUNDIR)
	cd eco/lib/eco; pypy fuzzylboxstats.py java15.eco method_declaration lua5_3.eco stat            javastdlib5/ java luafuncs.json $(HISTOK) $(HEURISTIC) $(RERUNDIR)

php_func: phpfiles luafuncs.json javafuncs.json
	cd eco/lib/eco; pypy fuzzylboxstats.py php.eco class_statement lua5_3.eco stat               phpfiles/ php luafuncs.json $(HISTOK) $(HEURISTIC) $(RERUNDIR)
	cd eco/lib/eco; pypy fuzzylboxstats.py php.eco class_statement java15.eco method_declaration phpfiles/ php javafuncs.json $(HISTOK) $(HEURISTIC) $(RERUNDIR)

lua_func: lua phpfuncs.json javafuncs.json
	cd eco/lib/eco; pypy fuzzylboxstats.py lua5_3.eco stat php.eco    class_statement    lua/testes lua phpfuncs.json $(HISTOK) $(HEURISTIC) $(RERUNDIR)
	cd eco/lib/eco; pypy fuzzylboxstats.py lua5_3.eco stat java15.eco method_declaration lua/testes lua javafuncs.json $(HISTOK) $(HEURISTIC) $(RERUNDIR)

# Compose expressions

java_expr: javastdlib5 phpexprs.json sqlstmts.json luaexprs.json
	cd eco/lib/eco; pypy fuzzylboxstats.py java15.eco assignment_expression php.eco    expr_without_variable javastdlib5/ java phpexprs.json $(HISTOK) $(HEURISTIC) $(RERUNDIR)
	cd eco/lib/eco; pypy fuzzylboxstats.py java15.eco assignment_expression sqlite.eco None                  javastdlib5/ java sqlstmts.json $(HISTOK) $(HEURISTIC) $(RERUNDIR)
	cd eco/lib/eco; pypy fuzzylboxstats.py java15.eco assignment_expression lua5_3.eco explist               javastdlib5/ java luaexprs.json $(HISTOK) $(HEURISTIC) $(RERUNDIR)

php_expr: phpfiles javaexprs.json sqlstmts.json luaexprs.json
	cd eco/lib/eco; pypy fuzzylboxstats.py php.eco expr_without_variable java15.eco assignment_expression phpfiles/ php javaexprs.json $(HISTOK) $(HEURISTIC) $(RERUNDIR)
	cd eco/lib/eco; pypy fuzzylboxstats.py php.eco expr_without_variable sqlite.eco None                  phpfiles/ php sqlstmts.json $(HISTOK) $(HEURISTIC) $(RERUNDIR)
	cd eco/lib/eco; pypy fuzzylboxstats.py php.eco expr_without_variable lua5_3.eco explist               phpfiles/ php luaexprs.json $(HISTOK) $(HEURISTIC) $(RERUNDIR)

lua_expr: lua javaexprs.json phpexprs.json sqlstmts.json
	cd eco/lib/eco; pypy fuzzylboxstats.py lua5_3.eco explist java15.eco assignment_expression lua/testes lua javaexprs.json $(HISTOK) $(HEURISTIC) $(RERUNDIR)
	cd eco/lib/eco; pypy fuzzylboxstats.py lua5_3.eco explist php.eco    expr_without_variable lua/testes lua phpexprs.json  $(HISTOK) $(HEURISTIC) $(RERUNDIR)
	cd eco/lib/eco; pypy fuzzylboxstats.py lua5_3.eco explist sqlite.eco None                  lua/testes lua sqlstmts.json  $(HISTOK) $(HEURISTIC) $(RERUNDIR)

sql_expr: sqlfiles javaexprs.json phpexprs.json luaexprs.json
	cd eco/lib/eco; pypy fuzzylboxstats.py sqlite.eco expr java15.eco assignment_expression sqlfiles/ sql javaexprs.json $(HISTOK) $(HEURISTIC) $(RERUNDIR)
	cd eco/lib/eco; pypy fuzzylboxstats.py sqlite.eco expr php.eco    expr_without_variable sqlfiles/ sql phpexprs.json  $(HISTOK) $(HEURISTIC) $(RERUNDIR)
	cd eco/lib/eco; pypy fuzzylboxstats.py sqlite.eco expr lua5_3.eco explist               sqlfiles/ sql luaexprs.json  $(HISTOK) $(HEURISTIC) $(RERUNDIR)

# Dependencies

sqlite:
	wget https://www.sqlite.org/src/tarball/sqlite.tar.gz?r=release -O sqlite.tar.gz
	tar xf sqlite.tar.gz

wordpress:
	wget https://wordpress.org/wordpress-4.6.13.tar.gz
	tar xf wordpress-4.6.13.tar.gz

flowblade:
	git clone https://github.com/jliljebl/flowblade.git

eco:
	git clone https://github.com/softdevteam/eco
	cd eco; git checkout lboxstats
	cp extractor.py eco/lib/eco
	cp fuzzylboxstats.py eco/lib/eco

lua:
	git clone https://github.com/lua/lua.git

# Extract expressions, functions, etc.

sqltests.json: sqlite
	python extractsqltests.py

sqlstmts.json: sqltests.json eco
	cp extractsqlstmts.py eco/lib/eco
	cd eco/lib/eco; python2 extractsqlstmts.py ../../../sqltests.json

phpexprs.json: wordpress eco
	cp extractphp.py eco/lib/eco
	cd eco/lib/eco; python2 extractphp.py expressions ../../../phpexprs.json

phpfuncs.json: wordpress eco
	cp extractor.py eco/lib/eco
	cp extractphp.py eco/lib/eco
	cd eco/lib/eco; pypy extractphp.py functions ../../../phpfuncs.json

pythonstmts.json: flowblade eco
	cp extractpython.py eco/lib/eco
	cd eco/lib/eco; python2 extractpython.py ../../../pythonstmts.json

luaexprs.json: lua eco
	cp extractlua.py eco/lib/eco
	cd eco/lib/eco; python2 extractlua.py expressions ../../../luaexprs.json

luafuncs.json: lua eco
	cp extractlua.py eco/lib/eco
	cd eco/lib/eco; python2 extractlua.py functions ../../../luafuncs.json

javaexprs.json: javastdlib5 eco
	cp extractjava.py eco/lib/eco
	cd eco/lib/eco; python2 extractjava.py expressions ../../../javaexprs.json

javafuncs.json: javastdlib5 eco
	cp extractjava.py eco/lib/eco
	cd eco/lib/eco; python2 extractjava.py functions ../../../javafuncs.json

# Extract programs

phpfiles: wordpress
	mkdir phpfiles
	python2 extractphpfiles.py

sqlfiles: sqlstmts.json
	mkdir sqlfiles
	python2 extractsqlfiles.py

clean:
	rm -r sqlite/
	rm -r wordpress
	rm -r lua
	rm -r flowblade
	rm sqlite.tar.gz
	rm wordpress-4.6.13.tar.gz
	rm sqlstmts.json
	rm phpstmts.json
	rm javastmts.json
	rm luastmts.json
	rm -r log
