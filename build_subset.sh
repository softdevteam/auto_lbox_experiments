if [ -d "logs" ]; then
    echo "Directory 'logs' already exists. Please rename or delete it."
    exit
fi

mkdir logs

echo "Applying changes to run subset"
cd eco
git apply ../subset.patch
cd ..

echo "===> Running expression benchmarks"

make comp_exprs HEURISTIC=all
mv log_exprs logs/all

make comp_exprs HEURISTIC=hist RERUNDIR=logs/all
mv log_exprs logs/hist

make comp_exprs HEURISTIC=stack RERUNDIR=logs/all
mv log_exprs logs/stack

make comp_exprs HEURISTIC=line RERUNDIR=logs/all
mv log_exprs logs/line

echo "===> Running function benchmarks"

make comp_funcs HEURISTIC=all
mv log_funcs logs/func_all

make comp_funcs HEURISTIC=hist RERUNDIR=logs/func_all
mv log_funcs logs/func_hist

make comp_funcs HEURISTIC=stack RERUNDIR=logs/func_all
mv log_funcs logs/func_stack

make comp_funcs HEURISTIC=line RERUNDIR=logs/func_all
mv log_funcs logs/func_line

echo "===> Analysing results and generating tables"

cd latex
make clean
make

echo "Resetting subset changes"
# Reset changes made by build_subset.sh
cp fuzzylboxstats.py eco/lib/eco
