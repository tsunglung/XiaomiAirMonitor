"""Support for Xiaomi Mi/QingPing Air Quality Monitor service."""
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import SensorEntity
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
    AIRQUALITY_SENSORS,
    MODELS_ALL_DEVICES,
    MODELS_MIOT,
    AVAILABLE_FEATURES,
    BATTERY_STATE_LITE,
    XiaomiAirQualitySensorDescription
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=90)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigType, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Xiaomi Mi/QingPing Air Quality Monitor sensor."""

    host = entry.options[CONF_HOST]
    model = entry.options[CONF_MODEL]
    name = entry.title
    unique_id = entry.unique_id

    airquality = hass.data[DOMAIN][host]

    try:
        entities = []

        for description in AIRQUALITY_SENSORS:
            if model in MODELS_ALL_DEVICES:
                features = AVAILABLE_FEATURES.get(model, [])
                if features:
                    for feature in features:
                        if feature == description.key:
                            entities.extend(
                                [XiaomiAirQualitySensor(entry.options, description, name, unique_id, airquality)]
                            )
                else:
                    entities.extend(
                        [XiaomiAirQualitySensor(entry.options, description, name, unique_id, airquality)]
                    )

        async_add_entities(entities)
    except AttributeError as ex:
        _LOGGER.error(ex)

class XiaomiAirQualitySensor(SensorEntity):
    """Implementation of a Xiaomi Mi/QingPing Air Quality Monitor sensor."""
    entity_description: XiaomiAirQualitySensorDescription

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
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class

    @property
    def name(self):
        """Return the name of the sensor."""
        return "{} {}".format(self._name, self.entity_description.name)

    @property
    def unique_id(self):
        """Return the unique of the sensor."""
        return "{}_{}".format(self._name, self.entity_description.key)

    def friendly_name(self):
        """Return the friendly name of the sensor."""
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
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

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
            if getattr(state, "tvoc_unit", None):
                self._attr_native_unit_of_measurement = getattr(state, "tvoc_unit", None)
            else:
                if self._attr == "battery_state" and self._model in MODELS_MIOT:
                    value = getattr(state, self._attr, None)
                    self._state = list(BATTERY_STATE_LITE.keys())[list(
                                        BATTERY_STATE_LITE.values()).index(value)]
                else:
                    self._state = getattr(state, self._attr, None)

        except UnboundLocalError:
            pass
        except TypeError:
            pass
        except DeviceException as ex:
            if self._available:
                self._available = False
                _LOGGER.error("Got exception while fetching the state: %s", ex)

