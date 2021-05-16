def puzzle_to_string(puzzle, sol=None):
    n = puzzle["size"]
    s = puzzle["stars"]
    b = puzzle["regions"]

    #out = "-" + "———" * n + "\n"
    out = "╌" + "╌╌╌" * n + "\n"
    for i in range(0, n):
        out += "│ "
        for j in range(0, n):
            if not sol:
                out += " "
            else:
                if sol[i][j] == 1:
                    out += "*"
                else:
                    out += " "
            if j == n - 1:
                out += "│ "
            else:
                if b[i][j+1] != b[i][j]:
                    out += "║ "
                else:
                    out += "┊ "
                    #out += "│ "
        out += "\n"
        if i < n - 1:
            out += " "
            for j in range(0, n):
                if b[i+1][j] != b[i][j]:
                    out += "═══"
                else:
                    out += "╌╌╌"
                    #out += "———"
        else:
            #out += "-" + "———" * n
            out += "╌" + "╌╌╌" * n + "\n"
        out += "\n"
    return out

def check_adj(sol, i, j, i2, j2):
    if sol[i][j] and sol[i2][j2]:
        return False, f"adjacent cells [{i},{j}] and [{i2},{j2}] both contain stars"
    return True, ""
        
def manual_check(puzzle, sol):
    b = puzzle["regions"]
    n = puzzle["size"]
    s = puzzle["stars"]
    r = max(max(b)) + 1 # number of regions
    region_count = [0] * r

    for i in range(0,n):
        t = sum(sol[i])
        if t != s:
            return False, f"row {i} contains {t} stars instead of {s}" 
        for j in range(0,n):
            region_count[b[i][j]] += sol[i][j]

            # check adjacency right, down and down-right
            if j < n-1:
                corr, msg = check_adj(sol,i,j,i,j+1)
                if not corr:
                    return corr, msg
            if i < n-1:
                corr, msg = check_adj(sol,i,j,i+1,j)
                if not corr:
                    return corr, msg
            if i < n-1 and j < n-1:
                corr,msg = check_adj(sol,i,j,i+1,j+1)
                if not corr:
                    return corr, msg
            
    for k in range(0,r):
        if region_count[k] != s:
            return False, f"region {k} contains {region_count[k]} stars instead of {s}"
    for j in range(0, n):
        t = sum(sol[i][j] for i in range(0,n))
        if t != s:
            return False, f"column {j} contains {t} stars instead of {s}"
    return True, ""

