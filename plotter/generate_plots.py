import sys
sys.path.insert(1, './')
from os import listdir
from os.path import isfile, join
import utils
import re

from plot_quantum_vs_classical import plot_q_vs_c_slope, plot_different_orders

#Read config file with the QFold configuration variables
config_path = './config/config.json'

tools = utils.Utils(config_path)

# list elements to read
input_files = [f for f in listdir(tools.get_config_variable('path_tts_plot')) if isfile(join(tools.get_config_variable('path_tts_plot'), f))]
results = {}
for input_name in input_files:
    if re.match(r"[0-9]_queen.txt+", input_name):
        results.update(tools.read_results_data(input_name))

#plot_q_vs_c_slope(results)

plot_different_orders(input_files, tools)