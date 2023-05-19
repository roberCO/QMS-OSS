import json
import math
import numpy as np
from scipy.stats import vonmises
import copy
import argparse


class Utils:

    def __init__(self, config_path=''):

        self.minimum_key_value = []
        self.maximum_key_value = []

        if config_path != '':
            try:
                f = open(config_path)
                f.close()
            except IOError:
                print('<!> Info: No configuration file')
                raise Exception('It is necessary to create a configuration file (.json) for some variables')

            with open(config_path) as json_file:
                        self.config_variables = json.load(json_file)

    def get_config_variable(self, variable):
        return self.config_variables[variable]

    def parse_arguments(self):

        parser = argparse.ArgumentParser(description="Module to create an input of n-queen problem for qms: Example ./python3 main.py 4")

        parser.add_argument("number_queens", help="number of queens of the problem", type=int)

        parser.add_argument("-q", "--queen", help="position (column) of the queen to fix", type=int, nargs='?')
        parser.add_argument("-v", "--value", help="position (row) of the queen to fix", type=int, nargs='?')

        self.args = parser.parse_args()
        self.fixed_position_queen = [self.args.queen, self.args.value] if self.args.queen != None and self.args.value != None else [-1, -1]

        return self.args

    # This method returns the json with all rotations and energies associated to these rotations
    # energies keys can contain hyphens ('-') to indicate that there is a group. For example '001 010' means that it is necessary to rotate (+/-1) 001 and then 010
    def calculateAllDeltasOfRotations(self, energies, is_circular, successor_generation_mode):

        deltasJson = {}
        deltasJson['deltas'] = {}

        # get the first key as reference (all keys should have the same structure (length and hyphens))
        first_key = list(energies.keys())[0]
        key_len = len(first_key.replace('-', ''))

        # count the number of hyphens (number groups = hyphens + 1) as the length of the key with hyphens minus the key without hyphens
        self.number_coordinates = (len(first_key) - key_len) + 1

        self.get_max_min_energy_indexes(energies)

        # check if all keys have the same number of groups
        if not all((len(key) - len(key.replace('-', ''))+1) == self.number_coordinates for key in energies):
            print('<*> ERROR: Not all energy keys have the number of groups')
            return
            
        print('    ⬤ Calculating deltas for all possible combinations of rotations')
        min_energy = 99999
        indexes_min_energy = []
        # iterates over all calculated energies using the keys (contains the values of the coords)      
        for e_key in energies.keys():

            old_energy = energies[e_key]

            # check if the energy is lower than the minimum
            if old_energy < min_energy:
                min_energy = old_energy
                indexes_min_energy = [e_key]

            elif old_energy == min_energy:
                indexes_min_energy.append(e_key)
            
            # divide the key in groups
            key_groups = e_key.split('-')
            for group_id in range(len(key_groups)):

                # calculate the plus/minus 1 rotation delta
                for plusminus in [0,1]:

                    pm = (-2)*plusminus + 1

                    # if the mode is swap, check that it is in the range of exchange
                    # if it is not swap, executes normally
                    if not successor_generation_mode =='swap' or (group_id+pm >= 0 and group_id+pm < len(key_groups)):

                        [new_key, new_value] = self.generate_new_key(key_groups, group_id, pm, is_circular, successor_generation_mode)

                        # if new_value is in the range max-min, the energy is extracted from the file
                        # if new_value is out of the range max-min, the energy is a default high energy to avoid the step (a barrier)
                        delta=energies[new_key] - old_energy if new_value <= self.maximum_key_value[group_id] and new_value >= self.minimum_key_value[group_id] else self.config_variables['barrier_energy_value']
                        deltasJson['deltas'][self.generate_deltas_key(key_groups, group_id, plusminus)] = delta

        deltasJson['initial_min_energy'] = min_energy
        deltasJson['indexes_min_energy'] = indexes_min_energy

        with open('deltas.json', 'w') as outfile:
            json.dump(deltasJson, outfile)

        return deltasJson

    def generate_new_key(self, key_groups, group_id, pm, is_circular, successor_generation_mode):

        # new key contains the key for the new energy
        new_key = ''
        new_key_groups = copy.deepcopy(key_groups)

        if successor_generation_mode == 'sequential':

            new_value = int(new_key_groups[group_id]) + pm

            # if new value is out of the range max-min value
            if is_circular and new_value > self.maximum_key_value[group_id]: new_value = self.minimum_key_value[group_id]
            elif is_circular and new_value < self.minimum_key_value[group_id]: new_value = self.maximum_key_value[group_id]

            new_key_groups[group_id] = str(new_value)

        elif successor_generation_mode == 'swap':
            
            new_value = int(new_key_groups[group_id+pm])

            temp_value = new_key_groups[group_id+pm]
            new_key_groups[group_id+pm] = new_key_groups[group_id]
            new_key_groups[group_id] = temp_value
            

        # convert the list with the key to a string with - between numbers    
        new_key = ''.join([key_number+'-' for key_number in new_key_groups])
        return [new_key[:-1], new_value]

    def generate_deltas_key(self, key_groups, group_id, plusminus):

            deltas_key = ''

            # construct the new_key adding the new value of the group with the rest of the groups
            for key_id in range(len(key_groups)):
                deltas_key += str(key_groups[key_id]) + ' '
            
            # remove last whitespace
            deltas_key = deltas_key.strip()
            
            #Add the values to the file with the precalculated energies
            # if there is more than one group, add an id for the group that is modified
            if self.number_coordinates > 1: deltas_key += '|' + str(group_id)

            # add 0/1 for plus/minus
            deltas_key += '|' + str(plusminus)

            deltas_key = deltas_key.replace(' ', '-')

            return deltas_key

    def calculate_tts_from_probability_matrix(self, probabilities_matrix_dict, indexes_min_energy, precision_solution):

        results = {}

        for step in probabilities_matrix_dict.keys():

            prob_matrix = probabilities_matrix_dict[step]

            p_t = 0
            # if one of the index of min energy calculated by psi 4 is in the results of metropolis, p_t is extracted (as a sum of all min_index)
            # else, the p_t is set to a very small value close to 0 (not 0 to avoid inf values)
            for i_min_energy in indexes_min_energy:

                if i_min_energy in prob_matrix.keys():
                    p_t += prob_matrix[i_min_energy]

            result = 0
            # Result is the calculated TTS
            if p_t >= 0.999:
                result = 1
            elif p_t == 0 or p_t < 1e-10:
                result = self.config_variables['default_value_tts']
            else:
                result = self.calculateTTS(precision_solution, step, p_t)

            results[step] = result

        return results

    def get_max_min_energy_indexes(self, energies):

        # get minimum and maximum value
        for key in energies:
            key = key.replace('-', '')
            for index in range(len(key)):
                                
                # append a new position to the max/min key value lists
                if index >= len(self.minimum_key_value):
                    self.minimum_key_value.append(int(key[index]))
                    self.maximum_key_value.append(int(key[index]))
                else:
                    
                    # update max/min vlaues if it is necessary
                    if int(key[index]) < self.minimum_key_value[index]: self.minimum_key_value[index] = int(key[index])
                    if int(key[index]) > self.maximum_key_value[index]: self.maximum_key_value[index] = int(key[index])

    def von_mises_amplitudes(self, n_qubits, kappa):

        probs = {}
        probs[0] = vonmises.cdf(np.pi/2**n_qubits, kappa) - vonmises.cdf(-np.pi/2**n_qubits, kappa)
        probs[2**n_qubits/2] = 2* vonmises.cdf(np.pi/2**n_qubits - np.pi, kappa)
        
        for i in range(1, 2**n_qubits//2):
            p = vonmises.cdf((2*i+1)*np.pi/2**n_qubits, kappa)-vonmises.cdf((2*i-1)*np.pi/2**n_qubits, kappa)
            probs[i] = p
            probs[-i + 2**n_qubits ] = p

        pr = []
        aa = []
        acc = []

        for i in range(2**n_qubits):
            pr.append(probs[i])

        for i in range(2**n_qubits):
            aa.append(np.sqrt(probs[i]))
            acc.append(np.sum(pr[:i]))
            
        acc.append(np.sum(pr)) # This should append 1
        acc = acc[1:] # We are not interested in the first item, which is 0

        return aa, acc

    # method to find how to generate successor in the oracle (swap or sequential)
    def find_successor_generation(self, energies):

        repeated_positions = False

        for position in energies:

            # if the length deleting the repeated is different than the length of all elements, there is one repeated element
            if len(set(position.split('-'))) != len(position.split('-')):
                repeated_positions = True
                break

        successor_generation_mode = 'sequential' if repeated_positions else 'swap'
        return successor_generation_mode

    def calculateTTS(self, precision_solution, t, p_t):

        return t * (math.log10(1-precision_solution)/(math.log10(1-p_t)))

    def execute_x_multiple_register(self, circuit, target, target_value, index, direction):

        if direction == 'fordward':

            for i in range(len(index)):
                if index[i] == target_value:
                    circuit.x(target[i])

        elif direction == 'backward':

            for i in range(len(index)):
                if index[len(index)-i-1] == target_value:
                    circuit.x(target[i])
        else:
            raise Exception("Wrong direction value")

    def read_results_data(self, input_name):

        path = self.config_variables['path_tts_plot']+input_name
        number_queens = input_name.split('_')[0]
        data = {}

        with open(path) as json_file:
            data[number_queens] = json.load(json_file)

        return data

    def read_results_sorting_data(self, input_name, order_name):

        path = self.get_config_variable('path_tts_plot')+input_name
        number_queens = input_name.split('_')[0]
        data = {}
        results = {}

        with open(path) as json_file:

            data = json.load(json_file)
            results[number_queens] = [d['quantum'] for d in data.values()]

        return results