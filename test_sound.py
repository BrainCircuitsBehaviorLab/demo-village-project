from village.custom_classes.task import Event, Output, Task


class TestSound(Task):
    """
    This class defines the task.

    Required methods to implement:
    - __init__: Initialize the task
    - start: Called when the task starts.
    - create_trial: Called once per trial to create the state machine.
    - after_trial: Called once after each trial to register the values in the .csv file.
    - close: Called when the task is finished.
    """

    def __init__(self):
        """
        Initialize the task. The text in the self.info variable
        will be shown when the task is selected in the GUI to be run manually.
        """
        super().__init__()

        self.info = """

        Test Sound Task
        -------------------

        Playing sounds.
        """

    def start(self):
        """
        This function is called when the task starts.
        It is used to calculate values needed for the task.
        The following variables are accesible by default:
        - self.bpod: (Bpod object)
        - self.name: (str) the name of the task
                (it is the name of the class, in this case Habituation)
        - self.subject: (str) the name of the subject performing the task
        - self.current_trial: (int) the current trial number starting from 1
        - self.system_name: (str) the name of the system as defined in the
                                tab settings of the GUI
        - self.settings: (Settings object) the settings defined in training_protocol.py
        - self.trial_data: (dict) information about the current trial
        - self.force_stop: (bool) if made true the task will stop

        Al the variables created in training_protocol.py are accessible.
        - self.settings.reward_amount_ml: reward volume
        - self.settings.stage: current training stage
        - self.settings.light_intensity_high: high light intensity
        - self.settings.light_intensity_low: low light intensity
        - self.settings.trial_types: possible trial types
        - self.settings.punishment_time: punishment duration
        - self.settings.iti_time: inter-trial interval
        """
        self.sound_duration = 1
        self.sound_gain = 0.1
        self.sound_file = "sound.wav"


    def create_trial(self):
        """
        This function is called once per trial, first it modifies variables and then
        sends the state machine to the bpod that will run the trial.
        """

        self.controller.add_state(
            state_name="A",
            state_timer=2,
            state_change_conditions={Event.Tup: "B"},
            output_actions=[Output.SoftCode1, Output.BNC1Low],
        )

        self.controller.add_state(
            state_name="B",
            state_timer=2,
            state_change_conditions={Event.Tup: "C"},
            output_actions=[Output.SoftCode5, Output.BNC1High],
        )

        self.controller.add_state(
            state_name="C",
            state_timer=2,
            state_change_conditions={Event.Tup: "D"},
            output_actions=[Output.SoftCode2, Output.BNC1Low],
        )

        self.controller.add_state(
            state_name="D",
            state_timer=2,
            state_change_conditions={Event.Tup: "color"},
            output_actions=[Output.SoftCode5, Output.BNC1High],
        )

        self.controller.add_state(
            state_name="color",
            state_timer=0,
            state_change_conditions={Event.Tup: "E"},
            output_actions=[Output.SoftCode3, Output.BNC1Low],
        )

        self.controller.add_state(
            state_name="E",
            state_timer=2,
            state_change_conditions={Event.Tup: "F"},
            output_actions=[Output.SoftCode5, Output.BNC1Low],
        )

        self.controller.add_state(
            state_name="F",
            state_timer=10,
            state_change_conditions={Event.Tup: "G"},
            output_actions=[Output.SoftCode4, Output.BNC1High],
        )

        self.controller.add_state(
            state_name="G",
            state_timer=2,
            state_change_conditions={Event.Tup: "H"},
            output_actions=[Output.SoftCode5, Output.BNC1Low],
        )




    def after_trial(self):
        """
        Here you can register all the values you need to save for each trial.
        It is essential to always include a variable named water, which stores the
        amount of water consumed during each trial.
        The system will calculate the total water consumption in each session
        by summing this variable.
        If the total water consumption falls below a certain threshold,
        an alarm will be triggered.
        This threshold can be adjusted in the Settings tab of the GUI.
        """
        pass


    def close(self):
        """
        Here you can perform any actions you want to take once the task is completed,
        such as sending a message via email or Slack, creating a plot, and more.
        """
        pass
