import numpy as np
from lab1.liuvacuum import *

DEBUG_OPT_DENSEWORLDMAP = False

AGENT_STATE_UNKNOWN = 0
AGENT_STATE_WALL = 1
AGENT_STATE_CLEAR = 2
AGENT_STATE_DIRT = 3
AGENT_STATE_HOME = 4

AGENT_DIRECTION_NORTH = 0
AGENT_DIRECTION_EAST = 1
AGENT_DIRECTION_SOUTH = 2
AGENT_DIRECTION_WEST = 3


def direction_to_string(cdr):
    cdr %= 4
    return (
        "NORTH"
        if cdr == AGENT_DIRECTION_NORTH
        else "EAST"
        if cdr == AGENT_DIRECTION_EAST
        else "SOUTH"
        if cdr == AGENT_DIRECTION_SOUTH
        else "WEST"
    )  # if dir == AGENT_DIRECTION_WEST


"""
Internal state of a vacuum agent
"""


class MyAgentState:
    def __init__(self, width, height):

        # Initialize perceived world state
        self.world = [
            [AGENT_STATE_UNKNOWN for _ in range(height)] for _ in range(width)
        ]
        self.world[1][1] = AGENT_STATE_HOME

        # Agent internal state
        self.last_action = ACTION_NOP
        self.direction = AGENT_DIRECTION_EAST
        self.pos_x = 1
        self.pos_y = 1

        # Metadata
        self.world_width = width
        self.world_height = height

    """
    Update perceived agent location
    """

    def update_position(self, bump):
        if not bump and self.last_action == ACTION_FORWARD:
            if self.direction == AGENT_DIRECTION_EAST:
                self.pos_x += 1
            elif self.direction == AGENT_DIRECTION_SOUTH:
                self.pos_y += 1
            elif self.direction == AGENT_DIRECTION_WEST:
                self.pos_x -= 1
            elif self.direction == AGENT_DIRECTION_NORTH:
                self.pos_y -= 1

    """
    Update perceived or inferred information about a part of the world
    """

    def update_world(self, x, y, info):
        self.world[x][y] = info

    """
    Dumps a map of the world as the agent knows it
    """

    def print_world_debug(self):
        for y in range(self.world_height):
            for x in range(self.world_width):
                if self.world[x][y] == AGENT_STATE_UNKNOWN:
                    print("?" if DEBUG_OPT_DENSEWORLDMAP else " ? ", end="")
                elif self.world[x][y] == AGENT_STATE_WALL:
                    print("#" if DEBUG_OPT_DENSEWORLDMAP else " # ", end="")
                elif self.world[x][y] == AGENT_STATE_CLEAR:
                    print("." if DEBUG_OPT_DENSEWORLDMAP else " . ", end="")
                elif self.world[x][y] == AGENT_STATE_DIRT:
                    print("D" if DEBUG_OPT_DENSEWORLDMAP else " D ", end="")
                elif self.world[x][y] == AGENT_STATE_HOME:
                    print("H" if DEBUG_OPT_DENSEWORLDMAP else " H ", end="")

            print()  # Newline
        print()  # Delimiter post-print


"""
Vacuum agent
"""


class MyVacuumAgent(Agent):
    def __init__(self, world_width, world_height, log):
        super().__init__(self.execute)
        self.initial_random_actions = 10
        self.iteration_counter = world_height*world_width*2
        self.state = MyAgentState(world_width, world_height)
        self.log = log
        self.heat_map= [[0 for _ in range(world_height)] for _ in range(world_width)]
    def move_to_random_start_position(self, bump):
        action = random()
        self.first_run=1
        self.goHome=False
        self.heat_hole=1

        self.initial_random_actions -= 1
        self.state.update_position(bump)

        if action < 0.1666666:  # 1/6 chance
            self.state.direction = (self.state.direction + 3) % 4
            self.state.last_action = ACTION_TURN_LEFT
            return ACTION_TURN_LEFT
        elif action < 0.3333333:  # 1/6 chance
            self.state.direction = (self.state.direction + 1) % 4
            self.state.last_action = ACTION_TURN_RIGHT
            return ACTION_TURN_RIGHT
        else:  # 4/6 chance
            self.state.last_action = ACTION_FORWARD
            return ACTION_FORWARD

    def upd_Map(self, x,y, bumpy, get_to_this_pos):
        if get_to_this_pos!=0:
            for j in range(1, self.state.world_height -1):
                for i in range(1, self.state.world_width -1):
                    self.heat_map[i][j]+= abs((i-get_to_this_pos[0]))+abs((j-get_to_this_pos[1]))
            return
        else:
            if self.state.last_action==ACTION_TURN_RIGHT or self.state.last_action==ACTION_TURN_LEFT:
                return
            else:

                if bumpy:
                    self.heat_map[x][y] +=100
                else:
                    self.heat_map[x][y] +=1

    def turn_right(self):
        self.state.direction= (self.state.direction +1) %4
        self.state.last_action=ACTION_TURN_RIGHT
        return ACTION_TURN_RIGHT

    def turn_left(self):
        self.state.direction= (self.state.direction +3) %4
        self.state.last_action=ACTION_TURN_LEFT
        return ACTION_TURN_LEFT
    def forward(self):
        self.state.last_action=ACTION_FORWARD
        return ACTION_FORWARD

    def execute(self, percept):
        # print('-----------EXECUTE------------')

        ###########################
        # DO NOT MODIFY THIS CODE #
        ###########################

        bump = percept.attributes["bump"]
        dirt = percept.attributes["dirt"]
        home = percept.attributes["home"]

        # Move agent to a randomly chosen initial position
        if self.initial_random_actions > 0:
            self.log(
                "Moving to random start position ({} steps left)".format(
                    self.initial_random_actions
                )
            )
            return self.move_to_random_start_position(bump)

        # Finalize randomization by properly updating position (without subsequently changing it)
        elif self.initial_random_actions == 0:
            self.initial_random_actions -= 1
            self.state.update_position(bump)
            self.state.last_action = ACTION_SUCK
            self.log("Processing percepts after position randomization")
            return ACTION_SUCK

        ########################
        # START MODIFYING HERE #
        ########################

        # Max iterations for the agent
        if self.iteration_counter < 1:
            if self.iteration_counter == 0:
                self.iteration_counter -= 1
                self.log("Iteration counter is now 0. Halting!")
                self.log("Performance: {}".format(self.performance))
            return ACTION_NOP

        self.log(
            "Position: ({}, {})\t\tDirection: {}".format(
                self.state.pos_x,
                self.state.pos_y,
                direction_to_string(self.state.direction),
            )
        )

        if self.first_run == 1:
            for i in range(self.state.world_width):
                self.upd_Map(i, 0, AGENT_STATE_WALL,0)
                self.upd_Map(i, self.state.world_height - 1, AGENT_STATE_WALL,0)
            for j in range(self.state.world_height): 
                self.upd_Map(0, j, AGENT_STATE_WALL,0)
                self.upd_Map(self.state.world_width - 1, j, AGENT_STATE_WALL,0)
            self.first_run = 0

        self.upd_Map(self.state.pos_x, self.state.pos_y,0, 0)
        # Track position of agent
        self.state.update_position(bump)
        world = []
        goals=[]
        for y in range(self.state.world_height -2):
            for x in range(self.state.world_width -2):
                if self.state.world[x+1][y+1] == 0:
                    goals.append([x+1, y+1])
                world.append(self.state.world[x+1][y+1])

        # print(len(goals))
        # if world.count(0) < 16:
        #     self.previous != pop()
        #     if 
        #     self.log('BEAST MODE')
        #     print('SUPER MODE')
        #     self.upd_Map(self.state.pos_x, self.state.pos_y,0, goals[0])


        if not(0) in world:
            self.goHome = True



        
        current_surrondings=[]
        if self.state.direction== 0:
            current_surrondings = [self.heat_map[self.state.pos_x][self.state.pos_y -1 ], self.heat_map[self.state.pos_x + 1][self.state.pos_y],self.heat_map[self.state.pos_x][self.state.pos_y +1], self.heat_map[self.state.pos_x - 1][self.state.pos_y]]
        if self.state.direction== 1:
            current_surrondings = [self.heat_map[self.state.pos_x + 1][self.state.pos_y],self.heat_map[self.state.pos_x][self.state.pos_y +1], self.heat_map[self.state.pos_x - 1][self.state.pos_y], self.heat_map[self.state.pos_x][self.state.pos_y -1 ]]
        if self.state.direction== 2:
            current_surrondings = [self.heat_map[self.state.pos_x][self.state.pos_y +1], self.heat_map[self.state.pos_x - 1][self.state.pos_y], self.heat_map[self.state.pos_x][self.state.pos_y -1 ], self.heat_map[self.state.pos_x + 1][self.state.pos_y]]
        if self.state.direction== 3:
            current_surrondings = [self.heat_map[self.state.pos_x - 1][self.state.pos_y],self.heat_map[self.state.pos_x][self.state.pos_y -1 ], self.heat_map[self.state.pos_x + 1][self.state.pos_y],self.heat_map[self.state.pos_x][self.state.pos_y +1]]

 
        self.iteration_counter -= 1





        if bump:
            # Get an xy-offset pair based on where the agent is facing
            offset = [(0, -1), (1, 0), (0, 1), (-1, 0)][self.state.direction]

            # Mark the tile at the offset from the agent as a wall (since the agent bumped into it)
            self.state.update_world(
                self.state.pos_x + offset[0],
                self.state.pos_y + offset[1],
                AGENT_STATE_WALL,
            )
            self.upd_Map(
                self.state.pos_x + offset[0],
                self.state.pos_y + offset[1],
                1,0
            )
        

        print(np.matrix(np.transpose(self.heat_map)))

        if self.goHome and not(home) and self.heat_hole:
            print('maaaammmma')
            self.heat_hole=0
            hem=[1,1]
            self.upd_Map(self.state.pos_x, self.state.pos_y, bump, hem)

        elif self.goHome and home:
            self.log('MISSION COMPLETED ')
            self.log(self.iteration_counter)
            self.log(' MOVES LEFT')
            self.iteration_counter=0
            self.state.last_action=ACTION_NOP
            return ACTION_NOP
        # else:

        # Update perceived state of current tile
        if dirt:
            self.state.update_world(
                self.state.pos_x, self.state.pos_y, AGENT_STATE_DIRT
            )
        else:
            self.state.update_world(
                self.state.pos_x, self.state.pos_y, AGENT_STATE_CLEAR
            )

        # Debug
        self.state.print_world_debug()

        # Decide action
        if dirt:
            self.log("DIRT -> choosing SUCK action!")
            self.state.last_action = ACTION_SUCK
            return ACTION_SUCK
        elif bump:
            print('BUMP')
            return self.turn_right()
        elif current_surrondings.index(min(current_surrondings)) == 0:
            print('MOVING FORWARD')
            return self.forward()
        elif current_surrondings.index(min(current_surrondings)) == 3:
            print('Left')
            return self.turn_left()
        elif current_surrondings.index(min(current_surrondings)) != 0:
            print('Right')
            return self.turn_right()
