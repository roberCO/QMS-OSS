from sympy.combinatorics.graycode import GrayCode, gray_to_bin, bin_to_gray
from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit, Qubit
from collections import OrderedDict
from qiskit import Aer, transpile

import math
import numpy as np

class Beta_precalc_TruthTableOracle():
    '''Outputs the binary coord of rotation to get the correct probability. Tested ok'''
    def __init__(self, deltas_dictionary, tools, in_bits, out_bits, precision_coords, optimization=False, mct_mode='noancilla'):

        self.out_bits = out_bits
        self.deltas_dictionary = OrderedDict(sorted(deltas_dictionary.items()))
        self.precision_coords = precision_coords
        self.tools = tools

        # If there are only two coords, we need to eliminate the penultimate digit of the keys:
        if len(list(self.deltas_dictionary.keys())[0]) == in_bits + 1:
            deltas = {}
            for (key, value) in list(self.deltas_dictionary.items()):
                deltas[key[:-2]+key[-1]] = value
            self.deltas_dictionary = deltas
        #assert(2**len(list(self.deltas_dictionary.keys())[0]) == len(self.deltas_dictionary))


    def generate_oracle(self, beta):

        coords = self.generate_coords_codification(beta)

        oracle_circuit = self.generate_qms_oracle(coords)

        return oracle_circuit.to_gate(label="oracle")

    def generate_coords_codification(self, beta):

        coords = {}

        for key in self.deltas_dictionary.keys():

            if self.deltas_dictionary[key] >= 0:
                probability = math.exp(-beta * self.deltas_dictionary[key])
            else: 
                probability = 1
            # Instead of encoding the coord corresponding to the probability, we will encode the coord theta such that sin^2(pi/2 - theta) = probability.
            # That way 1 -> 000, but if probability is 0 there is some small probability of acceptance
            
            # Instead of probability save coords so rotations are easier to perform afterwards sqrt(p) = sin(pi/2-theta/2).
            # The theta/2 is because if you input theta, qiskits rotates theta/2. Also normalised (divided between pi the result)
            coord = 1 - 2/math.pi * math.asin(math.sqrt(probability))

            # Ensure that the coord stays minimally away from 1
            coord = np.minimum(coord, 1-2**(-self.out_bits-1))
            # Convert it into an integer and a string
            if coord == 1.:
                print('probability = ',probability)
                print('coord',coord)
                raise ValueError('Warning: coord seems to be pi/2, and that should not be possible')
            
            # coord will be between 0 and 1, so we move it to between 0 and 2^out_bits. Then calculate the integer and the binary representation
            coords[key] = np.binary_repr(int(coord*2**self.out_bits), width= self.out_bits)

            #if key[:10] == '1101000101':
            #    print('<DEBUG> For key:', key, 'coord is:', coords[key])

        self.coords = coords

        return coords

    def generate_qms_oracle(self, coords):

        # calculate the length in binary of oracle key
        len_oracle_key = int(sum(self.precision_coords)) + int(math.ceil(np.log2(len(self.precision_coords)))) + 1
        if len(self.precision_coords) == 0: len_oracle_key += 1

        oracle_key = QuantumRegister(len_oracle_key, name='oracle_key')
        oracle_value = QuantumRegister(len(list(coords.values())[0]), name='oracle_value')

        # create a quantum circuit with the same length than the key of the deltas energies
        oracle_circuit = QuantumCircuit(oracle_key, oracle_value)

        for key in self.coords.keys():
            
            if '1' in coords[key]:

                binary_key = self.key_to_binary(key)

                # apply x gates to the 0s in the key
                self.tools.execute_x_multiple_register(oracle_circuit, oracle_key, '0', binary_key, 'backward')

                # apply mcx gates with the 1s in the coords (control the whole binary_key)
                coord = coords[key]
                for coord_bit_index in range(len(coord)):
                    if coord[(len(coord)-1) - coord_bit_index] == '1':
                        oracle_circuit.mcx(oracle_key, oracle_value[coord_bit_index])

                # apply x gates to the 0s in the binary_key
                self.tools.execute_x_multiple_register(oracle_circuit, oracle_key, '0', binary_key, 'backward')

        return transpile(oracle_circuit, Aer.get_backend('statevector_simulator'))

    # convert the interger key of the deltas dict in binary key
    # format of deltas key coord1-coord2-coord3-...|id(integer)|plusminus
    def key_to_binary(self, key):

        binary_key = ''

        coords = key.split('|')[0].split('-')
        id_integer = int(key.split('|')[1])
        plus_minus = key.split('|')[2]

        for coord_index in range(len(coords)):
            binary_key += np.binary_repr(int(coords[coord_index]), width = int(self.precision_coords[coord_index]))

        if len(self.precision_coords) == 1:
            binary_key += '0'
        else:
            number_bits_to_represent_id = int(math.ceil(np.log2(len(self.precision_coords))))
            binary_key += np.binary_repr(id_integer, width=number_bits_to_represent_id)

        binary_key += plus_minus

        return binary_key