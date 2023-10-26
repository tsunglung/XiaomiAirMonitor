"""Support for Xiaomi Mi/QingPing Air Quality Monitor."""
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, StateType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.components.air_quality import AirQualityEntity
from homeassistant.const import (
    CONF_HOST,
    CONF_TOKEN
)

from miio import DeviceException

from .const import (
    CONF_MODEL,
    DATA_KEY,
    DOMAIN,
    MODELS_MIIO,
    MODELS_MIOT
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigType, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Xiaomi Mi/QingPing Air Quality Monitor."""

    host = entry.options[CONF_HOST]
    model = entry.options[CONF_MODEL]
    name = entry.title
    unique_id = entry.unique_id

    airquality = hass.data[DOMAIN][host]

    try:
        entities = []

        if model in MODELS_MIIO:
            entities.extend(
                [XiaomiAirQuality(entry.options, name, unique_id, airquality)]
            )
        if model in MODELS_MIOT:
            entities.extend(
                [XiaomiAirQuality(entry.options, name, unique_id, airquality)]
            )

        if len(entities) >= 1:
            async_add_entities(entities)

    except AttributeError as ex:
        _LOGGER.error(ex)


class XiaomiAirQuality(AirQualityEntity):
    # pylint: disable=too-many-instance-attributes
    """Representation of a Xiaomi Mi/QingPing Air Quality Monitor."""

    def __init__(self, entry_data, name, unique_id, airquality):
        """Initialize the entity."""
        self._host = entry_data[CONF_HOST]
        self._airquality = airquality
        self._name = name
        self._attr_name = name
        self._attr_unique_id = "{}_{}".format(name, unique_id)
        self._model = entry_data[CONF_MODEL]
        self._mac = entry_data[CONF_TOKEN]
        self._unique_id = unique_id
        self._air_quality_index = None
        self._carbon_dioxide = None
        self._carbon_dioxide_equivalent = None
        self._particulate_matter_2_5 = None
        self._total_volatile_organic_compounds = None
        self._temperature = None
        self._humidity = None
        self._state = None
        self._should_poll = True
        self._available = False

    @property
    def should_poll(self):
        """Return True if entity has to be polled for state."""
        return self._should_poll

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
            device_info["connections"] = {(CONNECTION_NETWORK_MAC, self._mac)}

        return device_info

    @property
    def air_quality_index(self) -> StateType:
        """Return the Air Quality Index (AQI)."""
        return self._air_quality_index

    @property
    def carbon_dioxide(self) -> StateType:
        """Return the CO2 (carbon dioxide) level."""
        return self._carbon_dioxide

    @property
    def carbon_dioxide_equivalent(self) -> StateType:
        """Return the CO2e (carbon dioxide equivalent) level."""
        return self._carbon_dioxide_equivalent

    @property
    def particulate_matter_2_5(self) -> StateType:
        """Return the particulate matter 2.5 level."""
        return self._particulate_matter_2_5

    @property
    def total_volatile_organic_compounds(self) -> StateType:
        """Return the total volatile organic compounds."""
        return self._total_volatile_organic_compounds

    async def async_added_to_hass(self):
        """ add to hass """
        self.hass.data[DATA_KEY][self._host]["status"] = \
            await self.hass.async_add_executor_job(self._airquality.status)
        await super().async_added_to_hass()

    async def async_update(self):
        """Fetch state from the device."""

        try:
            state = await self.hass.async_add_executor_job(self._airquality.status)
            self.hass.data[DATA_KEY][self._host]["status"] = state
            _LOGGER.debug("Got new state: %s", state)

            self._carbon_dioxide_equivalent = getattr(state, "co2", None)
            self._carbon_dioxide = getattr(state, "co2", None)
            self._particulate_matter_2_5 = getattr(state, "pm25", None)
            self._total_volatile_organic_compounds = getattr(state, "tvoc", None)
            self._available = True

        except DeviceException as ex:
            if self._available:
                self._available = False
                _LOGGER.error("Got exception while fetching the state: %s", ex)

