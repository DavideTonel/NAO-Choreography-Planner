#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import random
from aima.search import astar_search
from nao_problem import NaoProblem, NaoMove
from utils import *
from info.statistics import *

# ----------------------------
# Tunable global parameters
# ----------------------------
MAX_DURATION = 120.0           # Exhibition maximum duration (in seconds)
LAMBDA_PENALTY = 0.9           # How much we penalize move repetitions
TIME_TOLERANCE = 2.3           # Accepted leftover time in each step
MIN_INTERMEDIATE_MOVES = 5     # Global constraint: at least this many intermediate moves


def main(robot_ip, port):
    """
    Plan and (optionally) execute a dance choreography for NAO.

    The choreography is built by:
      - Fixing a starting position and a list of mandatory positions.
      - Splitting the total available time into steps between consecutive mandatory positions.
      - For each step, planning a sequence of intermediate moves with A* that:
          * respects standing/lying constraints;
          * fills almost all the time slot without exceeding it;
          * penalizes repetitions through the cost function.
    """

    # ----------------------------
    # Available moves (intermediate)
    # ----------------------------
    moves = {
        '1-Rotation_handgun_object': NaoMove(3.2,   None,  None),
        '4-Arms_opening':            NaoMove(10,    {'standing': True},  {'standing': True}),
        '5-Union_arms':              NaoMove(7.08,  None,  None),
        '7-Move_forward':            NaoMove(3.1,   {'standing': True},  {'standing': True}),
        '8-Move_backward':           NaoMove(3.1,   {'standing': True},  {'standing': True}),
        '9-Diagonal_left':           NaoMove(2.82,   {'standing': True},  {'standing': True}),
        '10-Diagonal_right':         NaoMove(2.42,  {'standing': True},  {'standing': True}),
        'BlowKisses':                NaoMove(5.27,  None,  None),
        'AirGuitar':                 NaoMove(4.18,  {'standing': True},  {'standing': True}),
        'DanceMove':                 NaoMove(6.16,  {'standing': True},  {'standing': True}),
        'Rhythm':                    NaoMove(3.61,  {'standing': True},  {'standing': True}),
        'SprinklerL':                NaoMove(4.14,  {'standing': True},  {'standing': True}),
        'SprinklerR':                NaoMove(4.17,  {'standing': True},  {'standing': True}),
        'StandUp':                   NaoMove(9.11,  {'standing': False}, {'standing': True}),
        'Wave':                      NaoMove(3.72,  None, None),
        'Glory':                     NaoMove(3.44,  None, None),
        'Clap':                      NaoMove(4.13,  None, None),
        'Joy':                       NaoMove(5.0,  None, None),
        'Sit_Quick':                 NaoMove(8.0,   {'standing': True},  {'standing': False}),
    }

    # ----------------------------
    # Mandatory positions sequence
    # ----------------------------
    starting_position = (
        '14-StandInit',
        NaoMove(1.14, None, {'standing': True}),
    )

    mandatory = [
        ('WipeForehead', NaoMove(4.6)),
        ('Hello',        NaoMove(4.38)),
        ('16-Sit',       NaoMove(17, None, {'standing': False})),
        ('17-SitRelax',  NaoMove(15, None, {'standing': False})),
        ('11-Stand',     NaoMove(1.96)),
        ('15-StandZero', NaoMove(1.9)),
    ]
    random.shuffle(mandatory)  # Randomize mandatory positions order

    final_pos = (
        '6-Crouch',
        NaoMove(2.46),
    )

    pos_list = [starting_position, *mandatory, final_pos]
    steps_num = len(pos_list) - 1

    # ----------------------------
    # Time bookkeeping
    # ----------------------------
    total_time = sum(move.duration for _, move in pos_list)

    remaining_time_total = MAX_DURATION - total_time
    if remaining_time_total < 0:
        raise ValueError(
            f"MAX_DURATION ({MAX_DURATION:.2f}s) is smaller than the total mandatory duration "
            f"({total_time:.2f}s). Increase MAX_DURATION or reduce mandatory moves."
        )

    remaining_time_per_step = remaining_time_total / steps_num

    # ----------------------------
    # Planning phase
    # ----------------------------
    solution = tuple()
    print("PLANNED CHOREOGRAPHY:")
    start_planning = time.time()

    for i in range(1, len(pos_list)):
        # Each step: plan between two mandatory positions
        starting_pos = pos_list[i - 1]
        ending_pos = pos_list[i]

        # First move of this step is the mandatory starting pose
        choreography = (starting_pos[0],)

        initial_standing = postcondition_standing(starting_pos[0])
        goal_standing = precondition_standing(ending_pos[0])

        # Time slot for this step (only for intermediate moves)
        remaining_time = remaining_time_per_step

        # Initial state for this subproblem
        cur_state = (
            ('choreography', choreography),
            ('standing', initial_standing),
            ('remaining_time', remaining_time),
        )

        # Goal: correct standing + remaining_time ~ 0
        cur_goal_state = (
            ('standing', goal_standing),
            ('remaining_time', 0.0),
        )

        # Subproblem: fill the time slot penalizing repetitions
        step_problem = NaoProblem(
            init=cur_state,
            goal=cur_goal_state,
            moves=moves,
            previous_moves=solution,
            lambda_penalty=LAMBDA_PENALTY,
            time_tolerance=TIME_TOLERANCE,
        )

        # A* search
        cur_solution_node = astar_search(step_problem)
        if cur_solution_node is None:
            raise RuntimeError(f"Step {i} - no solution was found!")

        cur_solution_dict = from_state_to_dict(cur_solution_node.state)
        cur_choreography = cur_solution_dict['choreography']

        print(f"Step {i}: \t" + ", ".join(cur_choreography))
        solution += cur_choreography

    end_planning = time.time()

    # Add final mandatory position to the overall solution
    solution += (final_pos[0],)

    # Final state of the last subproblem, used for statistics
    state_dict = from_state_to_dict(cur_solution_node.state)

    # ----------------------------
    # Global constraint: intermediate moves
    # ----------------------------
    mandatory_names = [pos_name for pos_name, _ in pos_list]
    intermediate_moves = [m for m in solution if m not in mandatory_names]

    # Check that at least MIN_INTERMEDIATE_MOVES intermediate moves are present
    if len(intermediate_moves) < MIN_INTERMEDIATE_MOVES:
        raise RuntimeError(
            f"Choreography has only {len(intermediate_moves)} intermediate moves. "
            f"At least {MIN_INTERMEDIATE_MOVES} are required."
        )

    # ----------------------------
    # Statistics and pretty printing
    # ----------------------------
    print_solution_statistics(state_dict, start_planning, end_planning, MAX_DURATION)
    print_choreography(solution, mandatory_names)

    # ----------------------------
    # Dance execution
    # ----------------------------
    print("\nDANCE EXEC:")
    player = play_song("Wii_Sports.mp3")
    start = time.time()
    do_moves(solution, robot_ip, port)
    end = time.time()
    print("Length of the entire choreography: %.2f seconds." % (end - start))


def precondition_standing(position):
    """
    Return the required 'standing' value that must hold *before*
    executing the given mandatory position.
    """
    if position == '17-SitRelax':
        return False
    return True


def postcondition_standing(position):
    """
    Return the 'standing' value that holds *after*
    executing the given mandatory position.
    """
    if position in ('16-Sit', '17-SitRelax'):
        return False
    return True


if __name__ == "__main__":
    robot_ip = "127.0.0.1"
    port = 40237

    if len(sys.argv) > 2:
        port = int(sys.argv[2])
        robot_ip = sys.argv[1]
    elif len(sys.argv) == 2:
        robot_ip = sys.argv[1]

    main(robot_ip, port)
