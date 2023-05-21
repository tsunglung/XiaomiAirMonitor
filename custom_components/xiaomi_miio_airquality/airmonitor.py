"""Support for Xiaomi Mi/QingPing Air Quality Monitor."""
import logging
from collections import defaultdict
import click

from miio.click_common import command, LiteralParamType, format_output
from miio import Device, AirQualityMonitor, DeviceException
from .const import(
    AVAILABLE_FEATURES,
    MODELS_MIIO,
    MODEL_AIRQUALITYMONITOR_S1
)

_LOGGER = logging.getLogger(__name__)

class AirQualityMonitorStatus:
    """Container of air quality monitor status."""

    def __init__(self, data):
        self.data = data

    @property
    def power(self) -> str:
        """Current power state."""
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        """Return True if the device is turned on."""
        return self.power == "on"

    @property
    def temperature(self) -> bool:
        """Temperature value. (-20 ~ 50)."""
        return self.data["temperature"]

    @property
    def humidity(self) -> int:
        """Humidity value. (0 ~ 100)."""
        return self.data["humidity"]

    @property
    def co2(self) -> int:
        """Air CO2 value. (400 ~ 9999)."""
        return self.data["co2"]

    @property
    def tvoc(self) -> int:
        """Air quality index value. (1 ~ 2187)."""
        return self.data["tvoc"]

    @property
    def pm25(self) -> bool:
        """PM 2.5 value. (0 ~ 999)."""
        return self.data["pm25"]

    @property
    def pm10(self) -> bool:
        """PM 10 value. (0 ~ 999)."""
        return self.data["pm10"]

    @property
    def battery(self) -> bool:
        """Current battery level (0 ~ 100)."""
        return self.data["battery"]

    @property
    def battery_state(self) -> str:
        """Current battery charing state (1, 2)."""
        return self.data["battery_state"]

    def __repr__(self) -> str:
        s = "<AirQualityMonitorStatus humidity=%s, " \
            "co2=%s, " \
            "tvoc=%s, " \
            "pm25=%s, " \
            "pm10=%s, " \
            "battery=%s, " \
            "battery_state=%s>" % \
            (
                self.humidity,
                self.co2,
                self.tvoc,
                self.pm25,
                self.pm10,
                self.battery,
                self.battery_state
            )
        return s

    def __json__(self):
        return self.data

class AirQualityMonitor(Device):
    def __init__(self, ip: str = None, token: str = None, start_id: int = 0,
                 debug: int = 0, lazy_discover: bool = True,
                 model: str = MODEL_AIRQUALITYMONITOR_S1) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover, model=model)

        if model not in MODELS_MIIO:
            _LOGGER.error("Device model %s unsupported. Falling back to %s.", model, self.model)

        self.device_info = None

    @command(
        default_output=format_output(
            ""
        )
    )
    def status(self) -> AirQualityMonitorStatus:
        """Return device status."""

        try:
            properties = AVAILABLE_FEATURES[self.model]

            # get battery only battery_state is not in charging.
            if "battery_state" in properties and "battery" in properties:
                properties.remove("battery")

            values = self.send(
                "get_prop",
                properties
            )

            properties_count = len(properties)
            values_count = len(values)
            if properties_count != values_count:
                _LOGGER.error(
                    "Count (%s) of requested properties does not match the "
                    "count (%s) of received values.",
                    properties_count, values_count)
            if "battery_state" in values and values["battery_state"] != "charging":
                battery_level = self.send("get_prop", ["battery"])
                if battery_level["battery"]:
                    values["battery"] = battery_level["battery"]

            if "pm10" not in properties:
                values["pm10"] = None
            if "tvoc" not in properties:
                values["tvoc"] = None

            return AirQualityMonitorStatus(
                defaultdict(lambda: None, values))
        except ValueError as ex:
            _LOGGER.error("Get deivce status error {}!".format(ex))

    @command(
        default_output=format_output("Powering on"),
    )
    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    @command(
        default_output=format_output("Powering off"),
    )
    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    @command(
        click.argument("display_clock", type=bool),
        default_output=format_output(
            lambda led: "Turning on display clock"
            if led else "Turning off display clock"
        )
    )
    def set_display_clock(self, display_clock: bool):
        """Enable/disable displaying a clock instead the AQI."""
        if display_clock:
            self.send("set_time_state", ["on"])
        else:
            self.send("set_time_state", ["off"])

    @command(
        click.argument("auto_close", type=bool),
        default_output=format_output(
            lambda led: "Turning on auto close"
            if led else "Turning off auto close"
        )
    )
    def set_auto_close(self, auto_close: bool):
        """Purpose unknown."""
        if auto_close:
            self.send("set_auto_close", ["on"])
        else:
            self.send("set_auto_close", ["off"])

    @command(
        click.argument("night_mode", type=bool),
        default_output=format_output(
            lambda led: "Turning on night mode"
            if led else "Turning off night mode"
        )
    )
    def set_night_mode(self, night_mode: bool):
        """Decrease the brightness of the display."""
        if night_mode:
            self.send("set_night_state", ["on"])
        else:
            self.send("set_night_state", ["off"])

    @command(
        click.argument("begin_hour", type=int),
        click.argument("begin_minute", type=int),
        click.argument("end_hour", type=int),
        click.argument("end_minute", type=int),
        default_output=format_output(
            "Setting night time to {begin_hour}:{begin_minute} - {end_hour}:{end_minute}")
    )
    def set_night_time(self, begin_hour: int, begin_minute: int,
                       end_hour: int, end_minute: int):
        """Enable night mode daily at bedtime."""
        begin = begin_hour * 3600 + begin_minute * 60
        end = end_hour * 3600 + end_minute * 60

        if begin < 0 or begin > 86399 or end < 0 or end > 86399:
            raise Exception("Begin or/and end time invalid.")

        self.send("set_night_time", [begin, end])

    def set_property(self, property_key: str, value):
        """Sets property value using the existing mapping."""
        return self.send(
            "set_properties",
            [{"did": property_key, "property": property_key, "value": value}],
        )

    @command(
        click.argument("siid", type=int),
        click.argument("aiid", type=int),
        click.argument("params", type=LiteralParamType(), required=False),
    )
    def call_action_by(self, siid, aiid, params=None):
        """Call an action."""
        if params is None:
            params = []
        payload = {
            "did": f"call-{siid}-{aiid}",
            "siid": siid,
            "aiid": aiid,
            "in": params,
        }

        return self.send("action", payload)

    @command(
        click.argument("switch", type=str),
        default_output=format_output("Setting Switch {switch}"),
    )
    def set_switch_on(self, switch: str):
        """Set Switch on."""

        if switch == "screen":
            return self.call_action_by(9, 2, 0)
        if switch == "device":
            return self.call_action_by(9, 6, 0)
        return self.set_property(switch, True)

    @command(
        click.argument("switch", type=str),
        default_output=format_output("Setting Switch {switch}"),
    )
    def set_switch_off(self, switch: str):
        """Set Switch off."""

        if switch == "screen":
            return self.call_action_by(9, 2, 1)
        if switch == "device":
            return self.call_action_by(9, 6, 1)
        return self.set_property(switch, True)