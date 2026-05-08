from village.custom_classes.task import BpodEvent, BpodOutput, Task


# click on the link below to see the documentation about how to create
# tasks, plots and training protocols
# https://braincircuitsbehaviorlab.github.io/village/user_guide/create.html


class SimpleTask(Task):
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
        Initialize the training protocol. The text in the self.info variable
        will be shown when the task is selected in the GUI to be run manually.
        """
        super().__init__()

        self.info = """

        Simple Task
        -------------------

        This task is a simple visual task where the mouse has
        to poke in illuminated ports.
        The center port illuminates when a trial starts.
        After the center port is poked,
        both side ports are illuminated and give reward.
        """

    def start(self):
        """
        This function is called when the task starts.
        It is used to calculate values needed for the task.
        The following variables are accesible by default:
        - self.bpod: (Bpod object)
        - self.name: (str) the name of the task
                (it is the name of the class, in this case SimpleTask)
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

    def create_trial(self):
        """
        This function is called once per trial, first it modifies variables and then
        sends the state machine to the bpod that will run the trial.
        """

        try:
            self.bpod = self.controller
        except Exception:
            pass

        self.bpod.add_state(
            state_name="A",
            state_timer=1,
            state_change_conditions={BpodEvent.Tup: "B"},
            output_actions=[BpodOutput.SoftCode1, BpodOutput.BNC1Low],
        )

        self.bpod.add_state(
            state_name="B",
            state_timer=1,
            state_change_conditions={BpodEvent.Tup: "C"},
            output_actions=[BpodOutput.BNC1High],
        )

        self.bpod.add_state(
            state_name="C",
            state_timer=1,
            state_change_conditions={BpodEvent.Tup: "D"},
            output_actions=[(BpodOutput.PWM1, 255)],
        )

        self.bpod.add_state(
            state_name="D",
            state_timer=1,
            state_change_conditions={BpodEvent.Tup: "E"},
            output_actions=[BpodOutput.Valve1],
        )

        self.bpod.add_state(
            state_name="E",
            state_timer=1,
            state_change_conditions={BpodEvent.Tup: "exit"},
            output_actions=[(BpodOutput.Serial1, 20)],
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

        # print(self.trial_data)

        self.register_value("water", 20)

    def close(self):
        """
        Here you can perform any actions you want to take once the task is completed,
        such as sending a message via email or Slack, creating a plot, and more.
        """

        pass