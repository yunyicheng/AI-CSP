# AI-CSP
This is a course project from CSC384: Intro to AI at University of Toronto. In this project, I implemented an AI FunPuzz solver constitutes of two constraint propagators and three different CSP models.

## Introduction
There are two parts to this assignment.

1. Propagators. I implemented two constraint propagators—a Forward Checking constraint propagator, and a Generalized Arc Consistence (GAC) constraint propagator

2. Models. I implemented three different CSP models: two grid-only puzzle models, and one full FunPuzz model (adding cage constraints to grid).

## Files
- cspbase.py. Class definitions for the python objects Constraint, Variable, and BT.
- propagators.py. Code for the implementation of two propagators.
- puzzle csp.py. Code for the CSP models.
- csp sample run.py. This file contains a sample implementation of two CSP problems.
- propagators_test.py. Sample test cases for propagator implementation.
- sample_boards.py. Sample test cases for model generation.

## FunPuzz Formal Description
The FunPuzz puzzle has the following formal description:
- FunPuzz consists of an n × n grid where each cell of the grid can be assigned a number 1 to n. No digit appears more than once in any row or column. Grids range in size from 3×3 to 9×9.
- FunPuzz grids are divided into heavily outlined groups of cells called cages. These cages come with a target and an operation. The numbers in the cells of each cage must produce the target value when combined using the operation.
- For any given cage, the operation is one of addition, subtraction, multiplication or division. Values in a cage can be combined in any order: the first number in a cage may be used to divide the second, for example, or vice versa. Note that the four operators are “left associative” e.g., 16/4/4 is interpreted as (16/4)/4 = 1 rather than 16/(4/4) = 16.
- A puzzle is solved if all empty cells are filled in with an integer from 1 to n and all above constraints are satisfied.
- It is possible for a given cell to not participate in any cage constraints. That is still a valid FunPuzz board.
- For division, we are only concerned with divisions producing integer results throughout the operation.
- An example of a 6×6 grid is shown in Figure 1.
<img width="1196" alt="Screen Shot 2022-02-23 at 10 55 21 PM" src="https://user-images.githubusercontent.com/55462866/155455125-cb130b69-3f83-4fa1-9cc2-1f44af6229f3.png">

## Tasks
### 1. Propagators
Implement Python functions to realize two constraint propagators—a Forward Checking (FC) constraint propagator and a Generalized Arc Consistence (GAC) constraint propagator. These propagators are briefly described below. The files cspbase.py and propagators.py provide the complete input/output specification.

#### Brief Implementation Description
The propagator functions take as input a CSP object csp and (optionally) a Variable newVar representing a newly instantiated Variable, and return a tuple of (bool,list) where bool is False if and only if a dead-end is found, and list is a list of (Variable, value) tuples that have been pruned by the propagator. In all cases, the CSP object is used to access variables and constraints of the problem, via methods found in cspbase.py.

#### Key Functions
- `prop_FC`: A propagator function that propagates according to the FC algorithm that check constraints that have exactly one uninstantiated variable in their scope, and prune appropriately. If newVar is None, forward check all constraints. Otherwise only check constraints containing newVar.

- `prop_GAC`: A propagator function that propagates according to the GAC algorithm, as covered in lecture. If newVar is None, run GAC on all constraints. Otherwise, only check constraints containing newVar.

### 2. Models
Implement three different CSP models using three different constraint types. The three different constraint types are (1) binary not-equal; (2) n-ary all-different; and (3) FunPuzz cage. The three models are (a) binary grid-only FunPuzz; (b) n-ary grid-only FunPuzz; and (c) complete FunPuzz. The file puzzle csp.py provides the complete input/output specification.

#### Brief Implementation Description
The three models take as input a valid FunPuzz grid, which is a list of lists, where the first list has a single element, N, which is the size of each dimension of the board, and each following list represents a cage in the grid. Cell names are encoded as integers in the range 11,...,nn (note that cell indexing starts from 1, e.g. 11 is the cell in the upper left corner) and each inner list contains the numbers of the cells that are included in the corresponding cage, followed by the target value for that cage and the operation (0=’+’, 1=’-’, 2=’/’, 3=’*’). If a list has two elements, the first element corresponds to a cell, and the second one—the target—is the value enforced on that cell.

For example, the model ((3),(11,12,13,6,0),(21,22,31,2,2),....) corresponds to a 3x3 board 1 where
1. cells 11, 12 and 13 must sum to 6, and
2. the result of dividing some permutation of cells 21, 22, and 31 must be 2. That is, (C21/C22)/C23 = 2 or (C21/C23)/C22 = 2, or (C22/C21)/C23 = 2, etc...

All models need to return a CSP object, and a list of lists of Variable objects representing the board. The returned list of lists is used to access the solution. The grid-only models do not need to encode the cage constraints.

#### Key Functions
- `binary_ne_grid`: A model of a FunPuzz grid (without cage constraints) built using only binary not-equal constraints for both the row and column constraints.

- `nary_ad_grid`: A model of a FunPuzz grid (without cage constraints) built using only n-ary all-different constraints for both the row and column constraints.

- `caged_csp_model`: A model built using your choice of (1) binary binary not-equal, or (2) n-ary all-different constraints for the grid, together with (3) FunPuzz cage constraints. That is, you will choose one of the previous two grid models and expand it to include FunPuzz cage constraints.

## Mark Breakdown
Overall: 100% <br/>
Propagators: 50/50<br/>
Binary all-different model: 6/6<br/>
N-ary all-different model: 6/6<br/>
Complete FunPuzz model: 10/10<br/>
