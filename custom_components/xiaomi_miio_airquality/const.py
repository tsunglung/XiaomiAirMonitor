"""Constants of the Xiaomi Mi/QingPing Air Quality Monitor component."""
from datetime import timedelta
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass
)
from homeassistant.components.switch import SwitchEntityDescription

from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    CONCENTRATION_PARTS_PER_BILLION,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
    TEMP_CELSIUS,
    ATTR_BATTERY_CHARGING,
    ATTR_BATTERY_LEVEL
)

DEFAULT_NAME = "Xiaomi Mi/QingPing Air Quality Monitor"
DOMAIN = "xiaomi_miio_airquality"
DOMAINS = ["air_quality", "sensor", "switch"]
DATA_KEY = "xiaomi_airquality_data"
DATA_STATE = "state"
DATA_DEVICE = "device"

CONF_MODEL = "model"
CONF_MAC = "mac"

MODEL_AIRQUALITYMONITOR_S1 = "cgllc.airmonitor.s1"

MODEL_AIRQUALITYMONITOR_LITE = "cgllc.airm.cgdn1"

OPT_MODEL = {
    MODEL_AIRQUALITYMONITOR_S1: "QingPing Air Quality Monitor",
    MODEL_AIRQUALITYMONITOR_LITE: "QingPing Air Quality Monitor Lite"
}


MODELS_MIIO = [
    MODEL_AIRQUALITYMONITOR_S1
]

MODELS_MIIO_W_SWITCH = [
    MODEL_AIRQUALITYMONITOR_LITE
]

MODELS_MIOT = [
    MODEL_AIRQUALITYMONITOR_LITE
]

MODELS_ALL_DEVICES = MODELS_MIIO

AVAILABLE_FEATURES_COMMON = ['co2', 'humidity', 'pm25', 'temperature']

AVAILABLE_FEATURES = {
    MODEL_AIRQUALITYMONITOR_S1: AVAILABLE_FEATURES_COMMON + ['battery', 'battery_state', 'tvoc'],
    MODEL_AIRQUALITYMONITOR_LITE: AVAILABLE_FEATURES_COMMON + ['battery', 'battery_state', 'pm10']
}

DEFAULT_SCAN_INTERVAL = 30
SCAN_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

ATTR_POWER = "power"
ATTR_TEMPERATURE = "temperature"
ATTR_LOAD_POWER = "load_power"
ATTR_MODEL = "model"
ATTR_POWER_MODE = "power_mode"
ATTR_WIFI_LED = "wifi_led"
ATTR_POWER_PRICE = "power_price"
ATTR_PRICE = "price"
ATTR_WORKING_TIME = "working_time"
ATTR_COUNT_DOWN_TIME = "count_down_time"
ATTR_COUNT_DOWN = "count_down"
ATTR_KEEP_RELAY = "keep_relay"

@dataclass
class XiaomiAirQualitySensorDescription(
    SensorEntityDescription
):
    """Class to describe an Xiaomi Mi/QingPing Air Quality Monitor sensor."""


AIRQUALITY_SENSORS: tuple[XiaomiAirQualitySensorDescription, ...] = (
    XiaomiAirQualitySensorDescription(
        key="battery_state",
        name="Battery Status",
        icon="mdi:battery-charging"
    ),
    XiaomiAirQualitySensorDescription(
        key="battery",
        name="Battery Level",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.BATTERY,
        icon="mdi:battery"
    ),
    XiaomiAirQualitySensorDescription(
        key="temperature",
        name="Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        icon="mdi:thermometer"
    ),
    XiaomiAirQualitySensorDescription(
        key="humidity",
        name="Humidity",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.HUMIDITY,
        icon="mdi:water-percent"
    ),
    XiaomiAirQualitySensorDescription(
        key="co2",
        name="CO2",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CO2,
        icon="mdi:molecule-co2"
    ),
    XiaomiAirQualitySensorDescription(
        key="pm25",
        name="PM2.5",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PM25,
        icon="mdi:chemical-weapon"
    ),
    XiaomiAirQualitySensorDescription(
        key="pm10",
        name="PM10",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PM10,
        icon="mdi:chemical-weapon"
    ),
    XiaomiAirQualitySensorDescription(
        key="tvoc",
        name="TVOC",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_BILLION,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
        icon="mdi:cloud"
    )
)


@dataclass
class XiaomiAirQualitySwitchDescription(
    SwitchEntityDescription
):
    """Class to describe an Xiaomi Mi/QingPing Air Quality Monitor Switch."""


AIRQUALITY_SWITCHS: tuple[XiaomiAirQualitySwitchDescription, ...] = (
    XiaomiAirQualitySwitchDescription(
        key="screen",
        name="Screen Switch",
        icon="mdi:monitor"
    ),
    XiaomiAirQualitySwitchDescription(
        key="device",
        name="Device Switch",
        icon="mdi:monitor"
    )
)
