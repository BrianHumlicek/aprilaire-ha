from custom_components.aprilaire.coordinator import AprilaireCoordinator
from custom_components.aprilaire.const import DOMAIN
from custom_components.aprilaire.sensor import (
    async_setup_entry,
    BaseAprilaireTemperatureSensor,
    AprilaireIndoorHumidityControllingSensor,
    AprilaireOutdoorHumidityControllingSensor,
    AprilaireIndoorTemperatureControllingSensor,
    AprilaireOutdoorTemperatureControllingSensor,
    AprilaireDehumidificationStatusSensor,
    AprilaireHumidificationStatusSensor,
    AprilaireVentilationStatusSensor,
    AprilaireAirCleaningStatusSensor,
)

from homeassistant.config_entries import ConfigEntry, ConfigEntries
from homeassistant.core import Config, HomeAssistant, EventBus
from homeassistant.util import uuid as uuid_util
from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)

from homeassistant.const import (
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    PERCENTAGE,
)

import unittest
from unittest.mock import AsyncMock, Mock


class Test_Sensor(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.coordinator_mock = AsyncMock(AprilaireCoordinator)
        self.coordinator_mock.data = {}

        self.entry_id = uuid_util.random_uuid_hex()

        self.hass_mock = AsyncMock(HomeAssistant)
        self.hass_mock.data = {DOMAIN: {self.entry_id: self.coordinator_mock}}
        self.hass_mock.config_entries = AsyncMock(ConfigEntries)
        self.hass_mock.bus = AsyncMock(EventBus)
        self.hass_mock.config = Mock(Config)

        self.config_entry_mock = AsyncMock(ConfigEntry)
        self.config_entry_mock.data = {"host": "test123", "port": 123}
        self.config_entry_mock.entry_id = self.entry_id

    async def test_no_sensors_without_data(self):
        async_add_entities_mock = Mock()

        await async_setup_entry(
            self.hass_mock, self.config_entry_mock, async_add_entities_mock
        )

        async_add_entities_mock.assert_called_once_with([])

    def test_temperature_sensor_unit_of_measurement_sensor_option(self):
        base_sensor = BaseAprilaireTemperatureSensor(self.coordinator_mock)
        base_sensor.hass = self.hass_mock

        base_sensor._sensor_option_unit_of_measurement = TEMP_CELSIUS
        self.assertEqual(base_sensor.safe_unit_of_measurement, TEMP_CELSIUS)

        base_sensor._sensor_option_unit_of_measurement = TEMP_FAHRENHEIT
        self.assertEqual(base_sensor.safe_unit_of_measurement, TEMP_FAHRENHEIT)

    def test_temperature_sensor_unit_of_measurement_suggested_unit_of_measurement(self):
        base_sensor = BaseAprilaireTemperatureSensor(self.coordinator_mock)
        base_sensor.hass = self.hass_mock

        base_sensor._attr_suggested_unit_of_measurement = TEMP_CELSIUS
        self.assertEqual(base_sensor.safe_unit_of_measurement, TEMP_CELSIUS)

        base_sensor._attr_suggested_unit_of_measurement = TEMP_FAHRENHEIT
        self.assertEqual(base_sensor.safe_unit_of_measurement, TEMP_FAHRENHEIT)

    def test_temperature_sensor_unit_of_measurement_config(self):
        base_sensor = BaseAprilaireTemperatureSensor(self.coordinator_mock)
        base_sensor.hass = self.hass_mock

        self.hass_mock.config.units = METRIC_SYSTEM
        self.assertEqual(base_sensor.safe_unit_of_measurement, TEMP_CELSIUS)

        self.hass_mock.config.units = US_CUSTOMARY_SYSTEM
        self.assertEqual(base_sensor.safe_unit_of_measurement, TEMP_FAHRENHEIT)

    def test_base_temperature_sensor_value(self):
        base_sensor = BaseAprilaireTemperatureSensor(self.coordinator_mock)
        base_sensor.hass = self.hass_mock
        self.hass_mock.config.units = METRIC_SYSTEM

        self.assertIsNone(base_sensor.native_value)
        self.assertIsNone(base_sensor.get_native_value())

    async def test_indoor_humidity_controlling_sensor(self):
        test_value = 50

        self.coordinator_mock.data = {
            "indoor_humidity_controlling_sensor_status": 0,
            "indoor_humidity_controlling_sensor_value": test_value,
        }

        async_add_entities_mock = Mock()

        await async_setup_entry(
            self.hass_mock, self.config_entry_mock, async_add_entities_mock
        )

        sensors_list = async_add_entities_mock.call_args_list[0][0]

        self.assertEqual(len(sensors_list), 1)

        sensor = sensors_list[0][0]

        self.assertIsInstance(sensor, AprilaireIndoorHumidityControllingSensor)

        sensor._available = True

        self.assertEqual(sensor.device_class, SensorDeviceClass.HUMIDITY)
        self.assertEqual(sensor.state_class, SensorStateClass.MEASUREMENT)
        self.assertEqual(sensor.native_unit_of_measurement, PERCENTAGE)
        self.assertTrue(sensor.available)
        self.assertEqual(sensor.native_value, test_value)
        self.assertEqual(sensor.entity_name, "Indoor Humidity Controlling Sensor")
        self.assertEqual(sensor.extra_state_attributes["status"], 0)
        self.assertEqual(sensor.extra_state_attributes["raw_sensor_value"], test_value)

    async def test_outdoor_humidity_controlling_sensor(self):
        test_value = 50

        self.coordinator_mock.data = {
            "outdoor_humidity_controlling_sensor_status": 0,
            "outdoor_humidity_controlling_sensor_value": test_value,
        }

        async_add_entities_mock = Mock()

        await async_setup_entry(
            self.hass_mock, self.config_entry_mock, async_add_entities_mock
        )

        sensors_list = async_add_entities_mock.call_args_list[0][0]

        self.assertEqual(len(sensors_list), 1)

        sensor = sensors_list[0][0]

        self.assertIsInstance(sensor, AprilaireOutdoorHumidityControllingSensor)

        sensor._available = True

        self.assertEqual(sensor.device_class, SensorDeviceClass.HUMIDITY)
        self.assertEqual(sensor.state_class, SensorStateClass.MEASUREMENT)
        self.assertEqual(sensor.native_unit_of_measurement, PERCENTAGE)
        self.assertTrue(sensor.available)
        self.assertEqual(sensor.native_value, test_value)
        self.assertEqual(sensor.entity_name, "Outdoor Humidity Controlling Sensor")
        self.assertEqual(sensor.extra_state_attributes["status"], 0)
        self.assertEqual(sensor.extra_state_attributes["raw_sensor_value"], test_value)

    async def test_indoor_temperature_controlling_sensor(self):
        test_value = 25

        self.coordinator_mock.data = {
            "indoor_temperature_controlling_sensor_status": 0,
            "indoor_temperature_controlling_sensor_value": test_value,
        }

        async_add_entities_mock = Mock()

        await async_setup_entry(
            self.hass_mock, self.config_entry_mock, async_add_entities_mock
        )

        sensors_list = async_add_entities_mock.call_args_list[0][0]

        self.assertEqual(len(sensors_list), 1)

        sensor = sensors_list[0][0]

        self.assertIsInstance(sensor, AprilaireIndoorTemperatureControllingSensor)

        sensor._available = True
        sensor._sensor_option_unit_of_measurement = TEMP_CELSIUS

        self.assertEqual(sensor.device_class, SensorDeviceClass.TEMPERATURE)
        self.assertEqual(sensor.state_class, SensorStateClass.MEASUREMENT)
        self.assertEqual(sensor.native_unit_of_measurement, TEMP_CELSIUS)
        self.assertTrue(sensor.available)
        self.assertEqual(sensor.native_value, test_value)
        self.assertEqual(sensor.entity_name, "Indoor Temperature Controlling Sensor")
        self.assertEqual(sensor.extra_state_attributes["status"], 0)
        self.assertEqual(sensor.extra_state_attributes["raw_sensor_value"], test_value)

    async def test_outdoor_temperature_controlling_sensor(self):
        test_value = 25

        self.coordinator_mock.data = {
            "outdoor_temperature_controlling_sensor_status": 0,
            "outdoor_temperature_controlling_sensor_value": test_value,
        }

        async_add_entities_mock = Mock()

        await async_setup_entry(
            self.hass_mock, self.config_entry_mock, async_add_entities_mock
        )

        sensors_list = async_add_entities_mock.call_args_list[0][0]

        self.assertEqual(len(sensors_list), 1)

        sensor = sensors_list[0][0]

        self.assertIsInstance(sensor, AprilaireOutdoorTemperatureControllingSensor)

        sensor._available = True
        sensor._sensor_option_unit_of_measurement = TEMP_CELSIUS

        self.assertEqual(sensor.device_class, SensorDeviceClass.TEMPERATURE)
        self.assertEqual(sensor.state_class, SensorStateClass.MEASUREMENT)
        self.assertEqual(sensor.native_unit_of_measurement, TEMP_CELSIUS)
        self.assertTrue(sensor.available)
        self.assertEqual(sensor.native_value, test_value)
        self.assertEqual(sensor.entity_name, "Outdoor Temperature Controlling Sensor")
        self.assertEqual(sensor.extra_state_attributes["status"], 0)
        self.assertEqual(sensor.extra_state_attributes["raw_sensor_value"], test_value)

    def test_indoor_temperature_controlling_sensor_fahrenheit(self):
        test_value = 25

        self.coordinator_mock.data = {
            "indoor_temperature_controlling_sensor_status": 0,
            "indoor_temperature_controlling_sensor_value": test_value,
        }

        sensor = AprilaireIndoorTemperatureControllingSensor(self.coordinator_mock)
        sensor._available = True
        sensor._sensor_option_unit_of_measurement = TEMP_FAHRENHEIT

        self.assertEqual(sensor.device_class, SensorDeviceClass.TEMPERATURE)
        self.assertEqual(sensor.state_class, SensorStateClass.MEASUREMENT)
        self.assertEqual(sensor.native_unit_of_measurement, TEMP_FAHRENHEIT)
        self.assertTrue(sensor.available)
        self.assertEqual(sensor.native_value, 77)
        self.assertEqual(sensor.entity_name, "Indoor Temperature Controlling Sensor")
        self.assertEqual(sensor.extra_state_attributes["status"], 0)
        self.assertEqual(sensor.extra_state_attributes["raw_sensor_value"], test_value)

    def test_outdoor_temperature_controlling_sensor_fahrenheit(self):
        test_value = 25

        self.coordinator_mock.data = {
            "outdoor_temperature_controlling_sensor_status": 0,
            "outdoor_temperature_controlling_sensor_value": test_value,
        }

        sensor = AprilaireOutdoorTemperatureControllingSensor(self.coordinator_mock)
        sensor._available = True
        sensor._sensor_option_unit_of_measurement = TEMP_FAHRENHEIT

        self.assertEqual(sensor.device_class, SensorDeviceClass.TEMPERATURE)
        self.assertEqual(sensor.state_class, SensorStateClass.MEASUREMENT)
        self.assertEqual(sensor.native_unit_of_measurement, TEMP_FAHRENHEIT)
        self.assertTrue(sensor.available)
        self.assertEqual(sensor.native_value, 77)
        self.assertEqual(sensor.entity_name, "Outdoor Temperature Controlling Sensor")
        self.assertEqual(sensor.extra_state_attributes["status"], 0)
        self.assertEqual(sensor.extra_state_attributes["raw_sensor_value"], test_value)

    async def test_dehumidification_available(self):
        self.coordinator_mock.data = {
            "dehumidification_available": 1,
        }

        async_add_entities_mock = Mock()

        await async_setup_entry(
            self.hass_mock, self.config_entry_mock, async_add_entities_mock
        )

        sensors_list = async_add_entities_mock.call_args_list[0][0]

        self.assertEqual(len(sensors_list), 1)

        sensor = sensors_list[0][0]

        self.assertIsInstance(sensor, AprilaireDehumidificationStatusSensor)

    def test_dehumidification_status_sensor_0(self):
        self.coordinator_mock.data = {
            "dehumidification_status": 0,
        }

        sensor = AprilaireDehumidificationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Dehumidification Status")
        self.assertEqual(sensor.native_value, "Idle")

    def test_dehumidification_status_sensor_1(self):
        self.coordinator_mock.data = {
            "dehumidification_status": 1,
        }

        sensor = AprilaireDehumidificationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Dehumidification Status")
        self.assertEqual(sensor.native_value, "Idle")

    def test_dehumidification_status_sensor_2(self):
        self.coordinator_mock.data = {
            "dehumidification_status": 2,
        }

        sensor = AprilaireDehumidificationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Dehumidification Status")
        self.assertEqual(sensor.native_value, "On")

    def test_dehumidification_status_sensor_3(self):
        self.coordinator_mock.data = {
            "dehumidification_status": 3,
        }

        sensor = AprilaireDehumidificationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Dehumidification Status")
        self.assertEqual(sensor.native_value, "On")

    def test_dehumidification_status_sensor_4(self):
        self.coordinator_mock.data = {
            "dehumidification_status": 4,
        }

        sensor = AprilaireDehumidificationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Dehumidification Status")
        self.assertEqual(sensor.native_value, "Off")

    def test_dehumidification_status_sensor_5(self):
        self.coordinator_mock.data = {
            "dehumidification_status": 5,
        }

        sensor = AprilaireDehumidificationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Dehumidification Status")
        self.assertIsNone(sensor.native_value)

    async def test_humidification_available(self):
        self.coordinator_mock.data = {
            "humidification_available": 1,
        }

        async_add_entities_mock = Mock()

        await async_setup_entry(
            self.hass_mock, self.config_entry_mock, async_add_entities_mock
        )

        sensors_list = async_add_entities_mock.call_args_list[0][0]

        self.assertEqual(len(sensors_list), 1)

        sensor = sensors_list[0][0]

        self.assertIsInstance(sensor, AprilaireHumidificationStatusSensor)

    def test_humidification_status_sensor_0(self):
        self.coordinator_mock.data = {
            "humidification_status": 0,
        }

        sensor = AprilaireHumidificationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Humidification Status")
        self.assertEqual(sensor.native_value, "Idle")

    def test_humidification_status_sensor_1(self):
        self.coordinator_mock.data = {
            "humidification_status": 1,
        }

        sensor = AprilaireHumidificationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Humidification Status")
        self.assertEqual(sensor.native_value, "Idle")

    def test_humidification_status_sensor_2(self):
        self.coordinator_mock.data = {
            "humidification_status": 2,
        }

        sensor = AprilaireHumidificationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Humidification Status")
        self.assertEqual(sensor.native_value, "On")

    def test_humidification_status_sensor_3(self):
        self.coordinator_mock.data = {
            "humidification_status": 3,
        }

        sensor = AprilaireHumidificationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Humidification Status")
        self.assertEqual(sensor.native_value, "Off")

    def test_humidification_status_sensor_4(self):
        self.coordinator_mock.data = {
            "humidification_status": 4,
        }

        sensor = AprilaireHumidificationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Humidification Status")
        self.assertIsNone(sensor.native_value)

    async def test_ventilation_available(self):
        self.coordinator_mock.data = {
            "ventilation_available": 1,
        }

        async_add_entities_mock = Mock()

        await async_setup_entry(
            self.hass_mock, self.config_entry_mock, async_add_entities_mock
        )

        sensors_list = async_add_entities_mock.call_args_list[0][0]

        self.assertEqual(len(sensors_list), 1)

        sensor = sensors_list[0][0]

        self.assertIsInstance(sensor, AprilaireVentilationStatusSensor)

    def test_ventilation_status_sensor_0(self):
        self.coordinator_mock.data = {
            "ventilation_status": 0,
        }

        sensor = AprilaireVentilationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Ventilation Status")
        self.assertEqual(sensor.native_value, "Idle")

    def test_ventilation_status_sensor_1(self):
        self.coordinator_mock.data = {
            "ventilation_status": 1,
        }

        sensor = AprilaireVentilationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Ventilation Status")
        self.assertEqual(sensor.native_value, "Idle")

    def test_ventilation_status_sensor_2(self):
        self.coordinator_mock.data = {
            "ventilation_status": 2,
        }

        sensor = AprilaireVentilationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Ventilation Status")
        self.assertEqual(sensor.native_value, "On")

    def test_ventilation_status_sensor_3(self):
        self.coordinator_mock.data = {
            "ventilation_status": 3,
        }

        sensor = AprilaireVentilationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Ventilation Status")
        self.assertEqual(sensor.native_value, "Idle")

    def test_ventilation_status_sensor_4(self):
        self.coordinator_mock.data = {
            "ventilation_status": 4,
        }

        sensor = AprilaireVentilationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Ventilation Status")
        self.assertEqual(sensor.native_value, "Idle")

    def test_ventilation_status_sensor_5(self):
        self.coordinator_mock.data = {
            "ventilation_status": 5,
        }

        sensor = AprilaireVentilationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Ventilation Status")
        self.assertEqual(sensor.native_value, "Idle")

    def test_ventilation_status_sensor_5(self):
        self.coordinator_mock.data = {
            "ventilation_status": 5,
        }

        sensor = AprilaireVentilationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Ventilation Status")
        self.assertEqual(sensor.native_value, "Idle")

    def test_ventilation_status_sensor_6(self):
        self.coordinator_mock.data = {
            "ventilation_status": 6,
        }

        sensor = AprilaireVentilationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Ventilation Status")
        self.assertEqual(sensor.native_value, "Off")

    def test_ventilation_status_sensor_7(self):
        self.coordinator_mock.data = {
            "ventilation_status": 7,
        }

        sensor = AprilaireVentilationStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Ventilation Status")
        self.assertIsNone(sensor.native_value)

    async def test_air_cleaning_available(self):
        self.coordinator_mock.data = {
            "air_cleaning_available": 1,
        }

        async_add_entities_mock = Mock()

        await async_setup_entry(
            self.hass_mock, self.config_entry_mock, async_add_entities_mock
        )

        sensors_list = async_add_entities_mock.call_args_list[0][0]

        self.assertEqual(len(sensors_list), 1)

        sensor = sensors_list[0][0]

        self.assertIsInstance(sensor, AprilaireAirCleaningStatusSensor)

    def test_air_cleaning_status_sensor_0(self):
        self.coordinator_mock.data = {
            "air_cleaning_status": 0,
        }

        sensor = AprilaireAirCleaningStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Air Cleaning Status")
        self.assertEqual(sensor.native_value, "Idle")

    def test_air_cleaning_status_sensor_1(self):
        self.coordinator_mock.data = {
            "air_cleaning_status": 1,
        }

        sensor = AprilaireAirCleaningStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Air Cleaning Status")
        self.assertEqual(sensor.native_value, "Idle")

    def test_air_cleaning_status_sensor_2(self):
        self.coordinator_mock.data = {
            "air_cleaning_status": 2,
        }

        sensor = AprilaireAirCleaningStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Air Cleaning Status")
        self.assertEqual(sensor.native_value, "On")

    def test_air_cleaning_status_sensor_3(self):
        self.coordinator_mock.data = {
            "air_cleaning_status": 3,
        }

        sensor = AprilaireAirCleaningStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Air Cleaning Status")
        self.assertEqual(sensor.native_value, "Off")

    def test_air_cleaning_status_sensor_4(self):
        self.coordinator_mock.data = {
            "air_cleaning_status": 4,
        }

        sensor = AprilaireAirCleaningStatusSensor(self.coordinator_mock)
        sensor._available = True

        self.assertTrue(sensor.available)
        self.assertEqual(sensor.entity_name, "Air Cleaning Status")
        self.assertIsNone(sensor.native_value)
