"""Support for Xiaomi Mi/QingPing Air Quality Monitor service."""
import logging
from datetime import timedelta
from functools import partial

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import device_registry as dr
from homeassistant.const import (
    CONF_HOST,
    CONF_TOKEN
)
from miio import DeviceException

from .const import (
    CONF_MODEL,
    DATA_KEY,
    DOMAIN,
    AIRQUALITY_SWITCHS,
    MODELS_MIIO_W_SWITCH,
    XiaomiAirQualitySwitchDescription
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=90)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigType, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Xiaomi Mi/QingPing Air Quality Monitor Switch."""

    host = entry.options[CONF_HOST]
    model = entry.options[CONF_MODEL]
    name = entry.title
    unique_id = entry.unique_id

    airquality = hass.data[DOMAIN][host]

    try:
        entities = []

        for description in AIRQUALITY_SWITCHS:
            if model in MODELS_MIIO_W_SWITCH:
                entities.extend(
                    [XiaomiAirQualitySwitch(entry.options, description, name, unique_id, airquality)]
                )

        async_add_entities(entities)
    except AttributeError as ex:
        _LOGGER.error(ex)

class XiaomiAirQualitySwitch(SwitchEntity):
    """Implementation of a Xiaomi Mi/QingPing Air Quality Monitor Switch."""
    entity_description: XiaomiAirQualitySwitchDescription

    def __init__(self, entry_data, description, name, unique_id, airquality):
        self.entity_description = description
        self._entry_data = entry_data
        self._name = name
        self._model = entry_data[CONF_MODEL]
        self._unique_id = unique_id
        self._attr = description.key
        self._mac = entry_data[CONF_TOKEN]
        self._host = entry_data[CONF_HOST]
        self._airquality = airquality
        self._available = True
        self._skip_update = False
        self._state = None

    @property
    def name(self):
        """Return the name of the switch."""
        return "{} {}".format(self._name, self.entity_description.name)

    @property
    def unique_id(self):
        """Return the unique of the switch."""
        return "{}_{}".format(self._name, self.entity_description.key)

    def friendly_name(self):
        """Return the friendly name of the switch."""
        return "{}".format(self.entity_description.name)

    @property
    def device_info(self):
        """Return the device info."""
        info = self._airquality.info()
        device_info = {
            "identifiers": {(DOMAIN, self._unique_id)},
            "manufacturer": (self._model or "Xiaomi").split(".", 1)[0].capitalize(),
            "name": self._name,
            "model": self._model,
            "sw_version": info.firmware_version,
            "hw_version": info.hardware_version
        }

        if self._mac is not None:
            device_info["connections"] = {(dr.CONNECTION_NETWORK_MAC, self._mac)}

        return device_info

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return self._state

    async def _try_command(self, mask_error, func, *args, **kwargs):
        """Call a airquality command handling error messages."""
        try:
            result = await self.hass.async_add_executor_job(
                partial(func, *args, **kwargs)
            )

            _LOGGER.debug("Response received from airquality: %s", result)
            if isinstance(result, str):
                if result == "ok":
                    return True
                return False
            elif isinstance(result, list):
                if len(result) >= 1:
                    return result[0].get('code', -1) == 0
                return True
            elif isinstance(result, dict):
                return result.get('code', -1) == 0
            else:
                return False
                
        except DeviceException as exc:
            if self._available:
                _LOGGER.error(mask_error, exc)
                self._available = False

            return False

    async def async_turn_on(self, **kwargs):
        """Turn the airquality on."""
        result = await self._try_command(
            "Turning the airquality switch on failed.",
            self._airquality.set_switch_on,
            self._attr)

        if result:
            self._state = True
            self._skip_update = True

    async def async_turn_off(self, **kwargs):
        """Turn the airquality off."""
        result = await self._try_command(
            "Turning the airquality off failed.",
            self._airquality.set_switch_off,
            self._attr)

        if result:
            self._state = False
            self._skip_update = True

    async def async_update(self):
        """Fetch state from the device."""
        # On state change the device doesn't provide the new state immediately.
        if self._skip_update:
            self._skip_update = False
            return

        try:
            if self.hass.data[DATA_KEY][self._host].get("status", None):
                state = self.hass.data[DATA_KEY][self._host]["status"]
            else:
                state = await self.hass.async_add_executor_job(self._airquality.status)
            _LOGGER.debug("Got new state: %s", state)

            self._available = True
            self._state = getattr(state, self._attr, None)

        except UnboundLocalError:
            pass
        except TypeError:
            pass
        except DeviceException as ex:
            if self._available:
                self._available = False
                _LOGGER.error("Got exception while fetching the state: %s", ex)

