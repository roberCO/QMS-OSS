import utils
import problem_generator
import qms
from matplotlib import pyplot
import time
import datetime
from collections import OrderedDict

from n_queen_solutions_generator import n_queen_solution_by_n
import sys


print('\n###################################################################')
print('##                    QMS Open Source Software                   ##')
print('##                                                               ##')
print('##           Open version to solve any n-queen problem           ##')
print('###################################################################\n')

time_start = time.time()

#Read config file with the QFold configuration variables
config_path = './config/config.json'
tools = utils.Utils(config_path)

args = tools.parse_arguments()

# if one queen has a fixed position, it saves as (column, row)
if (args.queen!=None and args.value!=None) and (args.queen >= args.number_queens or args.value >= args.number_queens):
    print('<*> ERROR: The column or the row (', args.queen, ',', args.value, ') can not be grether than the number of queens', args.number_queens)
    sys.exit(0)

n_queen_solutions = n_queen_solution_by_n(args.number_queens)
if len(n_queen_solutions) < 1:
    print("<*> ERROR There are no solutions for the problem of", args.number_queens, "queens")
    sys.exit(0)

# generate a problem description of the input file that is valid for qms
progen = problem_generator.Problem_generator(number_queens=args.number_queens)
input_n_queen = progen.generate_input()

print('N-Queen board generated!!')

solver = qms.QMS(input_n_queen, False, tools)


classic_tts = solver.execute_classical_metropolis(mode='TTS')
step_minimum_c = min(classic_tts, key=classic_tts.get)
minimum_classic = classic_tts[step_minimum_c]
print('Minimum tts:', minimum_classic, 'at step:', step_minimum_c)

if tools.config_variables['output_plot']: 
    pyplot.plot(classic_tts.keys(), classic_tts.values())
    pyplot.savefig('classical_tts_'+str(args.number_queens)+'.png')


quantum_tts = solver.execute_quantum_metropolis(mode='TTS')
step_minimum_q = min(quantum_tts, key=quantum_tts.get)
minimum_quantum = quantum_tts[step_minimum_q]
print('Minimum tts:', minimum_quantum, 'at step:', step_minimum_q)

quantum_tts = OrderedDict(sorted(quantum_tts.items()))

if tools.config_variables['output_plot']: 
    pyplot.plot(quantum_tts.keys(), quantum_tts.values())
    pyplot.savefig('quantum_tts_'+str(args.number_queens)+'.png')


print("<i> N-Queen => Size", args.number_queens, "calculated in", str(datetime.timedelta(seconds=time.time() - time_start)), "(hh:mm:ss)")