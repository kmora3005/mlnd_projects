# Capstone project: Micromouse project siimulation

How run this project?
python tester.py <maze_path> <smart_level> <is_exploration_activated>

<maze_name> => test_maze_01.txt, test_maze_02.txt or test_maze_03.txt
<smart_level> => 0: random, 1: random with dead-end path detection, 2: counting locations visited, 3: heuristic values
<is_exploration_activated> => True or False

For example:
python tester.py test_maze_01.txt 0 False

The output file appears in the folder "results".
