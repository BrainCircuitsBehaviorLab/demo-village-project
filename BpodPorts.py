from village.custom_classes.task_base import BpodEvent, BpodOutput

class BpodPorts:
    __slots__ = (
    "valve_l_time",
        "valve_l_time_large",
        "valve_l_reward",

        "valve_c_time",
        "valve_c_time_large",
        "valve_c_reward",

        "valve_r_time",
        "valve_r_time_large",
        "valve_r_reward",

        "LED_l_on",
        "LED_c_on",
        "LED_r_on",

        "left_poke",
        "center_poke",
        "right_poke",

        "left_poke_out",
        "center_poke_out",
        "right_poke_out",

        "sound_gain"
    )

    def __init__(self, nbox, water_calibration, sound_calibration, settings):

        self.sound_gain = sound_calibration.get_sound_gain(0, 70, "whitenoise")
        self.valve_l_time = water_calibration.get_valve_time(port = 1, volume = settings.volume)
        self.valve_l_time_large = water_calibration.get_valve_time(port = 1, volume = settings.volume_large)
        self.valve_l_reward = BpodOutput.Valve1

        self.valve_c_time = water_calibration.get_valve_time(port = 2, volume = settings.volume)
        self.valve_c_time_large = water_calibration.get_valve_time(port = 2, volume = settings.volume_large)
        self.valve_c_reward = BpodOutput.Valve2

        self.valve_r_time = water_calibration.get_valve_time(port = 3, volume = settings.volume)
        self.valve_r_time_large = water_calibration.get_valve_time(port = 3, volume = settings.volume_large)
        self.valve_r_reward = BpodOutput.Valve3

        self.LED_l_on = (BpodOutput.PWM1, settings.led_intensity)
        self.LED_c_on = (BpodOutput.PWM2, settings.led_intensity)
        self.LED_r_on = (BpodOutput.PWM3, settings.led_intensity)

        self.left_poke = BpodEvent.Port1In
        self.center_poke = BpodEvent.Port2In
        self.right_poke = BpodEvent.Port3In

        self.left_poke_out = BpodEvent.Port1Out
        self.center_poke_out = BpodEvent.Port2Out
        self.right_poke_out = BpodEvent.Port3Out
