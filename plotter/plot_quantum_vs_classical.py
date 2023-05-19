
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict

from bokeh.plotting import figure, show, output_file
from bokeh.io import export_svgs
from bokeh.models import Legend, ColumnDataSource, LabelSet, Label

from utils import Utils
tools = Utils()

def TTSplotter(data, width = 800, height = 450, title = None, plot_width=500, plot_height=500):

    x_range = (1, 10**4)
    y_range = (1, 10**4)

    plot_q_c_slop = figure(
        #title='Evolution of tts with different steps', # Usually graphs do not have title
        x_axis_type="log",
        y_axis_type="log",
        x_range= x_range, 
        y_range= y_range,
        plot_height=height,
        plot_width=width,
        title = title)

    plot_q_c_slop.background_fill_alpha = 0

    plot_q_c_slop.yaxis.axis_label = 'Quantum min(TTS)'
    plot_q_c_slop.xaxis.axis_label = 'Classical min(TTS)'

    text_font_size = '16px'

    x_point = []
    y_point = []
    line_color = []
    marker = []
    legend = []
    size = []
    names=[]

    for number_queens in data.keys():


        for number_sample in data[number_queens].keys():

            x_point.append(data[number_queens][number_sample]['classical'])
            y_point.append(data[number_queens][number_sample]['quantum'])

            if number_queens == '4':
                marker.append('square')
                line_color.append('red')
                names.append(number_queens)
            elif number_queens == '5':
                marker.append('circle')
                line_color.append('blue')
                names.append(number_queens)
            elif number_queens == '6':
                marker.append('diamond')
                line_color.append('green')
                names.append(number_queens)
            elif number_queens == '7':
                marker.append('star')
                line_color.append('orange')
                names.append(number_queens)
            elif number_queens == '8':
                marker.append('triangle')
                line_color.append('orange')
                names.append(number_queens)

            legend.append('n='+number_queens)
            size.append(int(number_queens)*1.5)

    logcx = np.log(x_point)
    logqy = np.log(y_point)

    model = np.polynomial.polynomial.polyfit(logcx, logqy, 1)
    logb, a = model
    b = np.exp(logb)

    # 100 linearly spaced numbers
    x_fit = np.linspace(x_range[0]/1e2, x_range[1]*1e2)

    # the function, which is y = x^2 here
    y_fit = b*x_fit**a
    #print('a,b',a,b)

    source = ColumnDataSource(dict(x = x_point, y = y_point, line_color=line_color, marker=marker, legend=legend, size=size, names=names))
    labels = LabelSet(x='x', y='y', text='names', x_offset=5, y_offset=5, source=source, render_mode='canvas')

    #plot_q_c_slop.triangle(min_tts_c, min_tts_q, size=10, line_color='red', color='transparent')      
    #plot_q_c_slop.circle(min_tts_c, min_tts_q, size=10, line_color='blue', color='transparent')

    line_color = 'red'  
    x_fit = list(x_fit)
    #fit_source = ColumnDataSource(dict(x = x_fit, y = y_fit, line_color='green', legend='y='+str(b)+'*x**'+str(a)))
    plot_q_c_slop.line(x_fit, y_fit, line_color=line_color) 
    # Failed attempt to picture an slope: we do not want a line, but a line when we are in log scale
    # slope = Slope(gradient=a, y_intercept=b, line_color=line_color, line_dash='dashed', line_width=3.5)
    # plot_q_c_slop.add_layout(slope)

    y0 = 25
    x0 = 0
    citation = Label(x=width-600 + x0, y=90 + y0, x_units='screen', y_units='screen',
        text='qTTS = '+str(np.round(b, 3))+'*cTTS^'+str(np.round(a, 3)), text_font_size= text_font_size, render_mode='css',
        border_line_color=line_color, border_line_alpha=0.0, border_line_dash = 'solid',
        background_fill_color=line_color, background_fill_alpha=0, text_color = line_color)

    plot_q_c_slop.add_layout(citation)
    #plot_q_c_slop.add_layout(labels)


    plot_q_c_slop.scatter(x="x", y="y", line_color="line_color", fill_alpha=0, marker="marker", source=source, size = "size") #legend_group='legend',

    x_diag = [1, 10**6]
    y_diag = [1, 10**6]
    plot_q_c_slop.line(x_diag, y_diag, line_width=2, line_color='gray', line_dash="dashed")

    plot_q_c_slop.yaxis.major_label_orientation = "vertical"
    plot_q_c_slop.xgrid.grid_line_color = None
    plot_q_c_slop.ygrid.grid_line_color = None

    citation = Label(x=1/7*width, y=20, x_units='screen', y_units='screen',
                    text='quantum min(TTS) < classical min(TTS)', render_mode='css', text_font_size = text_font_size,
                    border_line_color='black', border_line_alpha=0.0,
                    background_fill_color='white', background_fill_alpha=0.0)

    plot_q_c_slop.add_layout(citation)

    citation = Label(x=.1*width, y=5/6*height, x_units='screen', y_units='screen',
                    text='classical min(TTS) < quantum min(TTS)', render_mode='css', text_font_size = text_font_size,
                    border_line_color='black', border_line_alpha=0.0,
                    background_fill_color='white', background_fill_alpha=0.0)

    plot_q_c_slop.add_layout(citation)

    return plot_q_c_slop

def generate_legend(plot, x0, y0, position = True, schedule = 'fixed'):
    x = -1
    y = -1
    sr = plot.square(x, y, line_color="red", fill_alpha = 0)
    cb = plot.circle(x, y, line_color="blue", fill_alpha = 0)
    dg = plot.diamond(x, y, color = 'green')
    so = plot.asterisk(x, y, color='orange')
    tp = plot.triangle(x, y, line_color="pink", fill_alpha = 0)

    location = (x0, y0) if position else 'top_left'

    legend = Legend(items=[
        ("4 queen", [sr]),
        ("5 queen", [cb]),
        ("6 queen", [dg]),
        ("7 queen", [so]),
        ("8 queen", [tp])
    ], location=location, background_fill_alpha = 0, border_line_alpha = 0)

    plot.add_layout(legend, 'left')
    if schedule != 'fixed':
        plot.legend.label_text_font_size = '15pt'

    return plot

def plot_q_vs_c_slope(data):

    output_file("TTS slope quantum vs random.html")
    width = 800
    height = 450

    plot_q_c_slop = TTSplotter(data, width = width, height = height)

    plot_q_c_slop = generate_legend(plot_q_c_slop, .75*width, 20)

    show(plot_q_c_slop)

    #plot_q_c_slop.output_backend = "svg"
    #export_svgs(plot_q_c_slop, filename="fixed_beta_TTS_slope.svg")

def get_plot_code_metric(order):

        if order=='lemieux': return "-bo"
        if order=='qubitization': return "--ys"
        if order=='other': return "-.g*"

def plot_different_orders(input_files, tools):

    results = {}
    for input_name in input_files:
        if re.match(r"[0-9]_queen.txt+", input_name):
            key='lemieux'
        elif re.match(r"[0-9]_queen_qubitization.txt+", input_name):
            key='qubitization'
        elif re.match(r"[0-9]_queen_sel_prepinv_r_prep.txt+", input_name):
            key='other'
        else:
            key='skip'

        if key != 'skip' and input_name != '7_queen.txt':
            if key in results.keys(): results[key].update(tools.read_results_sorting_data(input_name, key))
            else: results[key] = tools.read_results_sorting_data(input_name, key)

    for order in results.keys():

        results[order] = OrderedDict(sorted(results[order].items()))

        means = []
        stds = []
        for n in results[order].keys():

            means.append(np.mean(results[order][n]))
            stds.append(np.std(results[order][n]))
    
        plt.errorbar(results[order].keys(), means,  yerr=[stds], fmt=get_plot_code_metric(order), capsize=3.0, capthick=1.0, label = order)

    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.xlabel('Number queens', fontsize=14)
    plt.ylabel('Quantum TTS', fontsize=14)
    plt.yscale('log')
    plt.legend()
    plt.show()