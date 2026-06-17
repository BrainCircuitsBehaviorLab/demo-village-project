from village.custom_classes.task_base import BpodEvent, BpodOutput, TaskBase
from village.manager import manager
from BpodPorts import BpodPorts

class S0(TaskBase):
    def __init__(self):
        super().__init__()

        self.info = """
Habituation Task
----------------------------------------------------------
This task is an automatic mouse habitution to the box.
nothing will happen during the task, the mouse will be
left alone in the box for 15 minutes. BpodEual pokes will 
be registered but no reward will be delivered. 
"""

    def start(self):
        """
        This function is called when the task starts.
        It is used to calculate values needed for the task.
        The following variables are accesible by default:
        - self.bpod: Bpod object
        - self.settings: Settings object
        - self.manager: Manager object
        - self.subject: Subject object
        - self.task: Task object
        - self.task_name: Task name


        - self.bpod: (Bpod object)
        - self.name: (str) the name of the task
        self.subject: (str) the name of the subject
        self.current_trial: (int) the current trial number starting from 1
        self.trial_data: (list) information about the current trial
        self.system_name: (str) the name of the system as defined in the
                                tab settings of the GUI
        self.settings: (Settings object) the settings defined in training_settings.py
        self.force_stop: (bool) if made true the task will stop
        self.chrono = time_utils.Chrono()

        All the variables created in training_settings.py are accessible here.
        """

        self.ports = BpodPorts(
            nbox=self.system_name,
            water_calibration=self.calibrations.bpod_water_calibration,
            sound_calibration=self.calibrations.sound_calibration,
            settings=self.settings
        )
       

    def create_trial(self):
        """
        This function modifies variables and then sends the state machine to the bpod
        before each trial.
        """

        if self.current_trial == 1:

            self.bpod.add_state(
                state_name="trial_0",
                state_timer= 1,
                state_change_conditions={BpodEvent.Tup: "exit"},
                output_actions=[],
            )
    
        self.bpod.add_state(
            state_name="ready_to_explore",
            state_timer= 15 * 60,
            state_change_conditions={BpodEvent.Tup: "exit", 
                                     self.ports.left_poke: 'left_poke',
                                     self.ports.center_poke: 'center_poke',
                                     self.ports.right_poke: 'right_poke'},
            output_actions=[],
        )

        self.bpod.add_state(
            state_name="left_poke",
            state_timer= 0,
            state_change_conditions={BpodEvent.Tup: "exit"},
            output_actions=[],
        )

        self.bpod.add_state(
            state_name="center_poke",
            state_timer= 0,
            state_change_conditions={BpodEvent.Tup: "exit"},
            output_actions=[],
        )

        self.bpod.add_state(
            state_name="right_poke",
            state_timer= 0,
            state_change_conditions={BpodEvent.Tup: "exit"},
            output_actions=[],
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
        outcome = "miss"

        state = self.trial_data.get("STATE_left_poke_START")
        if state and len(state) > 0 and state[0] > 0:
             outcome = "left_poke"

        state = self.trial_data.get("STATE_center_poke_START")
        if state and len(state) > 0 and state[0] > 0:
             outcome = "center_poke"

        state = self.trial_data.get("STATE_right_poke_START")
        if state and len(state) > 0 and state[0] > 0:
             outcome = "right_poke"

        # Register the outcome of the trial
        self.register_value('poke_l', self.ports.left_poke)
        self.register_value('poke_c', self.ports.center_poke)
        self.register_value('poke_r', self.ports.right_poke)
        self.register_value('outcome', outcome)

    def close(self):
        """
        Here you can perform any actions you want to take once the task is completed,
        such as sending a message via email or Slack, creating a plot, and more.
        """

        print("closed!!")