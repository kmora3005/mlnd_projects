'''
This class stores data with interesting results about runs. It's saved in a text file when the run 2 is ended
'''
import time
import collections

def singleton(cls):
    return cls()

@singleton
class Statistics(object):
    def __init__(self):
        self.maze_name = ""
        self.filename = ""
        self.maze_dim = 0
        self.smart_level = 0
        self.is_goal_reached = False
        self.is_exploration_activated = False
        self.coverage = 0
        self.total_moves1 = 0
        self.path_length1 = 0
        self.total_moves2 = 0
        self.path_length2 = 0
        self.optimal_path = []
        self.location_visited = {}
        self.dead_end_path_locations = []
        
    def set_main_parameters(self, maze_name, maze_dim, smart_level, is_exploration_activated):
        self.maze_name = maze_name
        self.maze_dim = maze_dim
        self.smart_level = smart_level
        self.is_exploration_activated = is_exploration_activated
        time_string = time.strftime("%Y%m%d_%H%M%S")
        self.filename = 'results/'+maze_name+'_smart_level_'+str(smart_level)+'_stats_'+time_string+'.txt'
        
    def set_is_goal_reached(self, is_goal_reached):
        self.is_goal_reached = is_goal_reached
        
    def set_coverage(self, coverage):
        self.coverage = coverage
        
    def set_total_moves(self, is_run1, total_moves):
        if (is_run1):
            self.total_moves1=total_moves
        else:
            self.total_moves2=total_moves
        
    def set_path_length(self, is_run1, path_length):
        if (is_run1):
            self.path_length1 = path_length
        else:
            self.path_length2 = path_length
        
    def set_optimal_path(self, optimal_path):
        self.optimal_path = optimal_path
        
    def set_location_visited(self, location_visited):
        self.location_visited = location_visited
        
    def set_dead_end_path_locations(self, dead_end_path_locations):
        self.dead_end_path_locations = dead_end_path_locations
        
    def set_score(self, score):
        self.score = score
        
    def write_optimal_path(self, text_file):
        for y in reversed(range(self.maze_dim)):
            for x in range(self.maze_dim):
                symbol_to_write=self.draw_tile( (x,y))
                text_file.write( "%%-%ds" % 3 % symbol_to_write)
            text_file.write("\n")
    
    def draw_tile(self, location):
        if (location in self.optimal_path):
            return self.optimal_path.index(location)
        else:
            if location[0]==0 and location[1]==0:
                return 'S'
            elif ((location[0]==self.maze_dim/2 or location[0]==(self.maze_dim/2)-1) and (location[1]==self.maze_dim/2 or location[1]==(self.maze_dim/2)-1)):
                return 'G'
            return '.'
        
    def save(self):
        with open(self.filename, "w") as text_file:
            text_file.write("Maze name: {0}\n".format(self.maze_name))
            text_file.write("Smart level: {0}\n".format(self.smart_level))
            text_file.write("Is there exploration stage? {0}\n".format(self.is_exploration_activated))
            text_file.write("\nRun 1=>\n")
            text_file.write("Is goal reached? {0}\n".format(self.is_goal_reached))
            text_file.write("Coverage: {0}%\n".format(self.coverage))
            text_file.write("Total moves: {0}\n".format(self.total_moves1))
            text_file.write("Path length: {0}\n".format(self.path_length1))
            text_file.write("\nRun 2=>\n")
            text_file.write("Total moves: {0}\n".format(self.total_moves2))
            text_file.write("Path length: {0}\n".format(self.path_length2))
            text_file.write("Optimal path: {0}\n".format(self.optimal_path))
            text_file.write("Score: {0}\n".format(self.score))
            text_file.write("\nMore info=>\n")
            text_file.write("Dead end path locations: {0}\n".format(self.dead_end_path_locations))
            text_file.write("Locations visited: {0}\n".format(self.location_visited))
            text_file.write("Optimal path visualization:\n")
            self.write_optimal_path(text_file)
            