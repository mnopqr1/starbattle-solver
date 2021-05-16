'''Star battle puzzle solver using Z3
   Inspired by minesweeper solver in Sec 3.9 of https://sat-smt.codes/SAT_SMT_by_example.pdf
   and https://github.com/ppmx/sudoku-solver
'''
from utils import *
from pprint import pprint
import time
from z3 import Solver, Int, Or, Sum, sat


def add_constraint(expr, solver, debug=False,msg=""):
    if debug:
        print(msg)
        print(expr)
    solver.add(expr)
    return 1
    
def solve(puzzle, debug=False):
    b = puzzle["regions"]
    n = puzzle["size"]
    st = puzzle["stars"]
    s = Solver()

    # a variable for every cell, plus a border buffer
    # TODO: remove the (left and top) buffer, it's no longer needed
    cells=[[ Int(f'r%d_c%d' % (i,j)) for j in range(0,n+1) ] for i in range(0,n+1) ]

    nc = 0 # number of constraints counter
    
    for row in range(1, n+1):
        for col in range(1, n+1):
            
            expr = Or(cells[row][col] == 0, cells[row][col] == 1)
            nc += add_constraint(Or(cells[row][col] == 0, cells[row][col] == 1),
                                 solver=s, debug=debug, msg=f"* Handling cell {row, col}, value must be 0 or 1")

            if row < n:
                nc += add_constraint(Or(cells[row][col] == 0, cells[row+1][col] == 0),
                                     solver=s, debug=debug, msg="  o No adjacent stars, to below")
                
            if col < n:
                nc += add_constraint(Or(cells[row][col] == 0, cells[row][col+1] == 0),
                                     solver=s, debug=debug, msg="  o No adjacent stars, to the right")
                
            if row < n and col < n:
                nc += add_constraint(Or(cells[row][col] == 0, cells[row+1][col+1] == 0),
                                     solver=s, debug=debug, msg="  o No adjacent stars, to the right-below")


        this_row = [cells[row][col] for col in range(1,n+1)]
        nc += add_constraint(Sum(*this_row) == st,
                             solver=s, debug=debug, msg=f"* {st} stars in row {row}")

    for col in range(1, n+1):
        this_col = [cells[row][col] for row in range(1,n+1)]
        nc += add_constraint(Sum(*this_col) == st,
                             solver=s, debug=debug, msg=f"* {st} stars in column {col}")

    for reg in range(0, max(max(b)) + 1):
        this_region = []
        for row in range(1,n+1):
            for col in range(1,n+1):
                if b[row-1][col-1] == reg:
                    this_region += [cells[row][col]]
        nc += add_constraint(Sum(*this_region) == st,
                             solver=s, debug=debug, msg=f"* {st} stars in region {reg}")

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


