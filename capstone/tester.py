from maze import Maze
from robot import Robot
from statistics import Statistics
import sys
import time
import os

#compile this so: python tester.py test_maze_01.txt 0 False
# global dictionaries for robot movement and sensing
dir_sensors = {'u': ['l', 'u', 'r'], 'r': ['u', 'r', 'd'],
               'd': ['r', 'd', 'l'], 'l': ['d', 'l', 'u'],
               'up': ['l', 'u', 'r'], 'right': ['u', 'r', 'd'],
               'down': ['r', 'd', 'l'], 'left': ['d', 'l', 'u']}
dir_move = {'u': [0, 1], 'r': [1, 0], 'd': [0, -1], 'l': [-1, 0],
            'up': [0, 1], 'right': [1, 0], 'down': [0, -1], 'left': [-1, 0]}
dir_reverse = {'u': 'd', 'r': 'l', 'd': 'u', 'l': 'r',
               'up': 'd', 'right': 'l', 'down': 'u', 'left': 'r'}

# test and score parameters
max_time = 1000
train_score_mult = 1/30.

if __name__ == '__main__':
    '''
    This script tests a robot based on the code in robot.py on a maze given
    as an argument when running the script.
    '''

    # Create a maze based on input argument on command line.
    if len(sys.argv)>=2:
        maze_path = str(sys.argv[1])
        smart_level = int(sys.argv[2]) if len(sys.argv)>2 else 0
        is_exploration_activated = sys.argv[3]=='True' if len(sys.argv)>3 else False
        maze_name = os.path.splitext(maze_path)[0]
        testmaze = Maze( maze_path )
        Statistics.set_main_parameters(maze_name, testmaze.dim, smart_level, is_exploration_activated)
    else:
        print 'At least two parameters are required: python path file and maze path file'
        sys.exit()
        
    # Intitialize a robot; robot receives info about maze dimensions.
    testrobot = Robot(testmaze.dim, max_time, smart_level, is_exploration_activated)

    # Record robot performance over two runs.
    runtimes = []
    total_time = 0
    for run in range(2):
        print "Starting run {}.".format(run)
        if (is_exploration_activated):
            total_time = 0
        # Set the robot in the start position. Note that robot position
        # parameters are independent of the robot itself.
        robot_pos = {'location': [0, 0], 'heading': 'up'}

        run_active = True
        hit_goal = False
        while run_active:
            # check for end of time
            total_time += 1
            if total_time > max_time:
                run_active = False
                print "Allotted time exceeded."
                break

            # provide robot with sensor information, get actions
            sensing = [testmaze.dist_to_wall(robot_pos['location'], heading)
                       for heading in dir_sensors[robot_pos['heading']]]
            rotation, movement = testrobot.next_move(sensing)

            # check for a reset
            if (rotation, movement) == ('Reset', 'Reset'):
                if run == 0 and hit_goal:
                    run_active = False
                    runtimes.append(total_time)
                    print "Ending first run. Starting next run."
                    break
                elif run == 0 and not hit_goal:
                    print "Cannot reset - robot has not hit goal yet."
                    continue
                else:
                    print "Cannot reset on runs after the first."
                    continue

            # perform rotation
            if rotation == -90:
                robot_pos['heading'] = dir_sensors[robot_pos['heading']][0]
            elif rotation == 90:
                robot_pos['heading'] = dir_sensors[robot_pos['heading']][2]
            elif rotation == 0:
                pass
            else:
                print "Invalid rotation value, no rotation performed."

            # perform movement
            if abs(movement) > 3:
                print "Movement limited to three squares in a turn."
            movement = max(min(int(movement), 3), -3) # fix to range [-3, 3]
            while movement:
                if movement > 0:
                    if testmaze.is_permissible(robot_pos['location'], robot_pos['heading']):
                        robot_pos['location'][0] += dir_move[robot_pos['heading']][0]
                        robot_pos['location'][1] += dir_move[robot_pos['heading']][1]
                        movement -= 1
                    else:
                        print "Movement stopped by wall."
                        movement = 0
                else:
                    rev_heading = dir_reverse[robot_pos['heading']]
                    if testmaze.is_permissible(robot_pos['location'], rev_heading):
                        robot_pos['location'][0] += dir_move[rev_heading][0]
                        robot_pos['location'][1] += dir_move[rev_heading][1]
                        movement += 1
                    else:
                        print "Movement stopped by wall."
                        movement = 0
                
            # check for goal entered
            goal_bounds = [testmaze.dim/2 - 1, testmaze.dim/2]
            if robot_pos['location'][0] in goal_bounds and robot_pos['location'][1] in goal_bounds:
                hit_goal = True
                if run != 0:
                    if (is_exploration_activated):
                        runtimes.append(total_time)
                    else:
                        runtimes.append(total_time - sum(runtimes))
                    run_active = False
                    print "Goal found; run {} completed!".format(run)
                    
            #time.sleep(5.1)
            
    # Report score if robot is successful.
    score=0
    if len(runtimes) == 2:
        score = runtimes[1] + train_score_mult*runtimes[0]
        print "Task complete! Score: {:4.3f}".format(score)
    Statistics.set_score(score)
    Statistics.save()
    