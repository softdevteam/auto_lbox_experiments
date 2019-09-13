if [ -d "logs" ]; then
    echo "Directory 'logs' already exists. Please rename or delete it."
    exit
fi

if [ ! -d "logs_paper" ]; then
    echo "Directory 'logs_paper' required to rerun original experiment."
    exit
fi

mkdir logs

echo "===> Running expression benchmarks"

make comp_exprs HEURISTIC=all RERUNDIR=logs_paper/all
mv log_exprs logs/all

make comp_exprs HEURISTIC=hist RERUNDIR=logs/all
mv log_exprs logs/hist

make comp_exprs HEURISTIC=stack RERUNDIR=logs/all
mv log_exprs logs/stack

make comp_exprs HEURISTIC=line RERUNDIR=logs/all
mv log_exprs logs/line

echo "===> Running function benchmarks"

make comp_funcs HEURISTIC=all RERUNDIR=logs_paper/func_all
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
