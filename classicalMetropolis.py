import numpy as np
import copy
import math
import statistics
import time
import datetime

from sympy import false, true

class ClassicalMetropolis():

    def __init__(self, deltas_dict, tools, is_circular, successor_generation_mode):

        self.tools = tools
        self.is_circular = is_circular
        self.successor_generation_mode = successor_generation_mode

        self.initialization = self.tools.config_variables['initialization']
        self.beta = self.tools.config_variables['beta_classical']
        self.beta_type = self.tools.config_variables['beta_type']
        self.alpha = self.tools.config_variables['alpha']
        self.annealing_schedule = self.tools.config_variables['annealing_schedule']
        self.initial_step = self.tools.config_variables['initial_step']
        self.final_step = self.tools.config_variables['final_step']

        self.minimum_coord_value = self.tools.minimum_key_value
        self.maximum_coord_value = self.tools.maximum_key_value

        self.deltas_dict = deltas_dict
        self.number_coordinates = self.tools.number_coordinates

        # calculate the number of iterations based on the mean number of steps in the coordinate groups
        mean_coords_difference = statistics.mean([value[1] - value[0] for value in zip(self.minimum_coord_value, self.maximum_coord_value)])
        self.n_iterations = int(self.tools.config_variables['number_iterations'] * (mean_coords_difference ** self.number_coordinates))

    def execute_metropolis(self):

        probabilities_matrix_dict = {}

        for step in range(self.initial_step, self.final_step+1):
            
            time_start = time.time()

            probabilities_matrix = {}
    
            for _ in range(self.n_iterations):
                
                coords = self.calculate_metropolis_result(step)
            
                # it is necessary to construct the key from the received coords (from the classical metropolis)
                # the idea is to add 1/n_repetitions to the returned value (to get the normalized number of times that this coord was produced)
                position_coords = ''
                for index in range(len(coords)): position_coords += str(coords[index]) + '-'
                position_coords = position_coords[:-1]

                # if the is already created, sum the entry to the dict, else create the entry
                if position_coords in probabilities_matrix.keys():
                    probabilities_matrix[position_coords] += (1/self.n_iterations) 
                else:
                    probabilities_matrix[position_coords] = (1/self.n_iterations)

            probabilities_matrix_dict[step] = probabilities_matrix

            print("<i> Classical Metropolis => Step", step, "calculated in", str(datetime.timedelta(seconds=time.time() - time_start)), "(hh:mm:ss)")
        
        return probabilities_matrix_dict

    def calculate_metropolis_result(self, nW, fixed_coords=[]):

        #Final structure calculated with metropolis.

        # Data structure with the rotatation (0-rotation steps) of each coordinate
        # for example, if there are 3 groups of coordinates, it is necessary to store three positions
        coords_old = []

        if self.initialization == 'random':

            valid_coord = false
            while(not valid_coord):

                if self.successor_generation_mode == 'sequential':
                    coords_old = np.random.randint(self.minimum_coord_value, self.maximum_coord_value) # generate a initial random vector of coordinates
                elif self.successor_generation_mode == 'swap':

                    coords_old = []

                    for index in range(len(self.minimum_coord_value)):
                    
                        # generate a random value between the minimum and maximum value for each coord
                        random_candidate = np.random.randint(self.minimum_coord_value[index], self.maximum_coord_value[index]+1)
                        # repeat until the random candidate is not in the list
                        while(random_candidate in coords_old):
                            random_candidate = np.random.randint(self.minimum_coord_value[index], self.maximum_coord_value[index]+1)

                        coords_old.append(random_candidate)
                
                if self.tools.fixed_position_queen[0] == -1 or coords_old[self.tools.fixed_position_queen[0]] == self.tools.fixed_position_queen[1]:
                    valid_coord = true

        elif self.initialization == 'fixed':
            coords_old = fixed_coords

        for i in range(1, nW+1):

            coords_new, change_coord, change_plus_minus = self.generate_new_coords(coords_old)

            # This choice of Delta_E seems weird.
            # Correspondingly: (state = coord...) +  (move_id = coord +  position_coord) +  move_value
            beta_value = 0
            if self.beta_type == 'fixed':
                beta_value = self.beta
            elif self.beta_type == 'variable':
                if self.annealing_schedule == 'Cauchy' or self.annealing_schedule == 'linear':
                    beta_value = self.beta * i 
                elif self.annealing_schedule == 'Boltzmann' or self.annealing_schedule == 'logarithmic':
                    beta_value = self.beta * np.log(i) + self.beta
                elif self.annealing_schedule == 'geometric':
                    beta_value = self.beta * self.alpha**(-i+1)
                elif self.annealing_schedule == 'exponential': 
                    space_dim = self.number_coordinates
                    beta_value = self.beta * np.exp( self.alpha * (i-1)**(1/space_dim) )
                else:
                    raise ValueError('<*> ERROR: Annealing Scheduling wrong value. It should be one of [linear, logarithmic, geometric, exponential] but it is', self.annealing_schedule)
            else:
                ValueError('<*> ERROR: Beta type wrong value. Beta type should be variable or fixed but it is', self.beta_type)

            # convert coords_old to string and add a '-' between coords. Then remove last '-' (it is unnecessary)
            # add the change coord and change_plus_minus separated by |
            # if there is only one energy group, the key does not include the change_coord, if there is more than one energy group, include change_coord
            if self.number_coordinates == 1: key = ''.join(str(c)+'-' for c in coords_old)[:-1] + '|' + str(change_plus_minus)
            else: key = ''.join(str(c)+'-' for c in coords_old)[:-1] + '|' + str(change_coord) + '|' + str(change_plus_minus)

            Delta_E = self.deltas_dict[key]
            if Delta_E >= 0:
                probability_threshold = math.exp(-beta_value * Delta_E)
            else:
                probability_threshold = 1

            random_number = np.random.random_sample()

            # We should accept the change if probability_threshold > 1 (the energy goes down) or if beta is small.
            # If beta small, np.exp(-beta*Delta_E) approx 1.
            if random_number < min(1,probability_threshold): # Accept the change
                coords_old = copy.deepcopy(coords_new)

        return coords_old
    
    def generate_new_coords(self, coords_old):

        valid_coord = false
        while(not valid_coord):

            # initially the new coords are equal to the old (then one coord will be randomly modified)
            # deep copy is necessary to avoid two pointer to the same data structure (it is necessary only to modify one of the arrays)
            coords_new = copy.deepcopy(coords_old)
        
            # propose a change in one coord
            coord_change = np.random.choice(self.number_coordinates)

            # 0 = 1 | 1 = -1
            change_plus_minus = np.random.choice((0,1))
            pm = -2*change_plus_minus + 1

            # new coord in sequential mode is just to add pm to the new coord (that it is a copy of the previous coord)
            if self.successor_generation_mode == 'sequential':
                coords_new[coord_change] = (coords_new[coord_change] + pm)

            # new coord in swap mode it is necessary to exchange two coords
            elif self.successor_generation_mode == 'swap':
            
                # check if the change is the range of the coords
                if coord_change+pm < 0 or coord_change+pm >= len(coords_new):
                    change_plus_minus = (change_plus_minus+1)%2
                    pm = -2*change_plus_minus + 1

                # it is necessary to exchange two registers (two coords)
                # copy the first coord to a temp value, then the new coord to the first one and the temp to the new coord
                coord_temp = coords_new[coord_change+pm]
                coords_new[coord_change+pm] = coords_new[coord_change]
                coords_new[coord_change] = coord_temp

            # if new value is out of the range max-min value
            if self.is_circular and coords_new[coord_change] > self.maximum_coord_value[coord_change]: coords_new[coord_change] = self.minimum_coord_value[coord_change]
            elif self.is_circular and coords_new[coord_change] < self.minimum_coord_value[coord_change]: coords_new[coord_change] = self.maximum_coord_value[coord_change]

            if self.tools.fixed_position_queen[0] == -1 or coords_new[self.tools.fixed_position_queen[0]] == self.tools.fixed_position_queen[1]:
                valid_coord = true

        return coords_new, coord_change, change_plus_minus