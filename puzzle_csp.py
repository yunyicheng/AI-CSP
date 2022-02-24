"""
All models need to return a CSP object, and a list of lists of Variable objects
representing the board. The returned list of lists is used to access the
solution.

For example, after these three lines of code

    csp, var_array = caged_csp_model(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the FunPuzz puzzle.

The grid-only models do not need to encode the cage constraints.

1. binary_ne_grid (worth 10/100 marks)
    - A model of a FunPuzz grid (without cage constraints) built using only
      binary not-equal constraints for both the row and column constraints.

2. nary_ad_grid (worth 10/100 marks)
    - A model of a FunPuzz grid (without cage constraints) built using only n-ary
      all-different constraints for both the row and column constraints.

3. caged_csp_model (worth 25/100 marks)
    - A model built using your choice of (1) binary binary not-equal, or (2)
      n-ary all-different constraints for the grid.
    - Together with FunPuzz cage constraints.
"""

from cspbase import *
import itertools


def preprocessing(fpuzz_grid):
    # initializing dimension and domain
    dimension = fpuzz_grid[0][0]
    domain = [i + 1 for i in range(dimension)]

    # check for filled variables
    cages = fpuzz_grid[1:]
    filled = {}
    for cage in cages:
        if len(cage) == 2:
            cell = cage[0]
            target = cage[1]
            i, j = cell // 10, cell % 10
            filled[(i, j)] = target

    # initializing board with variables,
    # for value-enforced variables, its domain is enforced; otherwise domain is [1, ..., dimension]
    board = []
    variables = []
    for i in range(1, dimension + 1):
        curr_row = []
        for j in range(1, dimension + 1):
            if (i, j) in filled.keys():
                var = Variable(name='{}{}'.format(i, j), domain=[filled[(i, j)]])
            else:
                var = Variable(name='{}{}'.format(i, j), domain=domain)
            curr_row.append(var)
            variables.append(var)
        board.append(curr_row)
    return dimension, domain, board, variables


# helper function for generating binary not-equal constrains
def binary_ne_generator(matrix, domain):
    """return a list of all binary not equal constraints"""
    all_constraints = []
    for row in matrix:
        for i in range(0, len(row)):
            for j in range(i + 1, len(row)):
                # create constraint by adding all satisfying tuples
                sat_tuples = []
                for tup in itertools.product(domain, repeat=2):
                    if tup[0] != tup[1]:
                        sat_tuples.append(tup)
                constraint = Constraint(name="bi_ne({}, {})".format(i, j), scope=[row[i], row[j]])
                constraint.add_satisfying_tuples(sat_tuples)
                all_constraints.append(constraint)
    return all_constraints


def binary_ne_grid(fpuzz_grid):
    """A model of a FunPuzz grid (without cage constraints) built using
    only binary not-equal constraints for both the row and column constraints."""

    # initializing dimension, domain, empty board, and variables
    dimension, domain, board, variables = preprocessing(fpuzz_grid)
    # adding row binary ne constraints
    row_bi_ne = binary_ne_generator(matrix=board, domain=domain)
    # adding col binary ne constraints by taking transpose of board matrix
    # and pass it to the same constraint generator function
    zipped_rows = zip(*board)
    board_t = [list(row) for row in zipped_rows]
    col_bi_ne = binary_ne_generator(matrix=board_t, domain=domain)
    # combining all the constraints
    constraints = row_bi_ne + col_bi_ne
    # initialize csp
    csp = CSP("binary_ne_grid_model", variables)
    for con in constraints:
        csp.add_constraint(con)
    return csp, board


# helper function for generating n-ary all-diff constrains
def nary_alldiff_generator(matrix, domain):
    """return a list of nary all-diff constraints"""
    all_constraints = []
    # create constraint by adding all satisfying tuples
    for row_i in range(len(matrix)):
        row_vars = [var for var in matrix[row_i]]
        sat_tuples = []
        for tup in itertools.product(domain, repeat=len(domain)):
            if len(tup) == len(set(tup)):
                sat_tuples.append(tup)
        constraint = Constraint(name="all_diff_row{}".format(row_i), scope=row_vars)
        constraint.add_satisfying_tuples(sat_tuples)
        all_constraints.append(constraint)
    return all_constraints


def nary_ad_grid(fpuzz_grid):
    """A model of a FunPuzz grid (without cage constraints) built using
    only n-ary all-different constraints for both the row and column constraints."""

    # initializing dimension, domain, empty board, and variables
    dimension, domain, board, variables = preprocessing(fpuzz_grid)
    # adding row n-ary all-diff constraints
    row_nary_alldiff = nary_alldiff_generator(matrix=board, domain=domain)
    # adding col n-ary all-diff constraints by taking transpose of board matrix
    # and pass it to the same constraint generator function
    zipped_rows = zip(*board)
    board_t = [list(row) for row in zipped_rows]
    col_nary_alldiff = nary_alldiff_generator(matrix=board_t, domain=domain)
    # combining all the constraints
    constraints = row_nary_alldiff + col_nary_alldiff
    # initialize csp
    csp = CSP("nary_ad_grid_model", variables)
    for con in constraints:
        csp.add_constraint(con)
    return csp, board


# helper function for checking whether there exist a satisfying permutation for '-' and '/'
def exist_sat_per(tup, op, target):
    """return True if there exists a satisfying permutation and False otherwise"""

    lst = [item for item in tup]
    flag = False
    for per in itertools.permutations(lst, len(lst)):
        result = per[0]
        if op == 1:
            for i in range(1, len(per)):
                result -= per[i]
        else:
            for i in range(1, len(per)):
                result /= per[i]
        if result == target:
            flag = True
    return flag


# helper function for generating cage constraints
def fp_cage_generator(matrix, domain, fpuzz_grid):
    """return list of all cage constraints"""

    # initialization
    all_constraints = []
    cages = fpuzz_grid[1:]
    for cage_index in range(len(cages)):
        cage = cages[cage_index]
        vars_lst = []
        sat_tuples = []
        # special case: cage list only has two element: cell value enforcement
        if len(cage) == 2:
            cell = cage[0]
            target = cage[1]
            i, j = (cell // 10) - 1, (cell % 10) - 1
            vars_lst.append(matrix[i][j])
            constraint = Constraint("cage{}".format(cage_index), vars_lst)
            sat_tuples.append(tuple([target]))
            constraint.add_satisfying_tuples(sat_tuples)
            all_constraints.append(constraint)
            continue
        # normal case where list has >= 4 elements
        for grid in cage[:-2]:
            i, j = (grid // 10) - 1, (grid % 10) - 1
            vars_lst.append(matrix[i][j])
        op = cage[-1]
        target = cage[-2]
        for tup in itertools.product(domain, repeat=len(vars_lst)):
            # operation: +
            if op == 0:
                result = sum(list(tup))
                if result == target:
                    sat_tuples.append(tup)
            # operation: - & /
            elif op == 1 or op == 2:
                if exist_sat_per(tup, op, target):
                    sat_tuples.append(tup)
            # operation: *
            else:
                result = tup[0]
                for i in range(1, len(tup)):
                    result *= tup[i]
                if result == target:
                    sat_tuples.append(tup)
        constraint = Constraint("cage{}".format(cage_index), vars_lst)
        constraint.add_satisfying_tuples(sat_tuples)
        all_constraints.append(constraint)
    return all_constraints


def caged_csp_model(fpuzz_grid):
    """A model built using binary ne constraints for the grid, together with FunPuzz cage constraints."""

    # initializing dimension, domain, empty board, and variables
    dimension, domain, board, variables = preprocessing(fpuzz_grid)
    # adding row binary ne constraints
    row_bi_ne = binary_ne_generator(matrix=board, domain=domain)
    # adding col binary ne constraints by taking transpose of board matrix
    # and pass it to the same constraint generator function
    zipped_rows = zip(*board)
    board_t = [list(row) for row in zipped_rows]
    col_bi_ne = binary_ne_generator(matrix=board_t, domain=domain)
    # adding FunPuzz cage constraints
    fp_cage = fp_cage_generator(board, domain, fpuzz_grid)
    # combining all the constraints
    constraints = row_bi_ne + col_bi_ne + fp_cage
    # initialize csp
    csp = CSP("caged_csp_model", variables)
    for con in constraints:
        csp.add_constraint(con)
    return csp, board
    