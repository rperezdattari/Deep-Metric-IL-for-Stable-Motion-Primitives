from evaluation.evaluate import Evaluate
import pickle
import plotly.graph_objects as go
from agent.utils.dynamical_system_operations import denormalize_state
from scipy.spatial.transform import Rotation
import numpy as np


class Evaluate4DS3(Evaluate):
    """
    Class for evaluating three-dimensional dynamical systems
    """
    def __init__(self, learner, data, params, verbose=True):
        super().__init__(learner, data, params, verbose=verbose)

        self.show_plotly = params.show_plotly

    def compute_quali_eval(self, sim_results, attractor, primitive_id, iteration):
        """
        Computes qualitative results
        """
        save_path = self.learner.save_path + 'images/' + 'primitive_%i_iter_%i' % (primitive_id, iteration) + '.pickle'
        self.plot_DS_plotly(sim_results['visited states demos'], sim_results['visited states grid'], save_path)
        return True

    def compute_diffeo_quali_eval(self, sim_results, sim_results_latent, primitive_id, iteration):
        # Not implemented
        return False

    def plot_DS_plotly(self, visited_states, visited_states_grid, save_path):
        """
        Plots demonstrations and simulated trajectories when starting from demos initial states
        """
        plot_data = []

        # Denorm states
        denorm_visited_states_grid = denormalize_state(visited_states_grid, self.x_min, self.x_max)
        denorm_visited_states = denormalize_state(visited_states, self.x_min, self.x_max)

        # Map to euler angles
        rot = Rotation.from_quat(denorm_visited_states_grid.reshape(-1, 4))
        visited_states_grid_eul = rot.as_euler('xyz').reshape(-1, self.density**self.dim_manifold, 3)
        rot = Rotation.from_quat(denorm_visited_states.reshape(-1, 4))
        visited_states_eul = rot.as_euler('xyz').reshape(-1, self.n_trajectories, 3)
        demonstrations_eval_eul = []
        for i in range(self.n_trajectories):
            rot = Rotation.from_quat(self.demonstrations_eval[i].T)
            quat = rot.as_euler('xyz')
            demonstrations_eval_eul.append(quat.T)

        # Plot random trajectories
        for i in range(visited_states_grid.shape[1]):

            # Plot network executions
            marker_data_executed = go.Scatter3d(
                x=visited_states_grid_eul[:, i, 0],
                y=visited_states_grid_eul[:, i, 1],
                z=visited_states_grid_eul[:, i, 2],
                marker=go.scatter3d.Marker(size=3, color='blue'),
                line=dict(color='blue', width=10),
                opacity=0.1,
                mode='markers'
            )
            plot_data.append(marker_data_executed)

        for i in range(self.n_trajectories):

            # Plot datasets
            marker_data_demos = go.Scatter3d(
                x=demonstrations_eval_eul[i][0, :],
                y=demonstrations_eval_eul[i][1, :],
                z=demonstrations_eval_eul[i][2, :],
                marker=go.scatter3d.Marker(size=3, color='red'),
                opacity=0.5,
                mode='markers',
                name='demonstration %i' % i,
            )
            plot_data.append(marker_data_demos)

            # Plot network executions
            marker_data_executed = go.Scatter3d(
                x=visited_states_eul[:, i, 0],
                y=visited_states_eul[:, i, 1],
                z=visited_states_eul[:, i, 2],
                marker=go.scatter3d.Marker(size=3, color='green'),
                opacity=0.5,
                mode='markers',
                name='CONDOR %i' % i,
            )
            plot_data.append(marker_data_executed)

        layout = go.Layout(autosize=True,
                           scene=dict(
                               xaxis_title='x (m)',
                               yaxis_title='y (m)',
                               zaxis_title='z (m)'),
                           margin=dict(l=65, r=50, b=65, t=90),
                           showlegend=False,
                           font=dict(family='Time New Roman', size=15))
        fig = go.Figure(data=plot_data, layout=layout)

        plot_data = {'3D_plot': fig}

        # Save
        print('Saving image data to %s...' % save_path)
        pickle.dump(plot_data, open(save_path, 'wb'))

        if self.show_plotly:
            fig.show()

        return True
