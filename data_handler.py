'''
Data helper functions.
'''
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display
from ipywidgets import *
import pandas as pd

from constants import MODE_NAMES, TYPING_MODES


def load_data():
    '''
    Sets variables.
    '''
    # Load dataframes with data from all participants
    typing_df = pd.read_csv('typing_trials.csv', delimiter='\t')
    gesture_df = pd.read_csv('gestures.csv', delimiter='\t')
    layout_df = pd.read_csv('layout_trials.csv', delimiter='\t')

    # Add some columns
    layout_df['selection_count'] = layout_df['selections'].str.split(';').str.len()

    # Get participant list
    participants = sorted(typing_df.participant_id.unique())
    
    return typing_df, gesture_df, layout_df, participants


class DataPlotter(object):
    '''
    Helper class that plots data from a given key.
    '''
    def __init__(self, key, df, participants):
        self.key = key
        self.df = df
        self.participants = participants
        self.plots = None
        self.all_button = None
        self.checkboxes = None
        self.containers = None
        self.error_checkbox = None
        self.modes = sorted(df.mode_id.unique())

    def plot_data(self, mode, show_error=True, **kwargs):
        '''
        Plots the data.
        '''
        fig = plt.figure(figsize=(9, 5))
        all_means = []
        mode_values = self.df[self.df['mode_id'] == mode]
        plots = dict()
        for i, participant in enumerate(self.participants):
            participant_values = mode_values[mode_values['participant_id'] == participant].groupby('session_id')[self.key]
            all_means.append(participant_values.mean())
            yerrs = participant_values.std()
            if show_error:
                epsilon = 0.5 * (i / (len(self.participants) - 1) - 0.5)
            else:
                epsilon = 0
                yerrs = [0 for _ in yerrs]
            x = np.arange(1 + epsilon, len(all_means[-1]) + 1 + epsilon, 1)
            plots[participant] = plt.errorbar(x, all_means[-1], yerrs, label=participant)
        mean_values = mode_values.groupby(['participant_id', 'session_id'], as_index=False)[self.key].mean().groupby('session_id').mean()
        x = range(1, len(mean_values) + 1)
        plots['Overall'] = plt.plot(x, mean_values, '-*', label='Overall')
        plt.xticks(range(1, 1 + max([len(values) for values in all_means])))

        ax = plt.gca()
        ax.set_title(MODE_NAMES[mode])
        ax.legend(loc=2)
        if 'ylim' in kwargs:
            ax.set_ylim(kwargs['ylim'])
        ax.yaxis.grid(True)
        plt.show()
        return plots

    def show(self, **kwargs):
        '''
        Shows the plots for both modes
        '''
        # Plot data
        self.plots = [self.plot_data(mode, **kwargs) for mode in self.modes]

        # Helper button
        self.all_button = widgets.Button(description="Toggle Select All")
        display(self.all_button)
        self.all_button.on_click(self.toggle_all)
        
        # Create error checkbox
        self.error_checkbox = interactive(self.update_show_error, show_error=True)

        # Create checkboxes
        self.checkboxes = [interactive(self.update_plot, **{p: True, 'participant': fixed(p)}) for p in self.participants + ['Overall']]
        
        # Display checkboxes
        self.containers = []
        for i in range(0, len(self.checkboxes), 4):
            cb_container = widgets.Box()
            cb_container.children = self.checkboxes[i:i+4]
            display(cb_container)
            self.containers.append(cb_container)

        display(self.error_checkbox)

    def set_visible(self, p, visible):
        '''
        Change visibility of plot.
        '''
        p[0].set_visible(visible)
        self.set_error_visible(p, self.error_checkbox.children[0].value)
    
    def set_error_visible(self, p, visible):
        visible = visible and p[0].get_visible()
        if len(p) > 1:
            for p_i in p[1]:
                p_i.set_visible(visible)
        if len(p) > 2:
            for p_i in p[2]:
                p_i.set_visible(visible)

    def update_plot(self, **kwargs):
        '''
        Create checkboxes to select participants.
        '''
        participant = kwargs['participant']
        visible = kwargs[participant]
        for checkbox in self.checkboxes:
            for plot in self.plots:
                self.set_visible(plot[participant], visible)
    
    def update_show_error(self, show_error):
        '''
        Show/hide error bars from plot.
        '''
        for checkbox in self.checkboxes:
            for plot in self.plots:
                for participant in self.participants:
                    self.set_error_visible(plot[participant], show_error)

    def toggle_all(self, b):
        '''
        Toggles all checkboxes to either true or false. If there is at least
        one checked checkbox all checkboxes will be unckecked.
        '''
        new_value = not any([c.children[0].value for c in self.checkboxes])
        for checkbox in self.checkboxes:
            checkbox.children[0].value = new_value
