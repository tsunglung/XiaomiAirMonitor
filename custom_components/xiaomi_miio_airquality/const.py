"""Constants of the Xiaomi Mi/QingPing Air Quality Monitor component."""
from datetime import timedelta
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass
)
from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntityDescription
)
from homeassistant.components.switch import SwitchEntityDescription

from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    CONCENTRATION_PARTS_PER_BILLION,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
    TEMP_CELSIUS,
    ATTR_BATTERY_CHARGING,
    ATTR_BATTERY_LEVEL,
    UnitOfElectricPotential,
    UnitOfTime
)

DEFAULT_NAME = "Xiaomi Mi/QingPing Air Quality Monitor"
DOMAIN = "xiaomi_miio_airquality"
DOMAINS = ["air_quality", "number", "sensor", "switch"]
DATA_KEY = "xiaomi_airquality_data"
DATA_STATE = "state"
DATA_DEVICE = "device"

CONF_MODEL = "model"
CONF_MAC = "mac"

MODEL_AIRQUALITYMONITOR_S1 = "cgllc.airmonitor.s1"

MODEL_AIRQUALITYMONITOR_LITE = "cgllc.airm.cgdn1"
MODEL_AIRQUALITYMONITOR_LITE_DANY = "cgllc.airm.cgd1st"


OPT_MODEL = {
    MODEL_AIRQUALITYMONITOR_S1: "QingPing Air Quality Monitor",
    MODEL_AIRQUALITYMONITOR_LITE: "QingPing Air Quality Monitor Lite",
    MODEL_AIRQUALITYMONITOR_LITE_DANY: "QingPing Air Quality Monitor Lite (Dany ESP32)"
}


MODELS_MIIO = [
    MODEL_AIRQUALITYMONITOR_S1
]

MODELS_MIIO_W_SWITCH = [
    MODEL_AIRQUALITYMONITOR_LITE,
    MODEL_AIRQUALITYMONITOR_LITE_DANY
]

MODELS_MIOT = [
    MODEL_AIRQUALITYMONITOR_LITE,
    MODEL_AIRQUALITYMONITOR_LITE_DANY
]

MODELS_ALL_DEVICES = MODELS_MIIO + MODELS_MIOT

AVAILABLE_FEATURES_COMMON = ['co2', 'humidity', 'pm25', 'temperature']

AVAILABLE_FEATURES = {
    MODEL_AIRQUALITYMONITOR_S1: AVAILABLE_FEATURES_COMMON + ['battery', 'battery_state', 'tvoc'],
    MODEL_AIRQUALITYMONITOR_LITE: AVAILABLE_FEATURES_COMMON + ['battery', 'battery_state', 'pm10'],
    MODEL_AIRQUALITYMONITOR_LITE_DANY: AVAILABLE_FEATURES_COMMON + 
        ['battery', 'battery_state', 'voltage', 'pm10'] + 
        ["monitoring_frequency", "screen_off", "device_off", "screensaver_time", "auto_slideing_time", "screensaver_type", "device_off_new", "is_twelve_hours_sys", "pm_tpf_standard"]
}

DEFAULT_SCAN_INTERVAL = 60
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

BATTERY_STATE_LITE = {
    "Charging": 1,
    "Not charging": 2,
    "Not chargeable": 3
}

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
    ),
    XiaomiAirQualitySensorDescription(
        key="voltage",
        name="Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
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
        key="set-screen-off",
        name="Screen Switch",
        icon="mdi:monitor"
    ),
    XiaomiAirQualitySwitchDescription(
        key="set-device-off",
        name="Device Switch",
        icon="mdi:monitor"
    )
)


@dataclass
class XiaomiAirQualityNumberDescription(
    NumberEntityDescription
):
    """Class to describe an Xiaomi Mi/QingPing Air Quality Monitor Number."""


AIRQUALITY_NUMBERS: tuple[XiaomiAirQualityNumberDescription, ...] = (
    XiaomiAirQualityNumberDescription(
        key="monitoring-frequency",
        name="Monitoring Frequency",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=NumberDeviceClass.DURATION,
        icon="mdi:clock",
        native_min_value=0,
        native_max_value=600,
        native_step=1
    ),
    XiaomiAirQualityNumberDescription(
        key="screen_off",
        name="Screen Off",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=NumberDeviceClass.DURATION,
        icon="mdi:clock",
        native_min_value=0,
        native_max_value=600,
        native_step=1
    ),
    XiaomiAirQualityNumberDescription(
        key="device_off",
        name="Device Off",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=NumberDeviceClass.DURATION,
        icon="mdi:clock-outline",
        native_min_value=0,
        native_max_value=600,
        native_step=1
    ),
    XiaomiAirQualityNumberDescription(
        key="screensaver_time",
        name="Screen Save Time",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=NumberDeviceClass.DURATION,
        icon="mdi:clock",
        native_min_value=0,
        native_max_value=180,
        native_step=1
    ),
    XiaomiAirQualityNumberDescription(
        key="auto_slideing_time",
        name="Auto Slideing Time",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=NumberDeviceClass.DURATION,
        icon="mdi:clock",
        native_min_value=0,
        native_max_value=3600,
        native_step=1
    ),
    XiaomiAirQualityNumberDescription(
        key="screensaver_type",
        name="Screen Saver Type",
        icon="mdi:cog",
        native_min_value=0,
        native_max_value=10,
        native_step=1
    ),
    XiaomiAirQualityNumberDescription(
        key="device_off_new",
        name="Device Off New",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=NumberDeviceClass.DURATION,
        icon="mdi:clock-outline",
        native_min_value=0,
        native_max_value=65535,
        native_step=1
    ),
    XiaomiAirQualityNumberDescription(
        key="is_twelve_hours_sys",
        name="Is Twelve Hours",
        icon="mdi:cog",
        native_min_value=0,
        native_max_value=1,
        native_step=1
    ),
    XiaomiAirQualityNumberDescription(
        key="pm_tpf_standard",
        name="PM  TPF Standard",
        icon="mdi:cog",
        native_min_value=0,
        native_max_value=255,
        native_step=1
    )
)
