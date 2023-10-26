"""Support for Xiaomi Mi/QingPing Air Quality Monitor."""

import enum
from typing import Any, Dict
import logging
import click

from miio.click_common import command, format_output
from miio.device import DeviceStatus
from miio.miot_device import MiotDevice
from .const import (
    MODEL_AIRQUALITYMONITOR_LITE,
    MODEL_AIRQUALITYMONITOR_LITE_DANY
)

_LOGGER = logging.getLogger(__name__)


MIOT_MAPPING = {
    MODEL_AIRQUALITYMONITOR_LITE: {
        "relative-humidity": {"siid": 3, "piid": 1},  # read, notify
        "pm2.5-density": {"siid": 3, "piid": 4},  # read, notify
        "pm10-density": {"siid": 3, "piid": 5},  # read, notify
        "temperature": {"siid": 3, "piid": 7},  # read, notify
        "co2-density": {"siid": 3, "piid": 8},  # read, notify
        "battery-level": {"siid": 4, "piid": 1},  # read, notify
        "charging-state": {"siid": 4, "piid": 2},  # read, notify
        "voltage": {"siid": 4, "piid": 3},  # read, notify
        "set-screen-off": {"siid": 9, "aiid": 5},
        "set-device-off": {"siid": 9, "aiid": 6},
        "start-time": {"siid": 9, "piid": 2},  # read, write, notify
        "end-time": {"siid": 9, "piid": 3},  # read, write, notify
        "monitoring-frequency": {"siid": 9, "piid": 4},  # read, write, notify
        "screen-off": {"siid": 9, "piid": 5},  # read, write, notify
        "device-off": {"siid": 9, "piid": 6},  # read, write, notify
        "tempature-unit": {"siid": 9, "piid": 7},  # read, write, notify
        "screensaver-time": {"siid": 9, "piid": 8},  # read, write, notify
        "time-zone": {"siid": 9, "piid": 9},  # read, write, notify
        "auto-slideing-time": {"siid": 9, "piid": 10},  # read, write, notify
        "screensaver-type": {"siid": 9, "piid": 11},  # read, write, notify
        "page-sequence": {"siid": 9, "piid": 12},  # read, write, notify
        "temp-led-th": {"siid": 9, "piid": 13},  # read, write, notify
        "humi-led-th": {"siid": 9, "piid": 14},  # read, write, notify
        "carbondioxide-led-th": {"siid": 9, "piid": 15},  # read, write, notify
        "pm-tpf-led-th": {"siid": 9, "piid": 16},  # read, write, notify
        "pm-t-led-th": {"siid": 9, "piid": 17},  # read, write, notify
        "device-off-new": {"siid": 9, "piid": 18},  # read, write, notify
        "is-twelve-hours-sys": {"siid": 9, "piid": 19},  # read, write, notify
        "pm-tpf-standard": {"siid": 9, "piid": 20},  # read, write, notify
    },
    MODEL_AIRQUALITYMONITOR_LITE_DANY: {
        "relative-humidity": {"siid": 3, "piid": 1},  # read, notify
        "pm2.5-density": {"siid": 3, "piid": 4},  # read, notify
        "pm10-density": {"siid": 3, "piid": 5},  # read, notify
        "temperature": {"siid": 3, "piid": 7},  # read, notify
        "co2-density": {"siid": 3, "piid": 8},  # read, notify
        "battery-level": {"siid": 4, "piid": 1},  # read, notify
        "charging-state": {"siid": 4, "piid": 2},  # read, notify
        "voltage": {"siid": 4, "piid": 3},  # read, notify
        "set-screen-off": {"siid": 9, "aiid": 5},
        "set-device-off": {"siid": 9, "aiid": 6},
        "start-time": {"siid": 9, "piid": 2},  # read, write, notify
        "end-time": {"siid": 9, "piid": 3},  # read, write, notify
        "monitoring-frequency": {"siid": 9, "piid": 4},  # read, write, notify
        "screen-off": {"siid": 9, "piid": 5},  # read, write, notify
        "device-off": {"siid": 9, "piid": 6},  # read, write, notify
        "tempature-unit": {"siid": 9, "piid": 7},  # read, write, notify
        "screensaver-time": {"siid": 9, "piid": 8},  # read, write, notify
        "time-zone": {"siid": 9, "piid": 9},  # read, write, notify
        "auto-slideing-time": {"siid": 9, "piid": 10},  # read, write, notify
        "screensaver-type": {"siid": 9, "piid": 11},  # read, write, notify
        "page-sequence": {"siid": 9, "piid": 12},  # read, write, notify
        "temp-led-th": {"siid": 9, "piid": 13},  # read, write, notify
        "humi-led-th": {"siid": 9, "piid": 14},  # read, write, notify
        "carbondioxide-led-th": {"siid": 9, "piid": 15},  # read, write, notify
        "pm-tpf-led-th": {"siid": 9, "piid": 16},  # read, write, notify
        "pm-t-led-th": {"siid": 9, "piid": 17},  # read, write, notify
        "device-off-new": {"siid": 9, "piid": 18},  # read, write, notify
        "is-twelve-hours-sys": {"siid": 9, "piid": 19},  # read, write, notify
        "pm-tpf-standard": {"siid": 9, "piid": 20},  # read, write, notify
    }
}


class DeviceException(Exception):
    """Exception wrapping any communication errors with the device."""


class AirQualityStatusMiot(DeviceStatus):
    """Container for status reports for Xiaomi Mi/QingPing Air Quality Monitor."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        {
            'id': 1,
            'result': [
                {'did': 'relative-humidity', 'siid': 3, 'piid': 1, 'code': 0, 'value': 0},
                {'did': 'pm2.5-density', 'siid': 3, 'piid': 2, 'code': 0, 'value': 0},
                {'did': 'temperature', 'siid': 3, 'piid': 3, 'code': 0, 'value': 0},
                {'did': 'co2-density', 'siid': 3, 'piid': 4, 'code': 0, 'value': 0},
                {'did': 'tvoc-density', 'siid': 3, 'piid': 5, 'code': 0, 'value': 0},
                {'did': 'battery-level', 'siid': 4, 'piid': 1, 'code': 0, 'value': 0},
                {'did': 'charging-state', 'siid': 4, 'piid': 2, 'code': 0, 'value': 0}
            ],
            'exe_time': 280
        }
        """
        self.data = data

    @property
    def humidity(self) -> int:
        """Relative Humidity"""
        return self.data["relative-humidity"]

    @property
    def pm25(self) -> int:
        """Target pm2.5"""
        return self.data["pm2.5-density"]

    @property
    def pm10(self) -> int:
        """Target pm10"""
        return self.data["pm10-density"]

    @property
    def temperature(self) -> float:
        """Temperature"""
        return self.data["temperature"]

    @property
    def co2(self) -> int:
        """CO2 Density"""
        return self.data["co2-density"]

    @property
    def tvoc(self) -> int | None:
        """TVOC Density"""
        return self.data.get("tvoc-density", None)

    @property
    def battery(self) -> int:
        """Battery Level"""
        return self.data["battery-level"]

    @property
    def battery_state(self) -> int:
        """Charging state"""
        return self.data["charging-state"]

    @property
    def voltage(self) -> int:
        """voltage state"""
        return self.data["voltage"]

    @property
    def monitoring_frequency(self) -> int | None:
        """Monitoring Frequency"""
        return self.data.get("monitoring-frequency", None)

    @property
    def screen_off(self) -> int | None:
        """Screen Off time"""
        return self.data.get("screen-off", None)

    @property
    def device_off(self) -> int | None:
        """Device Off time"""
        return self.data.get("device-off", None)

    @property
    def screensaver_time(self) -> int | None:
        """Screen Saver Time"""
        return self.data.get("screensaver-time", None)

    @property
    def auto_slideing_time(self) -> int | None:
        """Auto Slideing Time"""
        return self.data.get("auto-slideing-time", None)

    @property
    def screensaver_type(self) -> int | None:
        """Screen Saver Type"""
        return self.data.get("screensaver-type", None)

    @property
    def device_off_new(self) -> int | None:
        """New Device Off time"""
        return self.data.get("device-off-new", None)

    @property
    def is_twelve_hours_sys(self) -> int | None:
        """Is Twelve Hours Sys"""
        return self.data.get("is-twelve-hours-sys", None)

    @property
    def pm_tpf_standard(self) -> int | None:
        """PM TPF SStandard"""
        return self.data.get("pm-tpf-standard", None)


class AirQualityMonitorMiot(MiotDevice):
    """Interface for Xiaomi Mi/QingPing Air Quality Monitor Miot"""
    mapping = MIOT_MAPPING[MODEL_AIRQUALITYMONITOR_LITE]

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_AIRQUALITYMONITOR_LITE,
    ) -> None:
        if model not in MIOT_MAPPING:
            raise DeviceException("Invalid AirQualityMonitorMiot model: %s" % model)

        super().__init__(ip, token, start_id, debug, lazy_discover)
        self._model = model

    @command(
        default_output=format_output(
            "",
            "Status: {result.status.name}\n"
        )
    )
    def status(self) -> AirQualityStatusMiot:
        """Retrieve properties."""
        return AirQualityStatusMiot(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )

    @command(
        click.argument("switch", type=str),
        default_output=format_output("Setting Switch {switch}"),
    )
    def set_switch_on(self, switch: str):
        """Set Switch on."""
        if switch in ["screen", "device"] :
            return self.call_action(switch, 0)
        return self.set_property(switch, True)

    @command(
        click.argument("switch", type=str),
        default_output=format_output("Setting Switch {switch}"),
    )
    def set_switch_off(self, switch: str):
        """Set Switch off."""
        if switch in ["screen", "device"] :
            return self.call_action(switch, 1)
        return self.set_property(switch, True)

    @command(
        click.argument("property", type=str),
        default_output=format_output("Setting {property} {value}"),
    )
    def set_value(self, property: str, value: float):
        """Set value."""
        property = property.replace("_", "-")
        return self.set_property(property, value)