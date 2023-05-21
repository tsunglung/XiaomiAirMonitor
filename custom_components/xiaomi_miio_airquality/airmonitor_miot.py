"""Support for Xiaomi Mi/QingPing Air Quality Monitor."""

import enum
from typing import Any, Dict
import logging
import click

from miio.click_common import command, format_output
from miio.device import DeviceStatus
from miio.miot_device import MiotDevice
from .const import (
    MODEL_AIRQUALITYMONITOR_LITE
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
        "screen": {"siid": 9, "aiid": 5},
        "device": {"siid": 9, "aiid": 6},
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
                {'did': 'relative-humidity', 'siid': 2, 'piid': 1, 'code': 0, 'value': 0},
                {'did': 'pm2.5-density', 'siid': 2, 'piid': 2, 'code': 0, 'value': 0},
                {'did': 'temperature', 'siid': 2, 'piid': 3, 'code': 0, 'value': 0},
                {'did': 'co2-density', 'siid': 2, 'piid': 4, 'code': 0, 'value': 0},
                {'did': 'tvoc-density', 'siid': 2, 'piid': 5, 'code': 0, 'value': 0},
                {'did': 'battery-level', 'siid': 3, 'piid': 1, 'code': 0, 'value': 0},
                {'did': 'charging-state', 'siid': 3, 'piid': 2, 'code': 0, 'value': 0}
            ],
            'exe_time': 280
        }
        """
        self.data = data

    @property
    def relative_humidity(self) -> int:
        """Relative Humidity"""
        return self.data["relative-humidity"]

    @property
    def pm25_density(self) -> int:
        """Target pm2.5"""
        return self.data["pm2.5-density"]

    @property
    def pm10_density(self) -> int:
        """Target pm10"""
        return self.data["pm10-density"]

    @property
    def temperature(self) -> int:
        """Temperature"""
        return self.data["temperature"]

    @property
    def co2_density(self) -> int:
        """CO2 Density"""
        return self.data["co2-density"]

    @property
    def tvoc_density(self) -> int:
        """TVOC Density"""
        return self.data["tvoc-density"]

    @property
    def battery_level(self) -> int:
        """Battery Level"""
        return self.data["battery-level"]

    @property
    def charging_state(self) -> int:
        """Charging state"""
        return self.data["charging-state"]

    @property
    def voltage(self) -> int:
        """voltage state"""
        return self.data["voltage"]



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
