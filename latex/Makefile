all: tbl_valid.tex tbl_breakdown.tex benchmark

tbl_valid.tex:
	./maketables.py valid all hist stack line > tbl_valid.tex

tbl_breakdown.tex:
	./maketables.py breakdown all hist stack line > tbl_breakdown.tex

benchmark: tbl_bench_all.tex tbl_bench_hist.tex tbl_bench_stack.tex tbl_bench_line.tex
tbl_bench_all.tex:
	./maketables.py benchmark all > tbl_bench_all.tex
tbl_bench_hist.tex:
	./maketables.py benchmark hist > tbl_bench_hist.tex
tbl_bench_stack.tex:
	./maketables.py benchmark stack > tbl_bench_stack.tex
tbl_bench_line.tex:
	./maketables.py benchmark line > tbl_bench_line.tex

clean:
	rm tbl_valid.tex
	rm tbl_breakdown.tex
	rm tbl_bench_*.tex
	rm experimentstats.tex
