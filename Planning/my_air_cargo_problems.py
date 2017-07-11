from aimacode.logic import PropKB
from aimacode.planning import Action
from aimacode.search import (
    Node, Problem,
)
from aimacode.utils import expr
from lp_utils import (
    FluentState, encode_state, decode_state,
)
from my_planning_graph import PlanningGraph

from functools import lru_cache


class AirCargoProblem(Problem):
    def __init__(self, cargos, planes, airports, initial: FluentState, goal: list):
        """

        :param cargos: list of str
            cargos in the problem
        :param planes: list of str
            planes in the problem
        :param airports: list of str
            airports in the problem
        :param initial: FluentState object
            positive and negative literal fluents (as expr) describing initial state
        :param goal: list of expr
            literal fluents required for goal test
        """
        self.state_map = initial.pos + initial.neg
        self.initial_state_TF = encode_state(initial, self.state_map)
        Problem.__init__(self, self.initial_state_TF, goal=goal)
        self.cargos = cargos
        self.planes = planes
        self.airports = airports
        self.actions_list = self.get_actions()

    def get_actions(self):
        """
        This method creates concrete actions (no variables) for all actions in the problem
        domain action schema and turns them into complete Action objects as defined in the
        aimacode.planning module. It is computationally expensive to call this method directly;
        however, it is called in the constructor and the results cached in the `actions_list` property.

        Returns:
        ----------
        list<Action>
            list of Action objects
        """

        # concrete actions definition: specific literal action that does not include variables as with the schema
        # for example, the action schema 'Load(c, p, a)' can represent the concrete actions 'Load(C1, P1, SFO)'
        # or 'Load(C2, P2, JFK)'.  The actions for the planning problem must be concrete because the problems in
        # forward search and Planning Graphs must use Propositional Logic

        def load_actions():
            """Create all concrete Load actions and return a list
            :return: list of Action objects
            """
            loads = []
            for airport in self.airports:
                for plane in self.planes:
                    for cargo in self.cargos:
                        precond_pos = [expr('At({}, {})'.format(cargo, plane))] \
                                     + [expr('At({}, {})'.format(plane, airport))]
                        precond_neg = []
                        effect_add = [expr('In({}, {})'.format(cargo, plane))]
                        effect_rem = [expr('At({}, {})'.format(cargo, airport))]

                        load = Action(expr('Load({}, {}, {})'.format(cargo, plane, airport)),
                                       [precond_pos, precond_neg],
                                       [effect_add, effect_rem])
                        loads.append(load)
            return loads

        def unload_actions():
            """Create all concrete Unload actions and return a list
            :return: list of Action objects
            """
            unloads = []
            for airport in self.airports:
                for plane in self.planes:
                    for cargo in self.cargos:
                        precond_pos = [expr('In({}, {})'.format(cargo, plane))] \
                                      + [expr('At({}, {})'.format(plane, airport))]
                        precond_neg = []
                        effect_add = [expr('At({}, {})'.format(cargo, airport))]
                        effect_rem = [expr('In({}, {})'.format(cargo, plane))]

                        unload = Action(expr('Unload({}, {}, {})'.format(cargo, plane, airport)),
                                       [precond_pos, precond_neg],
                                       [effect_add, effect_rem])
                        unloads.append(unload)
            return unloads

        def fly_actions():
            """Create all concrete Fly actions and return a list
            :return: list of Action objects
            """
            flys = []
            for fr in self.airports:
                for to in self.airports:
                    if fr != to:
                        for p in self.planes:
                            precond_pos = [expr("At({}, {})".format(p, fr)),
                                           ]
                            precond_neg = []
                            effect_add = [expr("At({}, {})".format(p, to))]
                            effect_rem = [expr("At({}, {})".format(p, fr))]
                            fly = Action(expr("Fly({}, {}, {})".format(p, fr, to)),
                                         [precond_pos, precond_neg],
                                         [effect_add, effect_rem])
                            flys.append(fly)
            return flys

        return load_actions() + unload_actions() + fly_actions()

    def actions(self, state: str) -> list:
        """ Return the actions that can be executed in the given state.

        :param state: str
            state represented as T/F string of mapped fluents (state variables)
            e.g. 'FTTTFF'
        :return: list of Action objects
        """
        possible_actions = []
        kb = PropKB()
        kb.tell(decode_state(state, self.state_map).pos_sentence())
        for action in self.actions_list:
            is_possible = True
            for clause in action.precond_pos:
                if clause not in kb.clauses:
                    is_possible = False
            for clause in action.precond_neg:
                if clause in kb.clauses:
                    is_possible = False
            if is_possible:
                possible_actions.append(action)
        return possible_actions

    def result(self, state: str, action: Action):
        """ Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state).

        :param state: state entering node
        :param action: Action applied
        :return: resulting state after action
        """
        new_state = FluentState([], [])
        old_state = decode_state(state, self.state_map)

        for fluent in old_state.pos:
            if fluent not in action.effect_rem:
                new_state.pos.append(fluent)
        for fluent in action.effect_add:
            if fluent not in new_state.pos:
                new_state.pos.append(fluent)
        for fluent in old_state.neg:
            if fluent not in action.effect_add:
                new_state.neg.append(fluent)
        for fluent in action.effect_rem:
            if fluent not in new_state.neg:
                new_state.neg.append(fluent)

        return encode_state(new_state, self.state_map)

    def goal_test(self, state: str) -> bool:
        """ Test the state to see if goal is reached

        :param state: str representing state
        :return: bool
        """
        kb = PropKB()
        kb.tell(decode_state(state, self.state_map).pos_sentence())
        for clause in self.goal:
            if clause not in kb.clauses:
                return False
        return True

    def h_1(self, node: Node):
        # note that this is not a true heuristic
        h_const = 1
        return h_const

    @lru_cache(maxsize=8192)
    def h_pg_levelsum(self, node: Node):
        """This heuristic uses a planning graph representation of the problem
        state space to estimate the sum of all actions that must be carried
        out from the current state in order to satisfy each individual goal
        condition.
        """
        # requires implemented PlanningGraph class
        pg = PlanningGraph(self, node.state)
        pg_levelsum = pg.h_levelsum()
        return pg_levelsum

    @lru_cache(maxsize=8192)
    def h_ignore_preconditions(self, node: Node):
        """This heuristic estimates the minimum number of actions that must be
        carried out from the current state in order to satisfy all of the goal
        conditions by ignoring the preconditions required for an action to be
        executed.
        """
        # TODO implement (see Russell-Norvig Ed-3 10.2.3  or Russell-Norvig Ed-2 11.2)
        count = 0
        return count

def item_helper(item, count):
    """
    :param item (str): An item in the problem (Cargo, Plane, Airport)
    :param count (int): A count of how many items
    :return (str): The item concatenated with a count
    """
    return [item + str(i) for i in range(1,count)]


def get_combo_helper(a, b, action, one_to_one=True):
    """
    Return all combindation for item a and item b wrapped in the action
    :param a (list): A list of items
    :param b (list): A list of items
    :param action (str): action to wrap a and b in
    :param one_to_one (boolean): Set to returns all combination if false else returns only one to one matching
    :return (list): A list of combinations
    """
    if one_to_one:
        return [action + '(' + x + ', ' + y +')' for x in a for y in b]
    else:
        return [action + '(' + a[i] + ', ' + b[i] + ')' for i in range(len(a))]

def air_cargo_p1() -> AirCargoProblem:
    cargos = ['C1', 'C2']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO']
    pos = [expr('At(C1, SFO)'),
           expr('At(C2, JFK)'),
           expr('At(P1, SFO)'),
           expr('At(P2, JFK)'),
           ]
    neg = [expr('At(C2, SFO)'),
           expr('In(C2, P1)'),
           expr('In(C2, P2)'),
           expr('At(C1, JFK)'),
           expr('In(C1, P1)'),
           expr('In(C1, P2)'),
           expr('At(P1, JFK)'),
           expr('At(P2, SFO)'),
           ]
    init = FluentState(pos, neg)
    goal = [expr('At(C1, JFK)'),
            expr('At(C2, SFO)'),
            ]
    return AirCargoProblem(cargos, planes, airports, init, goal)


def air_cargo_p2() -> AirCargoProblem:
    cargos = item_helper('C', 4)
    planes = item_helper('P', 4)
    airports = ['SFO', 'JFK', 'ATL']

    at_cargo = get_combo_helper(cargos, airports, 'At', False)
    at_planes = get_combo_helper(planes, airports, 'At', False)

    pos = [expr(state) for state in at_cargo + at_planes]

    plane_cargo_neg = get_combo_helper(cargos, planes, 'In')
    plane_airport_neg = list(set(get_combo_helper(planes, airports, 'At')).difference(at_planes))
    cargos_airport_neg = list(set(get_combo_helper(cargos, airports, 'At')).difference(at_cargo))
    neg = [expr(state) for state in  plane_airport_neg + plane_cargo_neg + cargos_airport_neg]

    init = FluentState(pos, neg)
    goal = [expr(state) for state in get_combo_helper(cargos, ['JFK'] + ['SFO']*2, 'At', False)]

    return AirCargoProblem(cargos, planes, airports, init, goal)


def air_cargo_p3() -> AirCargoProblem:
    cargos = item_helper('C', 5)
    planes = item_helper('P', 3)
    airports = ['SFO', 'JFK', 'ATL', 'ORD']

    at_planes = get_combo_helper(planes, airports[:2], 'At', False)
    at_cargo = get_combo_helper(cargos, airports, 'At', False)
    pos = [expr(state) for state in at_planes + at_cargo]

    plane_cargo_neg = get_combo_helper(cargos, planes, 'In')
    plane_airport_neg = list(set(get_combo_helper(planes, airports, 'At')).difference(at_planes))
    cargos_airport_neg = list(set(get_combo_helper(cargos, airports, 'At')).difference(at_cargo))
    neg = [expr(state) for state in plane_airport_neg + plane_cargo_neg + cargos_airport_neg]

    init = FluentState(pos, neg)
    goal = [expr(state) for state in get_combo_helper(cargos, ['JFK', 'SFO', 'JFK', 'SFO'], 'At', False)]

    return AirCargoProblem(cargos, planes, airports, init, goal)
