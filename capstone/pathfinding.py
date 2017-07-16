# Sample code from http://www.redblobgames.com/pathfinding/
# Copyright 2014 Red Blob Games <redblobgames@gmail.com>
#
# Feel free to use this code in your own projects, including commercial projects
# License: Apache v2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>


import collections

PENALTY_FOR_NOT_VISITING = 100
class Queue:
    def __init__(self):
        self.elements = collections.deque()
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, x):
        self.elements.append(x)
    
    def get(self):
        return self.elements.popleft()

# utility functions for dealing with square grids
def from_id_width(id, width):
    return (id % width, id // width)

def draw_tile(graph, id, style, width):
    r = "."
    if 'number' in style and id in style['number']: r = "%d" % style['number'][id]
    if 'point_to' in style and style['point_to'].get(id, None) is not None:
        (x1, y1) = id
        (x2, y2) = style['point_to'][id]
        if x2 == x1 + 1: r = 'r'#'\u2192'
        if x2 == x1 - 1: r = 'l'#'\u2190'
        if y2 == y1 + 1: r = 'd'#'\u2193'
        if y2 == y1 - 1: r = 'u'#'\u2191'
    if 'start' in style and id == style['start']: r = "A"
    if 'goal' in style and id == style['goal']: r = "Z"
    if 'path' in style and id in style['path']: r = "@"
    if id in graph.walls: r = "#" * width
    if 'visit' in style and id in graph.location_visited: r = "V"+str(graph.location_visited[id])
    return r

def draw_grid(graph, width=2, **style):
    for y in reversed(range(graph.height)):
        for x in range(graph.width):
            print "%%-%ds" % width % draw_tile(graph, (x, y), style, width), ;
        print ''

'''
Return locations gotten as result in a* algorithm from start position to goal

def get_path_came_from(came_from, start, goal):
    current_location = goal
    locations=[]
    while (came_from[current_location]!=start):
        locations.append(current_location)
        current_location=came_from[current_location]
    locations.append(current_location)
    locations.reverse()
    
    return locations
    '''
class SquareGrid(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = []
        self.dead_end_path_locations = []
        self.location_visited = {}
        
    def in_bounds(self, id):
        ((_,_),(x, y)) = id
        return 0 <= x < self.width and 0 <= y < self.height
    
    def passable(self, id):
        ((x1,y1),(x, y)) = id
        return id not in self.walls
    
    '''
    Return all possible reachable nodes given a position and maximum number of steps in one turn. Nodes must be inside maze and passable path (without wall)
    '''
    def possible_neighbors(self, id, max_steps):
        (x, y) = id
        results = []
        for step in range(max_steps):
            if (self.in_bounds(((x+step, y),(x+step+1, y))) and (self.passable(((x+step, y),(x+step+1, y))))):
                results+=[((x+step, y),(x+step+1, y))]
            else:
                break
                
        for step in range(max_steps):
            if (self.in_bounds(((x, y-step),(x, y-step-1))) and (self.passable(((x, y-step),(x, y-step-1))))):
                results+=[((x, y-step),(x, y-step-1))]  
            else:
                break
                
        for step in range(max_steps):
            if (self.in_bounds(((x-step, y),(x-step-1, y))) and (self.passable(((x-step, y),(x-step-1, y))))):
                results+=[((x-step, y),(x-step-1, y))]
            else:
                break
        for step in range(max_steps):
            if (self.in_bounds(((x, y+step),(x, y+step+1))) and (self.passable(((x, y+step),(x, y+step+1))))):
                results+=[((x, y+step),(x, y+step+1))]
            else:
                break
        return results
        
    def neighbors(self, id, max_steps):
        (x, y) = id
        results = self.possible_neighbors(id, max_steps)
        if (x + y) % 2 == 0: 
            results.reverse() # aesthetics
        destinations = [d for x,d in results]

        return destinations

    def add_wall(self, current_location, next_location):
        x,y=next_location
        if (x>=0 and y>=0 and x<self.width and y<self.height):
            wall = (current_location, next_location)
            if (wall not in self.walls):
                self.walls.append(wall)
                
    def add_dead_end_path_location(self, current_location):
        if (current_location not in self.dead_end_path_locations):
            self.dead_end_path_locations.append(current_location)
    
    def add_visit(self, current_location):
        if (current_location in self.location_visited):
            self.location_visited[current_location]+=1
        else:
            self.location_visited[current_location]=1

class GridWithWeights(SquareGrid):
    def __init__(self, width, height):
        super(GridWithWeights,self).__init__(width, height)
        self.weights = {}
    
    '''
    Return cost to move from node to other. If it's run 2 cost is high if node wasn't visited in run 1
    '''
    def cost(self, from_node, to_node, is_run2):
        if (to_node not in self.location_visited)and is_run2:
            return PENALTY_FOR_NOT_VISITING
        return self.weights.get(to_node, 1)


import heapq

class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]

def dijkstra_search(graph, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current = frontier.get()
        
        if current == goal:
            break
        
        for next in graph.neighbors(current,3):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost
                frontier.put(next, priority)
                came_from[next] = current
    
    return came_from, cost_so_far

def reconstruct_path(came_from, start, goal):
    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    #path.append(start) # optional
    path.reverse() # optional
    return path

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def a_star_search(graph, start, goal, is_run2=False):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()
        
        #if current == goal:
            #break
        
        for next in graph.neighbors(current,3):
            new_cost = cost_so_far[current] + graph.cost(current, next, is_run2)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current
    
    return came_from, cost_so_far