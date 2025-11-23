#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
from aima.search import Problem
from utils import from_state_to_dict

class NaoMove:
    """
    This class describes the information
    of a single move.
    """
    def __init__(self, duration=None, preconditions=None, postconditions=None):
        self.duration = duration
        self.preconditions = preconditions if preconditions is not None else {}
        self.postconditions = postconditions if postconditions is not None else {}

class NaoProblem(Problem):
    """
    A* problem where:
    - the cost of each step is: duration + lambda_penalty * f(repetitions)
    - the objective is to consume almost all the available time slot
      (remaining_time → ~0) without exceeding it.
    - We do NOT impose a minimum number of moves.
    - We do NOT use entropy: variety emerges from the repetition penalty.
    """

    def __init__(
            self,
            init,
            goal,
            moves,
            previous_moves,
            lambda_penalty=0.5,
            time_tolerance=3.0
        ):
        """
        :param init: initial state (tuple of pairs ('key', value))
                     must contain at least:
                        - 'choreography': tuple(...)
                        - 'standing': bool
                        - 'remaining_time': float
        :param goal: goal state, used only for:
                        - desired 'remaining_time' (e.g., 0.0)
                        - final 'standing' value
        :param moves: dict {move_name: move_object}
                      move_object must have:
                        - duration (float)
                        - preconditions (dict, e.g., {'standing': True})
                        - postconditions (dict, e.g., {'standing': False})
        :param previous_moves: list of moves performed in earlier steps
                               (used to penalize global repetitions).
        :param lambda_penalty: weight of the repetition penalty.
        :param time_tolerance: allowed deviation from the exact time filling.
                               Example: goal.remaining_time = 0, tolerance = 1 → OK if
                               0 <= remaining_time <= 1.
        """
        super().__init__(init, goal)
        self.available_moves = moves
        self.previous_moves = list(previous_moves)
        self.lambda_penalty = lambda_penalty
        self.time_tolerance = time_tolerance

    # ------------------------------------------------------------------
    # Check if a move is usable
    # ------------------------------------------------------------------
    def move_usable(self, state, move_name, move):
        state_dict = from_state_to_dict(state)

        # 1) Cannot exceed the time slot
        if state_dict['remaining_time'] < move.duration:
            return False

        # 2) Logical preconditions (e.g., standing / sitting)
        if 'standing' in move.preconditions:
            if state_dict['standing'] != move.preconditions['standing']:
                return False

        # 3) Hard constraint: avoid repeating the same move twice in a row
        choreography = state_dict['choreography']
        if choreography:
            if move_name == choreography[-1]:
                return False

        return True

    # ------------------------------------------------------------------
    # actions: list of possible moves
    # ------------------------------------------------------------------
    def actions(self, state):
        usable_actions = []
        for move_name, move in self.available_moves.items():
            if self.move_usable(state, move_name, move):
                usable_actions.append(move_name)
        random.shuffle(usable_actions)
        return usable_actions

    # ------------------------------------------------------------------
    # result: next state after applying a move
    # ------------------------------------------------------------------
    def result(self, state, action):
        nao_move = self.available_moves[action]
        state_dict = from_state_to_dict(state)

        # Determine new 'standing' value
        if 'standing' in nao_move.postconditions:
            new_standing = nao_move.postconditions['standing']
        else:
            new_standing = state_dict['standing']

        new_remaining_time = state_dict['remaining_time'] - nao_move.duration

        return (('choreography', (*state_dict['choreography'], action)),
                ('standing', new_standing),
                ('remaining_time', new_remaining_time))

    # ------------------------------------------------------------------
    # path_cost: duration + penalty on GLOBAL repetitions
    # ------------------------------------------------------------------
    def path_cost(self, c, state1, action, state2):
        """
        c = cost accumulated so far
        state1 -> state2 via 'action'

        action cost = duration + lambda_penalty * (count ** 2)

        where:
          - duration = duration of the move
          - count = number of times 'action' already appeared in the global
                    choreography (previous_moves + current choreography).
        """
        nao_move = self.available_moves[action]
        duration = nao_move.duration

        s1_dict = from_state_to_dict(state1)

        # All moves performed so far (previous steps + current choreography)
        history = self.previous_moves + list(s1_dict['choreography'])

        count = history.count(action)

        # Quadratic penalty for stronger discouragement of repetitions
        penalty = self.lambda_penalty * (count ** 2)

        return c + duration + penalty

    # ------------------------------------------------------------------
    # goal_test: check if we filled the time slot (approximately)
    #            and reached the desired final standing
    # ------------------------------------------------------------------
    def goal_test(self, state):
        state_dict = from_state_to_dict(state)
        goal_dict = from_state_to_dict(self.goal)

        goal_remaining_time = goal_dict['remaining_time']  # usually 0.0
        a = goal_remaining_time
        b = goal_remaining_time + self.time_tolerance

        # 1) remaining_time must be within the desired range
        time_constraint = (a <= state_dict['remaining_time'] <= b)

        # 2) final standing must match the goal
        standing_constraint = (state_dict['standing'] == goal_dict['standing'])

        return time_constraint and standing_constraint

    # ------------------------------------------------------------------
    # h: admissible / consistent heuristic
    # ------------------------------------------------------------------
    def h(self, node):
        """
        Heuristic = minimum time we MUST still consume
        to reach the interval [goal_remaining_time, goal_remaining_time + tol].

        If:
            R = current remaining_time,
            R_goal = goal_remaining_time (e.g., 0),
            tol = time_tolerance,
        then we must at least “burn” (R - (R_goal + tol)) if > 0.

        h = max(0, R - (R_goal + tol))

        - This is a lower bound on the time we will still spend.
        - It ignores repetition penalties, so it does NOT overestimate.
        - It is consistent (satisfies the triangle inequality).
        """
        state_dict = from_state_to_dict(node.state)
        goal_dict = from_state_to_dict(self.goal)

        R = state_dict['remaining_time']
        R_goal = goal_dict['remaining_time']
        tol = self.time_tolerance

        return max(0.0, R - (R_goal + tol))
