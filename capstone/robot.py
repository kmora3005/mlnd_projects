import numpy as np
import random
from pathfinding import *
from statistics import Statistics

DEGREE_ROTATION = 90
MAX_OF_STEPS = 3
class Robot(object):
    
    def __init__(self, maze_dim, max_moves, smart_level=0, is_exploration_activated=False):
        '''
        Use the initialization function to set up attributes that your robot
        will use to learn and navigate the maze. Some initial attributes are
        provided based on common information, including the size of the maze
        the robot is placed in.
        '''
        
        random.seed()
        self.location = (0, 0)
        self.heading = 'up'
        self.maze_dim = maze_dim
        self.max_moves = max_moves
        #smart level=> 0: random, 1: random with dead-end path detection, 2: counting visits, 3: heuristic values
        self.smart_level = smart_level
        self.is_exploration_activated = is_exploration_activated
        self.start_location = (0, 0)
        self.goal_location = (maze_dim/2, maze_dim/2)
                     
        self.grid = GridWithWeights(self.maze_dim, self.maze_dim)
        self.optimal_path = []
        self.state='run 1'
        self.total_moves=0
        self.path_length=0
            
    def next_move(self, sensors):
        '''
        Use this function to determine the next move the robot should make,
        based on the input from the sensors after its previous move. Sensor
        inputs are a list of three distances from the robot's left, front, and
        right-facing sensors, in that order.

        Outputs should be a tuple of two values. The first value indicates
        robot rotation (if any), as a number: 0 for no rotation, +90 for a
        90-degree rotation clockwise, and -90 for a 90-degree rotation
        counterclockwise. Other values will result in no rotation. The second
        value indicates robot movement, and the robot will attempt to move the
        number of indicated squares: a positive number indicates forwards
        movement, while a negative number indicates backwards movement. The
        robot may move a maximum of three units per turn. Any excess movement
        is ignored.

        If the robot wants to end a run (e.g. during the first training run in
        the maze) then returing the tuple ('Reset', 'Reset') will indicate to
        the tester to end the run and return the robot to the start.
        '''
        
        next_rotation=0
        steps=0
        if (self.state!='goal unreachable'):
            if ((self.state=='run 1')or(self.state=='exploring')):
                self.grid.add_visit(self.location)
                #draw_grid(self.grid, width=3, visit=(0,0))
                self.check_walls(sensors)
                next_rotation, steps = self.choose_rotation_and_steps(sensors)
                self.update_heading(next_rotation)
                self.update_location(steps)
            elif (self.state=='run 2'):
                next_location = self.optimal_path[self.total_moves+1]
                next_rotation = self.get_rotation_based_on_location(next_location)
                self.update_heading(next_rotation)
                steps = self.get_steps_based_on_location(next_location)
                self.location = next_location
                if (self.is_in_goal(self.location)): 
                    self.state='ended'
                    print 'Goal reached. Ending!'
                    Statistics.set_total_moves(False,self.total_moves+1)
                    Statistics.set_path_length(False,self.path_length+steps)
                    
            self.total_moves+=1
            self.path_length+=steps

            if (self.state=='run 1' and self.is_in_goal(self.location)):
                Statistics.set_is_goal_reached(True)
                coverage=(float(len(self.grid.location_visited))/(self.maze_dim**2))*100
                Statistics.set_coverage(coverage)
                Statistics.set_total_moves(True,self.total_moves)
                Statistics.set_path_length(True,self.path_length)

                self.goal_location = self.location
                self.state='exploring'
                print 'Goal reached in move {0}. Exploration start!'.format(self.total_moves)
            elif (self.state=='run 1' and self.total_moves==self.max_moves):
                self.state='goal unreachable'
                coverage=(float(len(self.grid.location_visited))/(self.maze_dim**2))*100
                Statistics.set_coverage(coverage)
                #draw_grid(self.grid, width=3, visit=(0,0))
                print 'Goal does not reached'
            elif (self.state=='exploring' and (not(self.is_exploration_activated) or self.total_moves==self.max_moves or self.are_all_locations_visited())):
                came_from, cost_so_far=a_star_search(self.grid, self.start_location, self.goal_location, True)
                #draw_grid(self.grid, width=3, number=cost_so_far, start=self.start_location, goal=self.goal_location)
                #draw_grid(self.grid, width=3, point_to=came_from, start=self.start_location, goal=self.goal_location)
                self.optimal_path=reconstruct_path(came_from, self.start_location, self.goal_location)
                Statistics.set_optimal_path(self.optimal_path)
                Statistics.set_location_visited(self.grid.location_visited)
                Statistics.set_dead_end_path_locations(self.grid.dead_end_path_locations)
                self.state='run 2'
                self.total_moves=0
                self.path_length=0
                message = 'Exploration finished. Run 2 start!' if (self.is_exploration_activated) else 'Run 1 finished. No exploration stage. Run 2 start!'
                print message

                self.location = (0, 0)
                self.heading = 'up'
                return 'Reset', 'Reset'
            
        return next_rotation, steps

    '''
    Check if location is inside center goal
    '''
    def is_in_goal(self,location):
        (x,y)=location
        return ((self.maze_dim/2 == x and self.maze_dim/2 == y) or (self.maze_dim/2 - 1 == x and self.maze_dim/2 == y) or (self.maze_dim/2 == x and self.maze_dim/2 - 1 == y) or (self.maze_dim/2 - 1 == x and self.maze_dim/2 - 1 == y))

    '''
    Check if all locations are visited
    '''
    def are_all_locations_visited(self):
        return len(self.grid.location_visited)==(self.maze_dim**2)
    
    '''
    Choose a random move (rotation and number of steps to displace)
    '''
    def choose_rotation_and_steps(self, sensors):
        left_reading, forward_reading, right_reading = sensors
        possible_moves=[]

        if (left_reading !=0):
            possible_moves += [(-DEGREE_ROTATION, step) for step in range(min(left_reading,MAX_OF_STEPS)+1)]
        if (forward_reading !=0):
            possible_moves += [(0, step) for step in range(min(forward_reading,MAX_OF_STEPS)+1) if step!=0]
        if (right_reading !=0):
            possible_moves += [(DEGREE_ROTATION, step) for step in range(min(right_reading,MAX_OF_STEPS)+1)]
        
        possible_moves = self.get_possible_moves_based_on_smart_level(possible_moves)
            
        if (len(possible_moves)==0):
            possible_moves.append((-DEGREE_ROTATION,0))
            possible_moves.append((DEGREE_ROTATION,0))
            self.grid.add_dead_end_path_location(self.location)
            
        return random.choice(possible_moves)
    
    '''
    Filter possible moves based on smart level
    '''
    def get_possible_moves_based_on_smart_level(self, possible_moves):
        if (self.smart_level==1):
            possible_moves = [(rotation,step) for rotation,step in possible_moves if self.get_location(rotation,step) not in self.grid.dead_end_path_locations]
        elif (self.smart_level==2):
            locations_visited ={self.get_location(rotation,step):self.grid.location_visited.get(self.get_location(rotation,step),0) for rotation,step in possible_moves}
            if (len(locations_visited)>0):
                min_value = min(locations_visited.itervalues())
                possible_moves = [self.get_move(location) for location in locations_visited if locations_visited[location] == min_value]
        elif (self.smart_level==3):
            _, cost_so_far =a_star_search(self.grid, self.location, self.goal_location)
            del cost_so_far[self.location]
            possible_locations = {self.get_location(rotation,step):cost_so_far.get(self.get_location(rotation,step),100) for rotation,step in possible_moves}
            if len(possible_locations)>0:
                min_value = min(possible_locations.itervalues())
                possible_moves = [self.get_move(location) for location in possible_locations if possible_locations[location] == min_value]
        return possible_moves
    
    '''
    Update robot heading
    '''
    def update_heading(self, next_rotation):
        if ((next_rotation==DEGREE_ROTATION and self.heading=='left') or (next_rotation==-DEGREE_ROTATION and self.heading=='right')):
            self.heading='up'
        elif ((next_rotation==DEGREE_ROTATION and self.heading=='up') or (next_rotation==-DEGREE_ROTATION and self.heading=='down')):
            self.heading='right'
        elif ((next_rotation==DEGREE_ROTATION and self.heading=='right') or (next_rotation==-DEGREE_ROTATION and self.heading=='left')):
            self.heading='down'
        elif ((next_rotation==DEGREE_ROTATION and self.heading=='down') or (next_rotation==-DEGREE_ROTATION and self.heading=='up')):
            self.heading='left'

    '''
    Update robot position based on number of steps chosen
    '''
    def update_location(self, steps):
        x, y = self.location
        if (self.heading=='left'):
            self.location = (x-steps, y)
        elif (self.heading=='right'):
            self.location = (x+steps, y)
        elif (self.heading=='up'):
            self.location = (x, y+steps)
        elif (self.heading=='down'):
            self.location = (x, y-steps)
    
    '''
    Get location given rotation and step chosen
    '''
    def get_location(self, next_rotation, steps):
        x, y = self.location
        new_location=(0,0)
        if ((next_rotation==DEGREE_ROTATION and self.heading=='down') or (next_rotation==-DEGREE_ROTATION and self.heading=='up')or (next_rotation==0 and self.heading=='left')):
            new_location= (x-steps, y)
        elif ((next_rotation==DEGREE_ROTATION and self.heading=='up') or (next_rotation==-DEGREE_ROTATION and self.heading=='down')or (next_rotation==0 and self.heading=='right')):
            new_location= (x+steps, y)
        elif ((next_rotation==DEGREE_ROTATION and self.heading=='left') or (next_rotation==-DEGREE_ROTATION and self.heading=='right')or (next_rotation==0 and self.heading=='up')):
            new_location= (x, y+steps)
        elif ((next_rotation==DEGREE_ROTATION and self.heading=='right') or (next_rotation==-DEGREE_ROTATION and self.heading=='left')or (next_rotation==0 and self.heading=='down')):
            new_location= (x, y-steps)
        return new_location
    
    '''
    Get rotation and step given location chosen
    '''
    def get_move(self, location):
        x, y = self.location
        x1,y1= location
        rotation,steps=0,0
        if (x==x1):
            steps=abs(y-y1)
        elif (y==y1):
            steps=abs(x-x1)
            
        if ((self.heading=='up' and x<x1) or (self.heading=='down' and x>x1) or (self.heading=='right' and y>y1)or (self.heading=='left' and y<y1)):
            rotation=DEGREE_ROTATION
        elif ((self.heading=='up' and x>x1) or (self.heading=='down' and x<x1) or (self.heading=='right' and y<y1)or (self.heading=='left' and y>y1)):
            rotation=-DEGREE_ROTATION
        return rotation,steps

    '''
    Add wall detected in sensors
    '''
    def check_walls(self, sensors):
        left_reading, forward_reading, right_reading = sensors
        x, y = self.location
        if (self.heading=='up'):
            self.grid.add_wall((x-left_reading,y),(x-left_reading-1,y))
            self.grid.add_wall((x+right_reading,y),(x+right_reading+1,y))
            self.grid.add_wall((x,y+forward_reading),(x,y+forward_reading+1))
        elif (self.heading=='down'):
            self.grid.add_wall((x-right_reading,y),(x-right_reading-1,y))
            self.grid.add_wall((x+left_reading,y),(x+left_reading+1,y))
            self.grid.add_wall((x,y-forward_reading),(x,y-forward_reading-1))
        elif (self.heading=='left'):
            self.grid.add_wall((x-forward_reading,y),(x-forward_reading-1,y))
            self.grid.add_wall((x,y+right_reading),(x,y+right_reading+1))
            self.grid.add_wall((x,y-left_reading),(x,y-left_reading-1))
        elif (self.heading=='right'):
            self.grid.add_wall((x+forward_reading,y),(x+forward_reading+1,y))
            self.grid.add_wall((x,y+left_reading),(x,y+left_reading+1))
            self.grid.add_wall((x,y-right_reading),(x,y-right_reading-1))
            
    '''
    Get rotation given a location in run 2 following a* path
    '''
    def get_rotation_based_on_location(self, next_location):
        x, y = self.location
        x1,y1 = next_location
        if ((self.heading =='up' and x1<x)or(self.heading =='down' and x1>x)or(self.heading =='left' and y1<y)or(self.heading =='right' and y1>y)):
            return -DEGREE_ROTATION
        if ((self.heading =='up' and x1>x)or(self.heading =='down' and x1<x)or(self.heading =='left' and y1>y)or(self.heading =='right' and y1<y)):
            return DEGREE_ROTATION
        else:
            return 0
    
    '''
    Get displacement (number of steps) given a location in run 2 following a* path
    '''
    def get_steps_based_on_location(self, next_location):
        x, y = self.location
        x1,y1 = next_location
        if (x!=x1):
            return abs(x-x1)
        else:
            return abs(y-y1)