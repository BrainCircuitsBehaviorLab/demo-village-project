#TODO re-read
import random
from village.custom_classes.task_base import BpodEvent, BpodOutput, TaskBase
from BpodPorts import BpodPorts

import time

class S2(TaskBase):

    def __init__(self):
        super().__init__()

        self.info = """
Active learning, Water Delivery Task variation
-----------------------------------------------------------------------------
The task is designed to teach mice to approach the lickport:
- Each trial starts with:
    * LED on the rewarded port turns on (one of the two ports)
    * The animal has to poke in the port with the led on
    * Reward valve opens (water is delivered)
- The LED remains ON until:
    * A poke is detected in the correct port
    * Or a time up occurs
If the animal pokes in the wrong port nothing will happen, the mice 
will remain in the same state until pokes in the "correct" port. The same 
reward side will be repeated for n trials (20).
Reward is set at 2nl, and 5nl randomly in 10% of the trials. 

"""

    def start(self):
        self.settings.reward_volume = getattr(self.settings, "reward_volume", 2.0)
        self.settings.reward_volume_large = getattr(self.settings, "reward_volume_large", 5.0)

        self.ports = BpodPorts(
            nbox=self.system_name,
            water_calibration=self.calibrations.bpod_water_calibration,
            sound_calibration=self.calibrations.sound_calibration,
            settings=self.settings
        )

        # counters
        self.trial_count = 0
        self.reward_drunk = 0
        self.iti_time = self.settings.iti_time
        

    def create_trial(self):
        self.side = random.choice(["left", "right"])
        self.trial_count += 1

        # ---- reward size ----
        large_reward = random.random() < 0.10
        
        self.reward_volume = (
            self.settings.reward_volume_large
            if large_reward
            else self.settings.volume
        )

        # ---- side-dependent settings ----
        if self.side == "left":
            self.valvetime = (
                self.ports.valve_l_time_large
                if large_reward
                else self.ports.valve_l_time
            )
            self.valve_action = self.ports.valve_l_reward
            self.light_LED = self.ports.LED_l_on
            self.poke_side = self.ports.left_poke

        else:
            self.valvetime = (
                self.ports.valve_r_time_large
                if large_reward
                else self.ports.valve_r_time
            )
            self.valve_action = self.ports.valve_r_reward
            self.light_LED = self.ports.LED_r_on
            self.poke_side = self.ports.right_poke

        #### CREATING STATE MACHINE, ADDING STATES, SENDING AND RUNNING ####

        print('')
        print('Trial: ' + str(self.current_trial))
        print('Reward side: ' + str(self.side))
        print('Reward volume: ' + str(self.reward_volume))

        self.bpod.add_state(
            state_name='led_on',
            state_timer= self.settings.led_on_time,
            state_change_conditions={BpodEvent.Tup: 'exit', self.poke_side: 'water_delivery'},
            output_actions=[self.light_LED]
            )

        self.bpod.add_state(
            state_name='water_delivery',
            state_timer=self.valvetime,
            state_change_conditions={BpodEvent.Tup: 'iti'},
            output_actions=[self.valve_action, self.light_LED]
            )

        self.bpod.add_state(
            state_name='iti',
            state_timer= self.settings.iti_time,
            state_change_conditions={BpodEvent.Tup: 'exit'},
            output_actions=[])



    def after_trial(self):
        # --- LOCAL helpers :  ---
        def _event_key(ev):
            return ev.name if hasattr(ev, "name") else str(ev)

        def _first_choice_after(t0, left_key: str, right_key: str):
            """Ritorna ('left'|'right', t_choice) del primo poke dopo t0, altrimenti (None, None)."""
            L = [t for t in self.trial_data.get(left_key,  []) if t >= t0]
            R = [t for t in self.trial_data.get(right_key, []) if t >= t0]
            tL = L[0] if L else None
            tR = R[0] if R else None
            if tL is None and tR is None:
                return None, None
            if tL is None:
                return "right", tR
            if tR is None:
                return "left", tL
            return ("left", tL) if tL <= tR else ("right", tR)

        # 1) timestamp side LED ON (start)
        side_on_key = "STATE_led_on_START"
        t_side_on = self.trial_data[side_on_key][0] if side_on_key in self.trial_data and self.trial_data[side_on_key] else None

        # 2) events keys poke L/R
        left_key  = _event_key(self.ports.left_poke)   # es. "Port5In" / "Port2In" / ...
        right_key = _event_key(self.ports.right_poke)  # es. "Port1In" / "Port5In" / ...

        # 3) frist choice after LED on
        if t_side_on is not None:
            first_resp, t_choice = _first_choice_after(t_side_on, left_key, right_key)
        else:
            first_resp, t_choice = (None, None)


        # 5) outcome  CHOSEN SIDE -> 'side'
        if first_resp is None:
            chosen_side = "none"
            correct_outcome_int = 0
            outcome  = "miss"
        else:
            chosen_side = first_resp
            correct_outcome_int = int(chosen_side == self.side)
            outcome = "correct" if correct_outcome_int else "incorrect"

        # Relevant prints
        self.register_value('rewarded_side', self.side)
        self.register_value('outcome', outcome)
        self.register_value('response_side', chosen_side)

        # Relevant prints
        self.register_value('rewarded_side', self.side)
        
        # register how much water was delivered
        state = self.trial_data.get("STATE_water_delivery_START")
        if state and len(state) > 0 and state[0] > 0:
            self.register_value('water', self.reward_volume)
        else:
            self.register_value('water', 0)
 

    def close(self):
        pass

