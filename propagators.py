"""This file will contain different constraint propagators to be used within
   bt_search.

   propagator == a function with the following template
      propagator(csp, newly_instantiated_variable=None)
           ==> returns (True/False, [(Variable, Value), (Variable, Value) ...]

      csp is a CSP object---the propagator can use this to get access
      to the variables and constraints of the problem. The assigned variables
      can be accessed via methods, the values assigned can also be accessed.

      newly_instaniated_variable is an optional argument.
      if newly_instantiated_variable is not None:
          then newly_instantiated_variable is the most
           recently assigned variable of the search.
      else:
          progator is called before any assignments are made
          in which case it must decide what processing to do
           prior to any variables being assigned. SEE BELOW

       The propagator returns True/False and a list of (Variable, Value) pairs.
       Return is False if a deadend has been detected by the propagator.
       in this case bt_search will backtrack
       return is true if we can continue.

      The list of variable values pairs are all of the values
      the propagator pruned (using the variable's prune_value method).
      bt_search NEEDS to know this in order to correctly restore these
      values when it undoes a variable assignment.

      NOTE propagator SHOULD NOT prune a value that has already been
      pruned! Nor should it prune a value twice

      PROPAGATOR called with newly_instantiated_variable = None
      PROCESSING REQUIRED:
        for plain backtracking (where we only check fully instantiated
        constraints)
        we do nothing...return true, []

        for forward checking (where we only check constraints with one
        remaining variable)
        we look for unary constraints of the csp (constraints whose scope
        contains only one variable) and we forward_check these constraints.

        for gac we establish initial GAC by initializing the GAC queue
        with all constaints of the csp


      PROPAGATOR called with newly_instantiated_variable = a variable V
      PROCESSING REQUIRED:
         for plain backtracking we check all constraints with V (see csp method
         get_cons_with_var) that are fully assigned.

         for forward checking we forward check all constraints with V
         that have one unassigned variable left

         for gac we initialize the GAC queue with all constraints containing V.
   """


def prop_BT(csp, newVar=None):
    """Do plain backtracking propagation. That is, do no
    propagation at all. Just check fully instantiated constraints"""

    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:
            vals = []
            for var in c.get_scope():
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []


def prop_FC(csp, newVar=None):
    """Do forward checking. That is check constraints with
       only one uninstantiated variable. Remember to keep
       track of all pruned variable,value pairs and return """

    # book-keeping for pruned variable-value pair for future restoring
    pruned_pairs = []

    # forward check helper function for a single unary constraint C
    def fc_check(C, X):
        """return True if DWO doesn't occur, False otherwise"""
        for d in X.cur_domain():
            # assign to X
            X.assign(d)
            # current assignment to variables in scope C (including X)
            curr_val = []
            for var in C.get_scope():
                curr_val.append(var.get_assigned_value())
            # if assigning d to X falsifies C, prune d
            if not C.check(curr_val):
                X.prune_value(d)
                pruned_pairs.append((X, d))
            # unassign for future looping
            X.unassign()
        # DWO
        if X.cur_domain_size() == 0:
            return False
        return True

    # get constraints
    if not newVar:
        cons = csp.get_all_cons()
    else:
        cons = csp.get_cons_with_var(newVar)
    # forward check for unary constraints
    for c in cons:
        if c.get_n_unasgn() == 1:
            x = c.get_unasgn_vars()[0]
            if not fc_check(c, x):
                return False, pruned_pairs
    return True, pruned_pairs


def prop_GAC(csp, newVar=None):
    """Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue"""

    # book-keeping for pruned variable-value pair for future restoring
    pruned_pairs = []
    # get constraints
    if not newVar:
        gac_queue = csp.get_all_cons()
    else:
        gac_queue = csp.get_cons_with_var(newVar)

    # enforce GAC helper function to prune all GAC inconsistent values
    def gac_enforce(gac_q):
        """return True if DWO doesn't occur, False otherwise"""
        while len(gac_q) > 0:
            con = gac_q.pop(0)
            for var in con.get_scope():
                # check whether there is an assignment A for all other variables in scope(con) s.t. C(A U V=d) is True
                for d in var.cur_domain():
                    if not con.has_support(var, d):
                        var.prune_value(d)
                        pruned_pairs.append((var, d))
                        # DWO
                        if var.cur_domain_size() == 0:
                            gac_q.clear()
                            return False
                        # push all constrains c' s.t. V in scope(c') and c' not in gac_q
                        else:
                            for r_con in csp.get_cons_with_var(var):
                                if r_con not in gac_q:
                                    gac_q = [r_con] + gac_q
        return True

    return gac_enforce(gac_queue), pruned_pairs
