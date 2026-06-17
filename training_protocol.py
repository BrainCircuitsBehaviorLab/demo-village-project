from village.custom_classes.training_protocol_base import TrainingProtocolBase

class TrainingProtocol(TrainingProtocolBase):
    """
    This class defines how the training protocol is going to be.
    This is, how variables change depending on different conditions (e.g. performance),
    and/or which tasks are going to be run.

    In this class 2 methods need to be implemented:
    - __init__
    - default_training_settings
    - update_training_settings

    In default_training_settings all the variables that can modify the state of
    the training protocol must be defined.
    In update_training_settings the variables are updated depeding on the
    performance of the animal.
    When a new subject is created, a new row is added to the data/subjects.csv file,
    with these variables and its values.

    The following variables are needed:
    - self.next_task
    - self.refractory_period
    - self.minimum_duration
    - self.maximum_duration
    In addition to these variables, all the necessary variables to modify the state
    of the tasks can be included.

    When a task is run the values of the variables are read from the json file.
    When the task ends, the values of the variables are updated in the json file,
    following the logic in the update method."""

    def __init__(self) -> None:
        super().__init__()

    def default_training_settings(self) -> None:
        """
        This method is called when a new subject is created.
        It sets the default values for the training protocol.
        """

        # Settings in this block are mandatory for everything
        # that runs on Traning Village
        # TODO
        self.settings.next_task = "S0"
        self.settings.refractory_period = 240 * 60 # 4 hours
        self.settings.minimum_duration = 10 * 60
        self.settings.maximum_duration =  15 * 60 #habituation lasts 15 mins

        # Settings in this block are dependent on each task,
        # and the user needs to create and define them here

        #S1
        self.settings.volume_early = 6
        #GENERAL SETTINGS
        self.settings.volume = 2 # ul of water delivered, bigger during habituation
        self.settings.volume_large = 5
        self.settings.led_intensity = 255 # led intensity (it's at maximum)

        #SHAPING SETTINGS:S1 AND S2
        self.settings.led_on_time =  5 * 60 # side led on in S1 and S2
        self.settings.iti_time = 1 #time to wait after the reward is delivered

        #SHAPING SETTINGS:S3
        self.settings.c_led_on_time = 5 * 60 # centre led on in S3
        self.settings.timeout =  3
        self.settings.noise_time = 1.5

        self.settings.curve_power = 2
        self.settings.p = 0
        self.settings.delay_values = [0, 0.1, 0.25, 0.5, 1, 10000]

        """
        TASK SETTINGS: Delayed Side-Cue Discriminaion Task – Deailed Description
        (S6 AND it's variations)
        --------------------------------------------------------------------------
        Task structure:
        Animals perform a 2-choice discrimination task based on which side LED turns ON first.

        TRIAL PARAMETERS:
        - Inter-cue delay: discrete values in [0, 0.48] s
        - Maximum response window: 40 s
        - ITI and timeout defined in settings

        NOTES:
        - Correct side is pre-generated per trial (first_led_side_vec).
        - Delay between cues is pre-generated per trial (inter_led_delay_vec).
        - Decision is based on FIRST poke after first LEDs is available.

        --------------------------------------------------------------------------
        VARIABLES
            - N_trials: max number of trials in the session
        """

        self.settings.N_trials = 1000

    def update_training_settings(self) -> None:
        """
        This method is called every time a session finishes.
        It is used to make the animal progress in the training protocol.

        For this example, we want the animal to go from S0 to S1
        after 2 sessions, as long as it completed overall more than 100 trials.
        We also want to decrease the reward amount during the first sessions.
        We promote the animals to the second training stage in S1
        when they do two consecutive sessions with over 85% performance.
        Note that in this case, they never go back to the easier task.
        """
        if self.last_task == "S0":
            df_S0 = self.df[self.df["task"] == "S0"]
            if len(df_S0) >= 1:
                self.settings.next_task = "S1"
                self.settings.minimum_duration = 25 * 60
                self.settings.maximum_duration = 45 * 60
            else:
                self.settings.next_task = "S0"


        elif self.last_task == "S1":
            df_S1 = self.df[self.df["task"] == "S1"]
            if len(df_S1) >= 2:
                df_last_two_session_s1 = df_S1.iloc[-2:]
                n_trials_S1 = df_last_two_session_s1.trial.sum()
                if n_trials_S1 >= 100:
                    self.settings.next_task = "S2"
                    self.settings.minimum_duration = 25 * 60
                    self.settings.maximum_duration = 45 * 60
                    self.settings.volume = 2
                    self.settings.volume_large = 5

                    #self.settings.trials_with_same_side = 20
                    self.settings.led_on_time = 300 #timeup
                    self.settings.iti_time = 1
                else:
                    self.settings.next_task = "S1"
            else:
                self.settings.next_task = "S1" # Keep in task until it meets the criteria

        elif self.last_task == "S2":
            df_S2 = self.df[self.df.task == "S2"]
            if len(df_S2) >= 2:
                df_last_two_session_S2 = df_S2.iloc[-2:]
                n_trials_S2 = df_last_two_session_S2.trial.sum()
                if n_trials_S2 >= 100:
                    self.settings.next_task = "S3"
                    self.settings.minimum_duration = 30 * 60
                    self.settings.maximum_duration = 45 * 60
                    self.settings.volume = 2
                    #self.settings.trials_with_same_side = 30
                    self.settings.iti_time = 1
                    self.settings.led_on_time = 5 * 60
                    self.settings.c_led_on_time = 5 * 60
                    self.settings.timeout = 0
                else:
                    self.settings.next_task = "S2"
            else:
                self.settings.next_task = "S2" # Keep in task until it meets the criteria

        elif self.last_task == "S3":
            df_S3 = self.df[self.df.task == "S3"]
            if len(df_S3) >= 3:
                df_last_two_session_S3 = df_S3.iloc[-2:]
                n_trials_S3 = df_last_two_session_S3.trial.sum()
                if n_trials_S3 >= 200:
                    self.settings.next_task = "S4"
                    self.settings.minimum_duration = 30 * 60
                    self.settings.maximum_duration = 45 * 60
                    self.settings.volume = 2
                    self.settings.volume_large = 5
                    #self.settings.trials_with_same_side = 30
                    self.settings.iti_time = 1
                    self.settings.led_on_time = 5 * 60
                    self.settings.c_led_on_time = 5 * 60
                    self.settings.timeout = 3
                    self.settings.noise_time = 3


                else:
                    self.settings.next_task = "S3"
            else:
                self.settings.next_task = "S3" # Keep in task until it meets the criteria

        elif self.last_task == "S4":
            df_S4 = self.df[self.df.task == "S4"]
            if len(df_S4) >= 3:
                df_last_two_session_S4 = df_S4.iloc[-2:]
                n_trials_S4 = df_last_two_session_S4.trial.sum()
                if n_trials_S4 >= 200:
                    self.settings.next_task = "S5"
                    self.settings.minimum_duration = 45 * 60
                    self.settings.maximum_duration = 60 * 60
                    self.settings.volume = 2
                    self.settings.volume_large = 5
                    self.settings.timeout = 3
                    self.settings.iti_time = 1
                    self.settings.p = 0
                    self.settings.delay_values = [0, 0.25, 0.5, 1, 10000]
                    self.settings.curve_power = 2

                else:
                    self.settings.next_task = "S4"
            else:
                self.settings.next_task = "S4" # Keep in task until it meets the criteria

        elif self.last_task == "S5":
            df_S5 = self.df[self.df.task == "S5"]
            previous_p = df_S5.iloc[-1]["p"] if len(df_S5) > 0 else 0.0
            self.settings.p = max(previous_p - 0.05, 0.0)
            self.settings.delay_values = [0, 0.25, 0.5, 1, 10000]
            self.settings.next_task = "S5"
            self.settings.curve_power = 2


    def define_gui_tabs(self) -> None:
        self.gui_tabs = {

            "Difficulty" : [
                "p",
                "delay_values",
                "curve_power"
            ]
        }
