import utils
import classicalMetropolis
#import quantumMetropolis

class QMS:

    def __init__(self, energies, is_circular, tools):

        self.tools = tools

        self.is_circular = is_circular

        self.successor_generation_mode = self.tools.find_successor_generation(energies)

        self.deltas = self.tools.calculateAllDeltasOfRotations(energies, self.is_circular, self.successor_generation_mode)
        
    def execute_quantum_metropolis(self, mode):

        print('    ⬤ Calculating probabilities with Quantum Metropolis')
        probability_maxtrix_dict = self._quantum_metropolis()
        
        if mode == 'TTS':
            print('    ⬤ Calculating TTS results for Quantum Metropolis')
            return self.tools.calculate_tts_from_probability_matrix(probability_maxtrix_dict, self.deltas['indexes_min_energy'], self.tools.config_variables['precision_solution'])
        elif mode == 'probabilities':
            return probability_maxtrix_dict

    def execute_classical_metropolis(self, mode):

        print('    ⬤ Calculating probabilities with Classical Metropolis')
        probability_maxtrix_dict = self._classical_metropolis()

        if mode == 'TTS':
            print('    ⬤ Calculating TTS results for Classical Metropolis')
            return self.tools.calculate_tts_from_probability_matrix(probability_maxtrix_dict, self.deltas['indexes_min_energy'], self.tools.config_variables['precision_solution'])
        elif mode == 'probabilities':
            return probability_maxtrix_dict

    def _quantum_metropolis(self):


        #qm = quantumMetropolis.QuantumMetropolis(self.deltas, self.tools, self.is_circular, self.successor_generation_mode)
        #return qm.execute_quantum_metropolis()

        print("\n\n<i> If you want to execute quantum version please contact repository owner (Roberto Campos: robecamp@ucm.es)\n\n")

        raise Exception("Open version does not include quantum pipelines")



    def _classical_metropolis(self):

        cm = classicalMetropolis.ClassicalMetropolis(self.deltas['deltas'], self.tools, self.is_circular, self.successor_generation_mode)

        return cm.execute_metropolis()