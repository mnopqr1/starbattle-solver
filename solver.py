'''Star battle puzzle solver using Z3
   Inspired by minesweeper solver in Sec 3.9 of https://sat-smt.codes/SAT_SMT_by_example.pdf
   and https://github.com/ppmx/sudoku-solver
'''
from utils import *
from pprint import pprint
import time
from z3 import Solver, Int, Or, Sum, sat

def solve(puzzle, debug=False):
    b = puzzle["regions"]
    n = puzzle["size"]
    st = puzzle["stars"]
    s = Solver()

    # a variable for every cell, plus a border buffer
    # TODO: remove the (left and top) buffer, it's no longer needed
    cells=[[ Int(f'r%d_c%d' % (i,j)) for j in range(0,n+1) ] for i in range(0,n+1) ]


    nc = 0 # number of constraints counter
    if debug:
        print("%%%%%%% PER CELL CONDITIONS %%%%%%")

    for row in range(1, n+1):
        for col in range(1, n+1):
            if debug:
                print(f"Handling cell {row, col}")
                print("Value must be 0 or 1:")
            expr = Or(cells[row][col] == 0, cells[row][col] == 1)
            if debug:
                print(expr)
            s.add(expr)
            nc += 1

            if debug:
                print("No adjacent stars")
            if row < n:
                expr = Or(cells[row][col] == 0, cells[row+1][col] == 0)
                if debug:
                    print(expr)
                s.add(expr)
                nc += 1
            if col < n:
                expr = Or(cells[row][col] == 0, cells[row][col+1] == 0)
                if debug:
                    print(expr)
                s.add(expr)
                nc += 1
            if row < n and col < n:
                expr = Or(cells[row][col] == 0, cells[row+1][col+1] == 0)
                if debug:
                    print(expr)
                s.add(expr)
                nc += 1
            if debug:
                print()

        # stars per row
        this_row = [cells[row][col] for col in range(1,n+1)]
        expr = Sum(*this_row) == st
        if debug:
            print(f"Stars per row {row}:")
            print(expr)
        s.add(expr)
        nc += 1

    if debug:
        print("\n%%%%% STARS PER COLUMN %%%%")
    for col in range(1, n+1):
        # stars per column
        this_col = [cells[row][col] for row in range(1,n+1)]
        expr = Sum(*this_col) == st
        s.add(expr)
        if debug:
            print(expr)

    if debug:
        print("\n%%%%% STARS PER REGION %%%%")
    for reg in range(0, max(max(b)) + 1):
        this_region = []
        for row in range(1,n+1):
            for col in range(1,n+1):
                if b[row-1][col-1] == reg:
                    this_region += [cells[row][col]]
                    expr = Sum(*this_region) == st
        if debug:
            print(expr)
        s.add(expr)
        nc += 1

    # SOLVING
    print(f"Asking Z3 to solve {nc} integer constraints in {n * n} variables..")
    
    if s.check() != sat:
        raise Exception("Z3 says the puzzle is unsolvable.")

    model = s.model()
    sol = []
    for row in range(1, n+1):
        this_row = [0] * n
        for col in range(1,n+1):
            this_row[col - 1] = int(model.evaluate(cells[row][col]).as_string())
        sol += [this_row]
    return sol


def main(puzzle):
    n = puzzle["size"]
    s = puzzle["stars"]
    
    print(f"Solving the following {s}-star {n} * {n} puzzle:")
    #pprint(puzzle["regions"])
    print(puzzle_to_string(puzzle))
    
    print("---------------------")
    start = time.time()
    sol = solve(puzzle, debug=False)
    end = time.time()
    print("---------------------")
    print(f"Solution found by Z3 after {end - start} secs:")
    print(puzzle_to_string(puzzle,sol))
    #pprint(sol)
    print("--------------------")
    print("Performing manual Python check of solution:")
    res, msg = manual_check(puzzle, sol)
    if res:
        print("Check passed")
    else:
        print("Check failed")
        print(msg)


from sample_puzzles import sample_puzzles
main(sample_puzzles[3])


