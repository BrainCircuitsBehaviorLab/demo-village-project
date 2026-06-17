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

# ----------------------------SESSION REPORT PARSING FUNCTIONS-----------------------------------

def assign_ports(df: pd.DataFrame) -> pd.DataFrame:
    """Robustly assign left/right/centre poke ports based on system_name."""
    system_name = df['system_name'].iloc[0]
    port_map = {
        'box1': {
            'left_poke_in': 'Port1In',
            'left_poke_out': 'Port1Out',
            'centre_poke_in': 'Port2In',
            'centre_poke_out': 'Port2Out',
            'right_poke_in': 'Port3In',
            'right_poke_out': 'Port3Out',
        }
    }

    if system_name not in port_map:
        raise ValueError(f"Unsupported system_name: {system_name}")
    
    mapping = port_map[system_name]

    for new_col, source_col in mapping.items():
        if source_col in df.columns:
            df[new_col] = df[source_col]
        else:
            print(f"[assign_ports] Warning: column '{source_col}' not found in DataFrame. Skipping '{new_col}'.")

    return df


def extract_first_float(val):
            if isinstance(val, str) and val.startswith("[") and val.endswith("]"):
                try:
                    return float(ast.literal_eval(val)[0])
                except Exception:
                    return None
            try:
                return float(val) 
            except:
                return None
    
def extract_first_from_list_string(val):
            if isinstance(val, str):
                try:
                    parsed = ast.literal_eval(val) 
                    if isinstance(parsed, list) and len(parsed) > 0:
                        return float(parsed[0])
                except Exception:
                    return None
            return None

def parse_data_S1_S2(df: pd.DataFrame) -> pd.DataFrame:
    """Parse and compute all S1/S2-related variables from raw trial dataframe."""

    # Basic durations
    df['trial_duration'] = df['TRIAL_END'] - df['TRIAL_START']
    df['sum_s_trial_duration'] = df['trial_duration'].sum()
    df['session_duration'] = df['sum_s_trial_duration'].iloc[0] / 60

    # Time parsing
    for col in [
        'STATE_iti_START', 'STATE_iti_END',
        'STATE_led_on_START', 'STATE_led_on_END',
        'STATE_water_delivery_START', 'STATE_water_delivery_END'
    ]:
        if col in df:
            df[col] = df[col].apply(extract_first_float)
        else:
            print(f"[parse_data] Warning: column '{col}' not found, skipping.")

    # Durations and latencies
    df['duration_iti'] = df.get('STATE_iti_END', 0) - df.get('STATE_iti_START', 0)
    df['duration_led_on'] = df.get('STATE_led_on_END', 0) - df.get('STATE_led_on_START', 0)
    df['reaction_time'] = df.get('STATE_led_on_END', 0) - df.get('STATE_led_on_START', 0)


    # Outcome
    if 'rewarded_side' in df:
        df["correct_outcome_bool"] = df["response_side"] == df['rewarded_side']
        df['true_count'] = df['correct_outcome_bool'].value_counts().get(True, 0)
        df["correct_outcome"] = np.where(df["correct_outcome_bool"], "correct", "incorrect")
        df["correct_outcome_int"] = np.where(df["correct_outcome_bool"], 1, 0)
    else:
        print("[parse_data] Warning: 'rewarded_side' column not found, skipping outcome computation.")
        df["correct_outcome_bool"] = False
        df["correct_outcome"] = "unknown"
        df["correct_outcome_int"] = 0
        df['true_count'] = 0

    # Summary stats
    df['reaction_time_median'] = df['reaction_time'].median()
    df['tot_correct_choices'] = df['correct_outcome_int'].sum()
    df['right_choices'] = (df['rewarded_side'] == 'right').sum() if 'rewarded_side' in df else 0
    df['left_choices'] = (df['rewarded_side'] == 'left').sum() if 'rewarded_side' in df else 0

    return df

def parse_licks(val):
    if isinstance(val, str):
        try:
            out = ast.literal_eval(val)
            return out if isinstance(out, list) else []
        except:
            return []
    elif isinstance(val, list):
        return val
    return []


def parse_S3_data(df: pd.DataFrame) -> pd.DataFrame:
    """Parse and compute all S3-related variables from raw trial dataframe."""
    # Basic durations
    df['trial_duration'] = df['TRIAL_END'] - df['TRIAL_START']
    df['sum_s_trial_duration'] = df['trial_duration'].sum()
    df['session_duration'] = df['sum_s_trial_duration'].iloc[0] / 60

    # Time parsing
    df['STATE_iti_START'] = df['STATE_iti_START'].apply(extract_first_float)
    df['STATE_iti_END'] = df['STATE_iti_END'].apply(extract_first_float)
    df['STATE_c_led_on_START'] = df['STATE_c_led_on_START'].apply(extract_first_float)
    df['STATE_c_led_on_END'] = df['STATE_c_led_on_END'].apply(extract_first_float)
    df['STATE_side_led_on_START'] = df['STATE_side_led_on_START'].apply(extract_first_float)
    df['STATE_side_led_on_END'] = df['STATE_side_led_on_END'].apply(extract_first_float)
    df['STATE_water_delivery_START'] = df['STATE_water_delivery_START'].apply(extract_first_float)
    df['STATE_water_delivery_END'] = df['STATE_water_delivery_END'].apply(extract_first_float)

    # Durations and latencies
    df['duration_iti'] = df['STATE_iti_END'] - df['STATE_iti_START']
    df['motor_time'] = df['STATE_side_led_on_END'] - df['STATE_side_led_on_START']
    df['reaction_time'] = df['STATE_c_led_on_END'] - df['STATE_c_led_on_START']  # or water_delivery if appropriate

    # Outcome
    df["correct_outcome_bool"] = df["response_side"] == df['rewarded_side']
    df['true_count'] = df['correct_outcome_bool'].value_counts().get(True, 0)
    df["correct_outcome"] = np.where(df["response_side"] == df['rewarded_side'], "correct", "incorrect")
    df["correct_outcome_int"] = np.where(df["response_side"] == df['rewarded_side'], 1, 0)

    # Summary stats
    df['reaction_time_median'] = df['reaction_time'].median()
    df['tot_correct_choices'] = df['correct_outcome_int'].sum()
    df['right_choices'] = (df['rewarded_side'] == 'right').sum()
    df['left_choices'] = (df['rewarded_side'] == 'left').sum()
    return df


def parse_S4_data(df: pd.DataFrame) -> pd.DataFrame:
    """Parse and compute all S4-related variables from raw trial dataframe."""
    # Basic durations
    if "response_side" not in df.columns and "c" in df.columns:
        df = df.rename(columns={"c": "response_side"})

    df['trial_duration'] = df['TRIAL_END'] - df['TRIAL_START']
    df['sum_s_trial_duration'] = df['trial_duration'].sum()
    df['session_duration'] = df['sum_s_trial_duration'].iloc[0] / 60

    # Time parsing
    df['STATE_iti_START'] = df['STATE_iti_START'].apply(extract_first_float)
    df['STATE_iti_END'] = df['STATE_iti_END'].apply(extract_first_float)
    df['STATE_c_led_on_START'] = df['STATE_c_led_on_START'].apply(extract_first_float)
    df['STATE_c_led_on_END'] = df['STATE_c_led_on_END'].apply(extract_first_float)
    df['STATE_side_led_on_START'] = df['STATE_side_led_on_START'].apply(extract_first_float)
    df['STATE_side_led_on_END'] = df['STATE_side_led_on_END'].apply(extract_first_float)
    df['STATE_water_delivery_START'] = df['STATE_water_delivery_START'].apply(extract_first_float)
    df['STATE_water_delivery_END'] = df['STATE_water_delivery_END'].apply(extract_first_float)
    df['STATE_wrong_choice_START'] = df['STATE_wrong_choice_START'].apply(extract_first_float)
    df['STATE_wrong_choice_END'] = df['STATE_wrong_choice_END'].apply(extract_first_float)
    df['STATE_timeout_START'] = df['STATE_timeout_START'].apply(extract_first_float)
    df['STATE_timeout_END'] = df['STATE_timeout_END'].apply(extract_first_float)

    # Durations and latencies
    df['duration_iti'] = df['STATE_iti_END'] - df['STATE_iti_START']
    df['motor_time'] = df['STATE_side_led_on_END'] - df['STATE_side_led_on_START']
    df['reaction_time'] = df['STATE_c_led_on_END'] - df['STATE_c_led_on_START']  # or water_delivery if appropriate

    # Outcome
    df["correct_outcome_bool"] = df["response_side"] == df['rewarded_side']
    df['true_count'] = df['correct_outcome_bool'].value_counts().get(True, 0)
    df["correct_outcome"] = np.where(df["response_side"] == df['rewarded_side'], "correct", "incorrect")
    df["correct_outcome_int"] = np.where(df["response_side"] == df['rewarded_side'], 1, 0)

    # Summary stats
    df['reaction_time_median'] = df['reaction_time'].median()
    df['tot_correct_choices'] = df['correct_outcome_int'].sum()
    df['right_choices'] = (df['rewarded_side'] == 'right').sum()
    df['left_choices'] = (df['rewarded_side'] == 'left').sum()
    return df

def probit(x, beta, alpha):
        # Probit function to generate the curve for the PC
        return 0.5 * (1 + erf((beta * x + alpha) / np.sqrt(2)))

def parse_S5_data(df: pd.DataFrame) -> pd.DataFrame:
    """Parse and compute all S5-related variables from raw trial dataframe."""
    # Basic durations
    if "response_side" not in df.columns and "c" in df.columns:
        df = df.rename(columns={"c": "response_side"})

    df['trial_duration'] = df['TRIAL_END'] - df['TRIAL_START']
    df['sum_s_trial_duration'] = df['trial_duration'].sum()
    df['session_duration'] = df['sum_s_trial_duration'].iloc[0] / 60

    # Time parsing
    df['STATE_iti_START'] = df['STATE_iti_START'].apply(extract_first_float)
    df['STATE_iti_END'] = df['STATE_iti_END'].apply(extract_first_float)
    df['STATE_c_led_on_START'] = df['STATE_c_led_on_START'].apply(extract_first_float)
    df['STATE_c_led_on_END'] = df['STATE_c_led_on_END'].apply(extract_first_float)
    df['STATE_first_side_led_START'] = df['STATE_first_side_led_START'].apply(extract_first_float)
    df['STATE_first_side_led_END'] = df['STATE_first_side_led_END'].apply(extract_first_float)
    df['STATE_both_side_leds_START'] = df['STATE_both_side_leds_START'].apply(extract_first_float)
    df['STATE_both_side_leds_END'] = df['STATE_both_side_leds_END'].apply(extract_first_float)

    df['STATE_correct_choice_START'] = df['STATE_correct_choice_START'].apply(extract_first_float)
    df['STATE_correct_choice_END'] = df['STATE_correct_choice_END'].apply(extract_first_float)
    df['STATE_wrong_choice_START'] = df['STATE_wrong_choice_START'].apply(extract_first_float)
    df['STATE_wrong_choice_END'] = df['STATE_wrong_choice_END'].apply(extract_first_float)
    df['STATE_timeout_START'] = df['STATE_timeout_START'].apply(extract_first_float)
    df['STATE_timeout_END'] = df['STATE_timeout_END'].apply(extract_first_float)

    # Durations and latencies
    #df['duration_iti'] = df['STATE_iti_END'] - df['STATE_iti_START']
    if (
        'STATE_iti_START' in df.columns and
        'STATE_iti_END' in df.columns
    ):

        df['duration_iti'] = (
            df['STATE_iti_END']
            - df['STATE_iti_START']
        )
    else:
        df['duration_iti'] = np.nan
    df['motor_time'] = df['first_trial_response_time'] - df['STATE_first_side_led_START']
    df['reaction_time'] = df['STATE_c_led_on_END'] - df['STATE_c_led_on_START']  # or water_delivery if appropriate

    # Outcome
    df["correct_outcome_bool"] = df["response_side"] == df['rewarded_side']
    df['true_count'] = df['correct_outcome_bool'].value_counts().get(True, 0)
    df["correct_outcome"] = np.where(df["response_side"] == df['rewarded_side'], "correct", "incorrect")
    df["correct_outcome_int"] = np.where(df["response_side"] == df['rewarded_side'], 1, 0)

    # Summary stats
    df['reaction_time_median'] = df['reaction_time'].median()
    df['tot_correct_choices'] = df['correct_outcome_int'].sum()
    df['right_choices'] = (df['rewarded_side'] == 'right').sum()
    df['left_choices'] = (df['rewarded_side'] == 'left').sum()
    return df


