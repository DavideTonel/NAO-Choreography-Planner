def print_solution_statistics(soluzion_state, start_planning, end_planning, total_time):
    print("\nSTATISTICS:")
    print(f"Time required by the planning phase: %.2f seconds." % (end_planning-start_planning))
    #print(f"Entropy of the solution found: {soluzion_state['entropy']}")
    print(f"Estimated choreography duration: {total_time - soluzion_state['remaining_time']}")

def print_choreography(solution, mandatory_positions):
    print("\nFINAL CHOREOGRAPHY:")
    for move in solution:
        if move in mandatory_positions:
            print(f"\t*** {move} ***")
        else:
            print(f"\t{move}")