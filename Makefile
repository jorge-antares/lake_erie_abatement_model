setup :
	/bin/sh setup.sh

test :
	./cvxenv/bin/python src/test.py

run :
	./cvxenv/bin/python main.py

setuptest : setup test
