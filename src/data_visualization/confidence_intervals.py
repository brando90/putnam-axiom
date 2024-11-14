import matplotlib.pyplot as plt
import numpy as np
import math
import textwrap

from collections import defaultdict, deque

confidence_intervals = {
    'Llama 3 8b': [3.295700182, 4.244299818, 3.295700182, 4.244299818],
    'Llama 3 8b Instruct': [6.84041068, 8.99958932, 3.188128058, 4.347871942],
    'Mistral 7B-v0.3': [5.696150892, 7.875849108, 4.363215003, 5.444784997],
    'Mistral 7B Instruct-v0.3': [1.86407157, 2.65592843, 3.889660019, 5.162339981],
    'gemma 7b': [2.754215291, 3.273784709, 2.995172302, 3.788827698],
    'gemma 2b': [1.918343156, 3.353656844, 1.482630993, 3.037369007],
    'gemma 7b-it': [2.995172302, 3.788827698, 4.577429957, 5.982570043],
    'gemma 2b-it': [2.772647178, 4.007352822, 2.097984736, 3.178015264],
    'deepseek math 7b-base': [5.4168395, 6.6511605, 3.731319231, 5.316680769],
    'deepseek math 7b-rl': [9.039161804, 12.0768382, 7.430734833, 9.149265167],
    'deepseek math 7b-instruct': [7.401117084, 8.438882916, 3.984094954, 5.063905046],
    'NuminaMath 7B-TIR': [9.277285895, 11.82271411, 4.759805104, 5.796194896],
    'Qwen2 Math-7B': [8.370024801, 11.2419752, 8.655172302, 9.448827698],
    'Qwen2 Math-7B Instruct': [9.926215291, 10.44578471, 7.207505927, 7.876494073],
    'Claude Sonnet-3.5': [22.83279695174412, 29.96720304825588, 15.58924908066727, 22.13075091933273], 
    'GPT-4': [10.531302982695788, 15.86869701730421, 7.342908354491403, 11.517091645508597], 
    'GPT-4o': [13.873125852282636, 20.086874147717367, 7.342908354491403, 11.517091645508597], 
    'GPT-o1-preview': [48.065811300136765, 50.03418869986323, 30.610913218108905, 37.18908678189109]
}

def plot_ci(ci_dict):
    models = list(ci_dict.keys())
    variation_ci = [ci[:2] for ci in ci_dict.values()]
    original_ci = [ci[2:] for ci in ci_dict.values()]

    def wrap_labels(labels, max_width):
        return ['\n'.join(textwrap.wrap(label, max_width)) for label in labels]
    
    wrapped_models = wrap_labels(models, 10)

    variation_means = [(ci[0] + ci[1]) / 2 for ci in variation_ci]
    original_means = [(ci[0] + ci[1]) / 2 for ci in original_ci]

    variation_errors = [(ci[1] - ci[0]) / 2 for ci in variation_ci]
    original_errors = [(ci[1] - ci[0]) / 2 for ci in original_ci]

    index = np.arange(len(models))
    bar_width = 0.2

    fig, ax = plt.subplots(figsize=(18, 8))

    # Add error bars with colors

    for i, (v_mean, v_error, o_mean, o_error) in enumerate(zip(variation_means, variation_errors, original_means, original_errors)):
        ax.errorbar(i, v_mean, yerr=v_error, fmt='o', color='b', alpha=0.7, capsize=15, markersize=10, elinewidth=15, label='Original' if i == 0 else "")
        ax.errorbar(i, o_mean, yerr=o_error, fmt='o', color='g', alpha=0.7, capsize=15, markersize=10, elinewidth=15, label='Variation' if i == 0 else "")

    # Add some text for labels, title and axes ticks
    ax.set_ylabel('Accuracy', fontsize=15)
    ax.set_title('Accuracy with Confidence Intervals of Models')
    ax.set_xticks(index)
    ax.set_xticklabels(wrapped_models, rotation=0, ha='center', fontweight='bold', fontsize=10)

    handles = [
        plt.Line2D([0], [0], color='b', lw=4, label='Original'),
        plt.Line2D([0], [0], color='g', lw=4, label='Variation')
    ]
    ax.legend(handles=handles)

    plt.tight_layout()
    plt.grid(True)
    plt.savefig('putnam-axiom/src/data_visualization/confidence_interval.png')
    plt.show()

plot_ci(confidence_intervals)