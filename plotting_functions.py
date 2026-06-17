# ---------------------------- IMPORTS------------------------------------------------------------
import numpy as np
import pandas as pd
import ast
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.gridspec as gridspec
from scipy.special import erf
from scipy.optimize import curve_fit
from matplotlib.patches import Patch
from session_parsing_functions import *
import math
from matplotlib.lines import Line2D
from utils_functions import get_delay_probabilities

# ----------------------------SESSION REPORT PLOTTING FUNCTIONS-----------------------------------

#PLOT used to represent S1 and S2 sessions
import matplotlib.pyplot as plt
from matplotlib import gridspec

def setup_figure_grid_S1_S2(ncols=3, nrows=3, height_ratios=[0.1, 1, 1], width_ratios=[1, 1, 0.3], figsize=(10, 8)):
    """
    Create a matplotlib figure with a configured GridSpec and font settings.

    Args:
        ncols (int): Number of columns in the grid.
        nrows (int): Number of rows in the grid.
        height_ratios (list): List of relative heights for each row.
        width_ratios (list): List of relative widths for each column.
        figsize (tuple): Size of the figure in inches (width, height).

    Returns:
        fig (Figure): The matplotlib Figure object.
        gs (GridSpec): The GridSpec object to place subplots.
    """
    # Update global font settings
    plt.rcParams.update({'font.size': 6, 'font.family': 'monospace'})

    # Create the figure
    fig = plt.figure(figsize=figsize)

    # Create a GridSpec layout with the specified rows, columns, and ratios
    gs = gridspec.GridSpec(
        nrows=nrows,
        ncols=ncols,
        figure=fig,
        height_ratios=height_ratios,
        width_ratios=width_ratios
    )

    return fig, gs

def plot_session_summary(ax, df):
    """
    Display a text summary of the session on the given matplotlib axis.

    Args:
        ax (matplotlib.axes.Axes): The axis where the summary will be plotted.
        df (pd.DataFrame): DataFrame containing session data.

    Returns:
        None
    """
    # Compute session stats
    n_trials = len(df)
    n_correct = df['correct_outcome_int'].sum()
    pct_correct = round(n_correct / n_trials * 100, 2)
    n_left = (df['response_side'] == 'left').sum()
    n_right = (df['response_side'] == 'right').sum()
    n_omit = (df['outcome'] == 'omission').sum()
    n_miss = (df['outcome'] == 'miss').sum()
    rt_median = round(df['reaction_time'].median(), 2)
    session_duration_min = round(df['session_duration'].iloc[0], 1)

    # Create the summary string
    summary_text = (
        f"Total trials: {n_trials} | Session: {session_duration_min} min | "
        f"Correct: {n_correct} ({pct_correct}%) | Left: {n_left} | Right: {n_right} | "
        f"Omissions: {n_omit} | Misses: {n_miss} | Median RT: {rt_median} s"
    )

    # Disable axis and display the text
    ax.axis("off")
    ax.text(0, 0.5, summary_text, fontsize=8, va='center', ha='left', family='monospace')

def plot_first_poke_side(ax, df):
    """Plot first poke side by outcome on the given axis."""
    response_map = {"left": -1, "right": 1, "none": 0}
    df["first_trial_response_num"] = df["response_side"].map(response_map)

    df['outcome_labels'] = np.where(df['correct_outcome_int'] == 1, 'correct',
                                    np.where(df['correct_outcome_int'].isna(), 'unknown', 'incorrect'))

    sns.scatterplot(
        data=df,
        x="trial",
        y="first_trial_response_num",
        hue="outcome_labels",
        palette={"correct": "black", "incorrect": "red", "unknown": "gray"},
        s=50,
        ax=ax,
    )
    ax.set_yticks([-1, 0, 1])
    ax.set_yticklabels(["Left", "omission", "Right"])
    ax.set_title("First poke (side)")
    ax.set_xlabel("Trial")
    ax.set_ylabel("First response (side)")
    ax.legend(title="Outcome")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

def plot_lick_raster_with_states(ax, df, fig):
            """
            Plot a lick raster aligned to TRIAL_START, with state phases as colored bands.
            Green = left licks, Purple = right licks.
            Lightblue = LED ON, Orange = Drink Delay, Lightgreen = Water Delivery.
            """

            left_raster_trials = []
            left_raster_times = []
            right_raster_trials = []
            right_raster_times = []

            for i, row in df.iterrows():
                try:
                    trial = row['trial']
                    t0 = row['TRIAL_START']

                    # --- LICK TIME  ---
                    left_licks = [lick - t0 for lick in parse_licks(row['left_poke_in'])]
                    right_licks = [lick - t0 for lick in parse_licks(row['right_poke_in'])]

                    left_raster_trials.extend([trial] * len(left_licks))
                    left_raster_times.extend(left_licks)
                    right_raster_trials.extend([trial] * len(right_licks))
                    right_raster_times.extend(right_licks)

                    # --- PHASES (relative to TRIAL_START) ---
                    led_on_start = row['STATE_led_on_START'] - t0
                    led_on_end = row['STATE_led_on_END'] - t0
                    # drink_start = row['STATE_iti_START'] - t0
                    # drink_end = row['STATE_iti_END'] - t0
                    reward_start = row['STATE_water_delivery_START'] - t0
                    reward_end = row['STATE_water_delivery_END'] - t0

                    # --- COLORED BANDS PER TRIAL ---
                    ax.fill_betweenx([trial - 0.4, trial + 0.4], led_on_start, led_on_end,
                                    color='orange', alpha=0.15, zorder=1, edgecolor=None)
                    # ax.fill_betweenx([trial - 0.4, trial + 0.4], drink_start, drink_end,
                    #                 color='orange', alpha=0.3, zorder=1)
                    ax.fill_betweenx([trial - 0.4, trial + 0.4], reward_start, reward_end,
                                    color='red', alpha=0.5, zorder=1)

                except Exception as e:
                    print(f"Errore al trial {i}: {e}")
                    continue

            # --- PLOT LICKS ---
            ax.scatter(left_raster_times, left_raster_trials, marker='|', color='#76B7D2',s=60, alpha=1.0, linewidths=0.5, label='Left lick', zorder=10)
            ax.scatter(right_raster_times, right_raster_trials, marker='|', color='#F28E2B', s=60,  alpha=1.0, linewidths=0.5, label='Right lick',  zorder=10)

            # Legend for states
            state_legend = [
                Patch(facecolor='orange', alpha=0.3, label='side led ON'),
                # Patch(facecolor='orange', alpha=0.3, label='ITI'),
                Patch(facecolor='red', alpha=0.5, label='Reward')
            ]

            # Legend for licks
            lick_legend = [
                Patch(color='#76B7D2', label='Left lick'),
                Patch(color='#F28E2B', label='Right lick')
            ]

            # Combine and place legend outside bottom-right
            ax.legend(handles=state_legend + lick_legend,
                    loc='lower right',
                    bbox_to_anchor=(1.75, -0.1),
                    fontsize=6,
                    frameon=False)

            ax.set_title("Lick raster (aligned to trial start)")
            ax.set_xlabel("Time from trial start (s)")
            ax.set_ylabel("Trial")
            ax.set_xlim(left=0)
            ax.set_ylim(df['trial'].min() - 1, df['trial'].max() + 1)
            ax.invert_yaxis()
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

def plot_trial_progression(ax, df):
    """Plot trial progression over time on the given axis."""
    df['min_from_session_start'] = (df['TRIAL_START'] - df['TRIAL_START'].iloc[0]) / 60
    colors = df["water"].map({
        0: "red",
        2: "orange",
        5: "green"
    }).fillna("gray")
    ax.plot(df["min_from_session_start"], df["trial"], label="Trial", color='black')
    ax.scatter(df["min_from_session_start"], df["trial"], color=colors, s=20)
    ax.set_title("Trial progression over time")
    ax.set_xlabel("mins from session start")
    ax.set_ylabel("Trial number")
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='0 µL',
            markerfacecolor='red', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='2 µL',
            markerfacecolor='orange', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='5 µL',
            markerfacecolor='green', markersize=8),
        # Line2D([0], [0], marker='o', color='w', label='Other/NaN',
        #     markerfacecolor='gray', markersize=8),
    ]
    ax.legend(handles=legend_elements, title="Water reward")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

def plot_rolling_accuracy(ax, df, window=5):
    """Plot rolling accuracy (%) over trials on the given axis."""
    df['rolling_accuracy'] = df['correct_outcome_int'].rolling(window=window, min_periods=1).mean() * 100

    ax.plot(df['trial'], df['rolling_accuracy'], color='blueviolet', linestyle='-',
            linewidth=2, marker='o', markersize=4)
    ax.axhline(y=50, color='black', linestyle='--')
    ax.set_yticks([0, 50, 100])
    ax.set_xlabel("Trial")
    ax.set_ylabel("%")
    ax.set_title("Trials accuracy (rolling average)")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

def plot_reaction_time(ax, df):
    """Plot reaction time (RT) over trials on a log scale."""
    ax.plot(df['trial'], df['reaction_time'], color='dodgerblue', linewidth=2, markersize=8)

    # Log scale for y-axis
    ax.set_yscale('log')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:g}'.format(y)))

    # Titles and labels
    ax.set_title('Reaction time (RT)')
    ax.set_xlabel('Trial')
    ax.set_ylabel('Latency to poke (s)')

    # Horizontal grid lines at specific tick values
    custom_yticks = [1, 10, 100]
    for y in custom_yticks:
        ax.axhline(y=y, linestyle='--', color='lightgray', alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

def plot_rolling_accuracy_and_p(df, ax=None, window=5):
    df['rolling_accuracy'] = (
        df['correct_outcome_int']
        .rolling(window=window, min_periods=1)
        .mean() * 100)
    ax.plot(df['trial'], df['rolling_accuracy'],
            color='blueviolet', linewidth=2,
            marker='o', markersize=4, label='Accuracy')
    ax.axhline(50, color='black', linestyle='--')
    ax.set(xlabel='Trial', ylabel='Accuracy (%)',
           ylim=(0, 100), yticks=[0, 50, 100],
           title='Trials accuracy and difficulty')
    ax.spines[['top', 'right']].set_visible(False)

    ax2 = ax.twinx()
    ax2.plot(df['trial'], df['p'],
             color='mediumturquoise', linewidth=2,
             marker='o', markersize=4, label='p')
    ax2.set(ylabel='p', ylim=(0, 1), yticks=[0, 0.5, 1])
    ax2.spines['top'].set_visible(False)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc='upper right',
              fontsize=6, frameon=False)

def plot_delay_probabilities(ax, df, curve_power=2):

    trials = df['trial'].values
    p_values = df['p'].values
    chosen = df['delay_cues'].values

    base, _ = get_delay_probabilities(p_values[0], curve_power)
    delays = np.r_[ -base[::-1], base ]
    n = len(delays)

    prob_matrix = np.zeros((len(trials), n))

    for i, p in enumerate(p_values):
        _, pr = get_delay_probabilities(p, curve_power)
        prob_matrix[i] = np.r_[ pr[::-1], pr ] / 2

    def bin_idx(x): return np.argmin(np.abs(delays - x))
    y = [bin_idx(d) for d in chosen]

    im = ax.imshow(prob_matrix.T, aspect='auto', origin='lower', cmap='Blues')
    ax.scatter(trials, y, s=8, c='grey', alpha=0.7)

    ax.set(yticks=range(n),
           yticklabels=["∞" if abs(d) >= 10000 else f"{d:.2f}" for d in delays],
           xlabel="Trial", ylabel="Signed delay")

    ax.spines[['top', 'right']].set_visible(False)
    plt.colorbar(im, ax=ax, label="Probability")


# #PLOT used to represent S3 and S4 sessions
# def plot_right_reward_probability(df, ax=None):
#     """Plot the probability of right reward over trials."""
#     if ax is None:
#         fig, ax = plt.subplots(figsize=(10, 4))
#     df = df.replace(np.nan, 0)

#     df['rolling_prob'] = df['correct_outcome_int'].rolling(window=5, min_periods=1).mean()
#     df['right_rewards'] = ((df['rewarded_side'] == 'right') & (df['correct_outcome_int'] == 1)).astype(int)
#     df['rolling_avg_right_reward'] = df["right_rewards"].rolling(window=5, min_periods=1).mean()

#     df["first_resp_left"] = (df["response_side"] == "left").astype(int)
#     df["first_resp_right"] = (df["response_side"] == "right").astype(int)
#     df["omission"] = (df["outcome"] == "omission").astype(int)
#     df["miss"] = (df["outcome"] == "miss").astype(int)


#     # --- Plot rolling prob curve ---
#     ax.plot(df["trial"], df["rolling_avg_right_reward"], color='mediumturquoise', linewidth=1, label='Rolling P(right reward)', linestyle='-')
#     ax.plot(df["trial"], df["rolling_prob"], color='black', linewidth=1, linestyle='--', label= 'Rolling accuracy')
#     ax.set_ylim(-0.5, 1.5)
#     ax.set_yticks([0, 0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 1])
#     ax.axhline(0.5, linestyle='--', color='lightgray', alpha=0.7)
#     ax.axhline(0, linestyle='solid', color='black', alpha=0.7)
#     ax.axhline(1, linestyle='solid', color='black', alpha=0.7)

#     # --- Plot ticks ---
#     for i, row in df.iterrows():
#         if row["first_resp_right"]:
#             markersize = 15 if row["correct_outcome_int"] == 1 else 5
#             ax.plot(i + 1, 1.15 if markersize == 15 else 1.35, '|', color='purple', markersize=markersize)
#         if row["first_resp_left"]:
#             markersize = 15 if row["correct_outcome_int"] == 1 else 5
#             ax.plot(i + 1, -0.15 if markersize == 15 else -0.35, '|', color='green', markersize=markersize)
#         if row["omission"]:
#             ax.plot(i + 1, 0.5, 'o', color='black', markersize=5)
#         if row["miss"]:
#             ax.plot(i + 1, -0.35, 'o', color='black', markersize=5)

#     # --- SIDE LABLES ---
#     ax.text(1.02, 0.1, 'L', ha='left', va='top', color='green', transform=ax.transAxes, fontsize=10)
#     ax.text(1.02, 0.9, 'R', ha='left', va='bottom', color='purple', transform=ax.transAxes, fontsize=10)
#     ax.text(1.02, 0.455, 'C', ha='left', va='bottom', color='black', transform=ax.transAxes, fontsize=10)

#     #----- legend -----
#     ax.legend(loc='lower right', fontsize=7, frameon=False)
#     # --- x axis ---
#     selected_trials = df["trial"][::19]
#     ax.set_xticks(selected_trials)
#     ax.set_xticklabels(selected_trials)
#     ax.set_xlabel("Trial")
#     ax.set_ylabel("P(right)")
#     ax.set_title("Rolling accuracy for right-side rewards")
#     ax.spines['top'].set_visible(False)
#     ax.spines['right'].set_visible(False)
#     return ax

def plot_latency_to_first_poke(df, ax=None):
    """
    Plot latency to the first correct poke (side and centre) with log y-scale.

    Parameters:
    - df: pandas DataFrame, deve contenere le colonne 'trial', 'side_response_latency', 'centre_response_latency'
    - ax: matplotlib axis object, opzionale. Se None, ne crea uno.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(df.trial, df.motor_time, color='dodgerblue', label='MT', linewidth=1)
    ax.plot(df.trial, df.reaction_time, color='black', label='RT', linewidth=1)

    # Y log scale and ticks
    custom_yticks = [0.1, 1, 10, 20, 50, 100, 200, 300]
    ax.set_yscale('log')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:g}'.format(y)))
    for y in custom_yticks:
        ax.axhline(y=y, linestyle='--', color='lightgray', alpha=0.7)

    ax.set_title('Latency to first correct poke')
    ax.set_xlabel('Trial')
    ax.set_ylabel('Latency (s)')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # Legend
    ax.legend(loc='upper right', bbox_to_anchor=(1, -0.2), ncol=2, frameon=False)

    return ax

def plot_lick_raster_with_states_S3(ax, df, fig):
            """
            Plot a lick raster aligned to TRIAL_START, with state phases as colored bands.
            Green = left licks, Purple = right licks.
            Lightblue = LED ON, Orange = Drink Delay, Lightgreen = Water Delivery.
            """

            left_raster_trials = []
            left_raster_times = []
            centre_raster_trials = []
            centre_raster_times = []
            right_raster_trials = []
            right_raster_times = []

            for i, row in df.iterrows():
                try:
                    trial = row['trial']
                    t0 = row['TRIAL_START']

                    # --- LICK TIME  ---
                    left_licks = [lick - t0 for lick in parse_licks(row['left_poke_in'])]
                    centre_licks = [lick - t0 for lick in parse_licks(row['centre_poke_in'])]
                    right_licks = [lick - t0 for lick in parse_licks(row['right_poke_in'])]

                    left_raster_trials.extend([trial] * len(left_licks))
                    left_raster_times.extend(left_licks)
                    centre_raster_trials.extend([trial] * len(centre_licks))
                    centre_raster_times.extend(centre_licks)
                    right_raster_trials.extend([trial] * len(right_licks))
                    right_raster_times.extend(right_licks)

                    # --- PHASES (relative to TRIAL_START) ---
                    c_led_on_start = row['STATE_c_led_on_START'] - t0
                    c_led_on_end = row['STATE_c_led_on_END'] - t0
                    side_led_on_start = row['STATE_side_led_on_START'] - t0
                    side_led_on_end = row['STATE_side_led_on_END'] - t0
                    drink_start = row['STATE_drink_delay_START'] - t0
                    drink_end = row['STATE_drink_delay_END'] - t0
                    reward_start = row['STATE_water_delivery_START'] - t0
                    reward_end = row['STATE_water_delivery_END'] - t0
                    penalty_start = row['STATE_water_delivery_START'] - t0
                    penalty_end = row['STATE_water_delivery_END'] - t0

                    # --- COLORED BANDS PER TRIAL ---
                    ax.fill_betweenx([trial - 0.4, trial + 0.4], c_led_on_start, c_led_on_end,
                                    color='yellow', alpha=0.3, zorder=1)
                    ax.fill_betweenx([trial - 0.4, trial + 0.4], side_led_on_start, side_led_on_end,
                                    color='lightblue', alpha=0.3, zorder=1)
                    ax.fill_betweenx([trial - 0.4, trial + 0.4], drink_start, drink_end,
                                    color='orange', alpha=0.3, zorder=1)
                    ax.fill_betweenx([trial - 0.4, trial + 0.4], penalty_start, penalty_end,
                                    color='red', alpha=0.3, zorder=1)
                    ax.fill_betweenx([trial - 0.4, trial + 0.4], reward_start, reward_end,
                                    color='lightgreen', alpha=0.3, zorder=1)

                except Exception as e:
                    print(f"Errore al trial {i}: {e}")
                    continue

            # --- PLOT LICKS ---
            ax.scatter(left_raster_times, left_raster_trials, marker='|', color='#76B7D2',s=60, alpha=1.0, linewidths=0.5, label='Left lick', zorder=10)
            ax.scatter(right_raster_times, right_raster_trials, marker='|', color='#F28E2B', s=60,  alpha=1.0, linewidths=0.5, label='Right lick',  zorder=10)
            ax.scatter(centre_raster_times, centre_raster_trials, marker='|', color='grey', s=60,  alpha=1.0, linewidths=0.5, label='Centre lick',  zorder=10)

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            ax.set_title("Lick raster (aligned to trial start)")
            ax.set_xlabel("Time from trial start (s)")
            ax.set_ylabel("Trial")
            ax.set_xlim(left=0)
            ax.set_ylim(df['trial'].min() - 1, df['trial'].max() + 1)
            ax.invert_yaxis()

def plot_lick_raster_with_states_S3_S4(ax, df, fig=None):
    """
    Plot a lick raster aligned to TRIAL_START with trial on x-axis and time on y-axis.
    Green = left licks, Purple = right licks, Gray = center licks.
    Background bands: Yellow = center LED, Lightblue = side LED, Orange = drink delay, Red = penalty, Lightgreen = reward.
    """

    left_raster_trials, left_raster_times = [], []
    centre_raster_trials, centre_raster_times = [], []
    right_raster_trials, right_raster_times = [], []

    for i, row in df.iterrows():
        try:
            trial = row['trial']
            t0 = row['TRIAL_START']

            # Lick times relative to trial start
            left_licks = [lick - t0 for lick in parse_licks(row.get('left_poke_in', ''))]
            centre_licks = [lick - t0 for lick in parse_licks(row.get('centre_poke_in', ''))]
            right_licks = [lick - t0 for lick in parse_licks(row.get('right_poke_in', ''))]

            left_raster_trials.extend([trial] * len(left_licks))
            left_raster_times.extend(left_licks)
            centre_raster_trials.extend([trial] * len(centre_licks))
            centre_raster_times.extend(centre_licks)
            right_raster_trials.extend([trial] * len(right_licks))
            right_raster_times.extend(right_licks)

            # Phases
            def rel(key):
                return row.get(key, t0) - t0

            bands = [
                (rel('STATE_c_led_on_START'), rel('STATE_c_led_on_END'), 'yellow', 'Center LED'),
                (rel('STATE_side_led_on_START'), rel('STATE_side_led_on_END'), 'orchid', 'Side LED'),
                (rel('STATE_drink_delay_START'), rel('STATE_drink_delay_END'), 'orange', 'ITI'),
                (rel('STATE_water_delivery_START'), rel('STATE_water_delivery_END'), 'blue', 'Reward'),
                (rel('STATE_penalty_START'), rel('STATE_penalty_END'), 'firebrick', 'Penalty')
            ]

            for start, end, color, _ in bands:
                ax.fill_between([trial - 0.4, trial + 0.4], start, end, color=color, alpha=0.3, zorder=1)

        except Exception as e:
            print(f"[Raster] Trial {i} skipped due to error: {e}")
            continue

    # Plot licks
    ax.scatter(left_raster_trials, left_raster_times, marker='_', color='#76B7D2', s=40, alpha=0.7, label='Left')
    ax.scatter(centre_raster_trials, centre_raster_times, marker='_', color='grey', s=40, alpha=0.7, label='Centre')
    ax.scatter(right_raster_trials, right_raster_times, marker='_', color='#F28E2B', s=40, alpha=0.7, label='Right')

    ax.set_xlabel("Trial")
    ax.set_ylabel("Time from trial start (s)")
    ax.set_title("Lick Raster (aligned to TRIAL_START)")
    ax.set_ylim(0, df['trial_duration'].max() + 1)
    ax.spines[['top', 'right']].set_visible(False)

    # Legend for licks
    lick_legend = [
        Patch(color='#76B7D2', label='Left'),
        Patch(color='#F28E2B', label='Right'),
        Patch(color='grey', label='Center')
    ]

    # Legend for states
    state_legend = [
        Patch(facecolor='yellow', alpha=0.5, label='Center LED'),
        Patch(facecolor='orchid', alpha=0.5, label='Side LED'),
        Patch(facecolor='orange', alpha=0.5, label='ITI'),
        Patch(facecolor='blue', alpha=0.5, label='Reward'),
        Patch(facecolor='firebrick', alpha=0.5, label='Penalty')
    ]

    all_handles = lick_legend + state_legend
    ax.legend(handles=all_handles, loc='center left', bbox_to_anchor=(0.99, 0.5),
              fontsize=6, frameon=False)


    return ax

def plot_lick_raster_with_states_S5(ax, df, fig=None):
    """
    Plot a lick raster aligned to TRIAL_START with trial on x-axis and time on y-axis.
    Green = left licks, Purple = right licks, Gray = center licks.
    Background bands: Yellow = center LED, Lightblue = side LED, Orange = drink delay, Red = penalty, Lightgreen = reward.
    """

    left_raster_trials, left_raster_times = [], []
    centre_raster_trials, centre_raster_times = [], []
    right_raster_trials, right_raster_times = [], []

    for i, row in df.iterrows():
        try:
            trial = row['trial']
            t0 = row['TRIAL_START']

            # Lick times relative to trial start
            left_licks = [lick - t0 for lick in parse_licks(row.get('left_poke_in', ''))]
            centre_licks = [lick - t0 for lick in parse_licks(row.get('centre_poke_in', ''))]
            right_licks = [lick - t0 for lick in parse_licks(row.get('right_poke_in', ''))]

            left_raster_trials.extend([trial] * len(left_licks))
            left_raster_times.extend(left_licks)
            centre_raster_trials.extend([trial] * len(centre_licks))
            centre_raster_times.extend(centre_licks)
            right_raster_trials.extend([trial] * len(right_licks))
            right_raster_times.extend(right_licks)

            # Phases
            def rel(key):
                return row.get(key, t0) - t0

            bands = [
                (rel('STATE_c_led_on_START'), rel('STATE_c_led_on_END'), 'yellow', 'Center LED'),
                (rel('STATE_side_led_on_START'), rel('first_trial_response_time'), 'orchid', 'Side LED'),
                (rel('STATE_iti_START'), rel('STATE_iti_END'), 'orange', 'ITI'),
                (rel('STATE_correct_choice_START'), rel('STATE_correct_choice_END'), 'blue', 'Reward'),
                (rel('STATE_penalty_START'), rel('STATE_penalty_END'), 'firebrick', 'Penalty')
            ]

            for start, end, color, _ in bands:
                ax.fill_between([trial - 0.4, trial + 0.4], start, end, color=color, alpha=0.3, zorder=1)

        except Exception as e:
            print(f"[Raster] Trial {i} skipped due to error: {e}")
            continue

    # Plot licks
    ax.scatter(left_raster_trials, left_raster_times, marker='_', color='#76B7D2', s=40, alpha=0.7, label='Left')
    ax.scatter(centre_raster_trials, centre_raster_times, marker='_', color='grey', s=40, alpha=0.7, label='Centre')
    ax.scatter(right_raster_trials, right_raster_times, marker='_', color='#F28E2B', s=40, alpha=0.7, label='Right')

    ax.set_xlabel("Trial")
    ax.set_ylabel("Time from trial start (s)")
    ax.set_title("Lick Raster (aligned to TRIAL_START)")
    ax.set_ylim(0, df['trial_duration'].max() + 1)
    ax.spines[['top', 'right']].set_visible(False)


    # Legend for licks
    lick_legend = [
        Patch(color='#76B7D2', label='Left'),
        Patch(color='#F28E2B', label='Right'),
        Patch(color='grey', label='Center')
    ]

    # Legend for states
    state_legend = [
        Patch(facecolor='yellow', alpha=0.5, label='Center LED'),
        Patch(facecolor='orchid', alpha=0.5, label='Side LED'),
        Patch(facecolor='orange', alpha=0.5, label='ITI'),
        Patch(facecolor='blue', alpha=0.5, label='Reward'),
        Patch(facecolor='firebrick', alpha=0.5, label='Penalty')
    ]

    all_handles = lick_legend + state_legend
    ax.legend(handles=all_handles, loc='center left', bbox_to_anchor=(0.99, 0.5),
              fontsize=6, frameon=False)


    return ax

def plot_iti_histogram(ax, df, bins=10):
    """
    Plot histogram of ITI durations.

    Parameters:
        ax : matplotlib.axes.Axes
            The axis to plot on.
        df : pd.DataFrame
            The dataframe containing the 'duration_iti' column.
        bins : int
            Number of histogram bins.
    """
    if 'post_trial_duration' not in df.columns:
        ax.text(0.5, 0.5, 'No ITI data', ha='center', va='center', fontsize=8)
        ax.set_axis_off()
        return

    iti_data = df['post_trial_duration'].dropna()

    ax.hist(iti_data, bins=bins, color='lightseagreen', edgecolor='black', alpha=0.8)
    ax.set_title("ITI duration histogram")
    ax.set_xlabel("ITI duration (s)")
    ax.set_ylabel("Number of trials")
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.spines[['top', 'right']].set_visible(False)

def plot_probability_right_reward_S4(df: pd.DataFrame, ax=None) -> plt.Axes:
    """
    Plot probability of right reward vs. actual right choices.
    Shows rolling average of right choices, expected probabilities,
    response ticks, and block-level structure.

    Parameters:
    - df: DataFrame with trial data.
    - ax: matplotlib axis to plot on (optional).

    Returns:
    - ax: matplotlib axis with the plot.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))

    # Clean & prepare
    df = df.copy()
    df = df.replace(np.nan, 0)

    # Rolling average of right choices
    df["right_choice"] = (df["response_side"] == "right").astype(int)
    df["rolling_avg_right"] = df["right_choice"].rolling(window=5, min_periods=1).mean()

    # Plot expected probability of reward
    ax.plot(df["trial"], df["probability_r"], label=" P(reward on right)",
            color="black", linewidth=1, alpha=0.7)

    # Plot actual right choices rolling average
    ax.plot(df["trial"], df["rolling_avg_right"], label="Right choice frequency",
            color="mediumturquoise", linewidth=2)

    df["first_resp_left"] = (df["response_side"] == "left").astype(int)
    df["first_resp_right"] = (df["response_side"] == "right").astype(int)
    df["omission"] = (df["outcome"] == "omission").astype(int)
    df["miss"] = (df["outcome"] == "miss").astype(int)

    # # Plot response ticks (green = left, purple = right)
    # for i, row in df.iterrows():
    #     correct = row["correct_outcome_int"] == 1
    #     if row["response_side"] == "right":
    #         ax.plot(row["trial"], -0.15 if correct else -0.35, '|', color="green", markersize=15 if correct else 5)
    #     elif row["response_side"] == "left":
    #         ax.plot(row["trial"], 1.15 if correct else 1.35, '|', color="purple", markersize=15 if correct else 5)

   # --- Plot ticks ---
    for i, row in df.iterrows():


        if row["first_resp_right"]:
            markersize = 15 if row["correct_outcome_int"] == 1 else 5
            tick_color = "purple"
            ax.plot(i + 1, 1.15 if markersize == 15 else 1.35, '|',
                    color=tick_color, markersize=markersize)

        if row["first_resp_left"]:
            markersize = 15 if row["correct_outcome_int"] == 1 else 5
            tick_color = "green"
            ax.plot(i + 1, -0.15 if markersize == 15 else -0.35, '|',
                    color=tick_color, markersize=markersize)

        if row["omission"]:
            ax.plot(i + 1, 0.5, 'o', color='black', markersize=5)

        if row["miss"]:
            ax.plot(i + 1, -0.35, 'o', color='black', markersize=5)

    # Draw block probability bars
    if "Block_index" in df.columns:
        unique_blocks = df["Block_index"].unique()
        for block in unique_blocks:
            block_data = df[df["Block_index"] == block]
            start, end = block_data["trial"].min(), block_data["trial"].max()
            block_prob = block_data["probability_r"].iloc[0]
            color = "purple" if block_prob > 0.5 else "green" if block_prob < 0.5 else "blue"
            ax.hlines(y=1.7, xmin=start, xmax=end, colors=color, linewidth=10)
            ax.text((start + end) / 2, 1.6, f"{block_prob:.2f}", ha="center", va="center",
                    fontsize=6, backgroundcolor="white")

        # Vertical lines for block changes
        changes = df["Block_index"].diff().fillna(0).ne(0)
        for trial in df[changes]["trial"]:
            ax.axvline(x=trial-0.5, color="gray", linestyle="--")

    # Axes formatting
    ax.set_ylim(-0.5, 1.7)
    ax.set_yticks([0, 0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 1])
    ax.axhline(y=0.5, linestyle="--", color="lightgray", alpha=0.7)
    ax.axhline(y=0, linestyle="solid", color="black", alpha=0.7)
    ax.axhline(y=1, linestyle="solid", color="black", alpha=0.7)

    # Labels
    ax.text(1.02, 0.1, "L", transform=ax.transAxes, color="#76B7D2", fontsize=10)
    ax.text(1.02, 0.9, "R", transform=ax.transAxes, color="#F28E2B", fontsize=10)
    ax.text(1.02, 0.46, "C", transform=ax.transAxes, color="grey", fontsize=10)

    # Title and axis
    ax.set_title("P(reward on right) vs. Choice (Rolling)")
    ax.set_xlabel("Trial")
    ax.set_ylabel("P(right)")
    ax.set_xticks(df["trial"][::20])
    ax.set_xticklabels(df["trial"][::20])

    # Legend
    ax.legend(loc="upper left")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return ax

# def plot_psychometric_curve(df, ax=None):
#     """Plot psychometric curve: proportion of right choices vs. delay."""
#     if ax is None:
#         fig, ax = plt.subplots(figsize=(4, 3))

#     # Ensure columns are float and clean
#     df = df.copy()
#     df = df[df['response_side'].isin(['left', 'right'])]
#     df['delay_cues'] = df['delay_cues'].astype(float)
#     df['first_trial_response_num'] = df['response_side'].apply(
#         lambda x: 1 if x == 'right' else 0
#     )

#     # Compute right choice rate per unique delay
#     delays = np.sort(df['delay_cues'].unique())
#     right_choice_freq = [
#         df[df['delay_cues'] == p]['first_trial_response_num'].mean()
#         for p in delays
#     ]

#     # Fit probit curve
#     try:
#         pars, _ = curve_fit(
#             probit,
#             df['delay_cues'],
#             df['first_trial_response_num'],
#             p0=[0, 1]
#         )
#     except RuntimeError:
#         pars = [0, 0]  # fallback if fitting fails

#     # Plot data points
#     ax.scatter(delays, right_choice_freq, color='indianred', s=20, label='Data')

#     # Plot fitted curve
#     x = np.linspace(0, 1, 100)
#     ax.plot(x, probit(x, *pars), color='indianred', linewidth=2, label='Probit Fit')

#     # Style
#     ax.set_ylim(0, 1)
#     ax.axhline(0.5, color='gray', linestyle='--')
#     ax.axvline(0.5, color='gray', linestyle='--')
#     ax.set_xlabel('Right reward probability')
#     ax.set_ylabel('Right choice rate')
#     ax.set_title('Psychometric curve')
#     ax.legend(loc='lower right', fontsize=6)
#     ax.spines['top'].set_visible(False)
#     ax.spines['right'].set_visible(False)

#     return ax


def plot_psychometric_curve(df, ax=None):
    """Plot psychometric curve: proportion of right choices vs. delay."""

    if ax is None:
        fig, ax = plt.subplots(figsize=(4, 3))

    df = df.copy()
    df = df[df['response_side'].isin(['left', 'right'])]
    df['delay_plot'] = df['delay_cues'].astype(float)
    df.loc[df['delay_plot'] <= -9999, 'delay_plot'] = -np.inf
    df.loc[df['delay_plot'] >= 9999, 'delay_plot'] = np.inf
    df['right_choice'] = (df['response_side'] == 'right').astype(int)

    delays = np.sort(df['delay_plot'].unique())
    right_choice_freq = [
        df[df['delay_plot'] == d]['right_choice'].mean()
        for d in delays ]

    fit_df = df[np.isfinite(df['delay_plot'])]
    if len(fit_df) < 5 or fit_df['delay_plot'].nunique() < 2:
        pars = [0, 1]
    else:
        try:
            pars, _ = curve_fit(
                probit,
                fit_df['delay_plot'],
                fit_df['right_choice'],
                p0=[0, 1],
                bounds=([-10, 0.1], [10, 10])
            )
        except Exception:
            pars = [0, 1]
    scatter = ax.scatter(
        delays,
        right_choice_freq,
        color='indianred',
        s=25,
        label='Data')

    finite = df['delay_plot'][np.isfinite(df['delay_plot'])]

    if len(finite) > 0:
        x_min, x_max = finite.min(), finite.max()
        x = np.linspace(x_min, x_max, 200)

        line, = ax.plot(
            x,
            probit(x, *pars),
            color='indianred',
            linewidth=2,
            label='Probit fit'
        )
    else:
        line, = ax.plot([], [], label='Probit fit')

    ax.set_ylim(0, 1)
    ax.axhline(0.5, color='gray', linestyle='--')
    ax.axvline(0, color='gray', linestyle='--')
    ax.set_xlabel('Delay (− left first, + right first)')
    ax.set_ylabel('Right choice rate')
    ax.set_title('Psychometric curve')
    ax.legend(handles=[scatter, line], loc='lower right', fontsize=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return ax
# ---------------------------------------------------------
# Helper: ON color depends on system_name
# ---------------------------------------------------------
def get_subject_group(subject_id: str) -> str:
    controls = {"C15", "C24", "C22"}
    egfp = {"C12", "C1", "C9", "C7"}

    sid = str(subject_id).strip().upper()
    if sid in controls:
        return "CONTROL"
    elif sid in egfp:
        return "EGFP"
    return "OPSIN"


def get_on_color(df, col="system_name"):
    """
    Returns ON color based on df[col] (system_name).
    11 & 8 -> blue
    12 & 9 -> red
    """
    if col not in df.columns or len(df) == 0:
        return "royalblue"

    sys_val = df[col].iloc[0]

    # normalize: could be '11', 11, 'system_11', etc.
    sys_id = None
    try:
        sys_id = int(sys_val)
    except Exception:
        # try extracting digits from string
        s = str(sys_val)
        digits = "".join(ch for ch in s if ch.isdigit())
        if digits != "":
            try:
                sys_id = int(digits)
            except Exception:
                sys_id = None

    if sys_id in (11, 8):
        return "royalblue"
    elif sys_id in (12, 9):
        return "firebrick"
    return "royalblue"


def plot_iti_histogram(ax, df, bins=10):
    if 'iti_duration' not in df.columns:
        ax.text(0.5, 0.5, 'No ITI data', ha='center', va='center', fontsize=8)
        ax.set_axis_off()
        return

    iti_data = df['iti_duration'].dropna()
    ax.hist(iti_data, bins=bins, color='lightseagreen', edgecolor='black', alpha=0.8)
    ax.set_title("ITI duration histogram")
    ax.set_xlabel("ITI duration (s)")
    ax.set_ylabel("Number of trials")
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.spines[['top', 'right']].set_visible(False)


def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    phat = k / n
    denom = 1 + (z**2) / n
    center = (phat + (z**2) / (2*n)) / denom
    half = (z * math.sqrt((phat*(1-phat) + (z**2)/(4*n)) / n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def compute_switch_rate_on_off(df):
    d = df.copy()
    d = d[d["response_side"].isin(["left", "right"])].copy()

    if "trial" in d.columns:
        d = d.sort_values("trial")

    d["prev_side"] = d["response_side"].shift(1)
    d["switch"] = (d["response_side"] != d["prev_side"]).astype(int)
    d = d.dropna(subset=["prev_side"]).copy()

    on_mask, off_mask = get_on_off_masks(d)

    on_switch = d.loc[on_mask, "switch"].values
    off_switch = d.loc[off_mask, "switch"].values

    out = {
        "on_rate": float(np.mean(on_switch)) if len(on_switch) else np.nan,
        "off_rate": float(np.mean(off_switch)) if len(off_switch) else np.nan,
        "on_n": int(len(on_switch)),
        "off_n": int(len(off_switch)),
        "on_switches": int(np.sum(on_switch)) if len(on_switch) else 0,
        "off_switches": int(np.sum(off_switch)) if len(off_switch) else 0,
    }
    return out
