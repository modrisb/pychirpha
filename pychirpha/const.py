"""The ChirpStack LoRaWAN Integration - constant definitions."""

DOMAIN = "chirp"
GRPCLIENT = "grpclient"
MQTTCLIENT = "mqttclient"
DEFAULT_NAME = "Chirp"

CONF_API_SERVER = "chirpstack_api_server"
CONF_API_PORT = "server_port"
CONF_API_KEY = "api_connection_key"
CONF_TENANT = "tenant"
CONF_APPLICATION = "application_name"
CONF_APPLICATION_ID = "application_id"

DEFAULT_API_SERVER = ""
DEFAULT_API_PORT = 8080
DEFAULT_API_KEY = ""
DEFAULT_TENANT = "ChirpStack"
DEFAULT_APPLICATION = "temp"

CONF_CHIRP_SERVER_RESERVED = "chirp_server_reserved"
CONF_ERROR_CHIRP_CONN_FAILED = "chirpstack_connection_failed"
CONF_ERROR_MQTT_CONN_FAILED = "mqtt_connection_failed"

CONF_MQTT_SERVER = "mqtt_server"
CONF_MQTT_PORT = "mqtt_port"
CONF_MQTT_USER = "mqtt_user"
CONF_MQTT_PWD = "mqtt_password"
CONF_MQTT_DISC = "discovery_prefix"
CONF_MQTT_CHIRPSTACK_PREFIX = "mqtt_chirpstack_prefix"

DEFAULT_MQTT_SERVER = "localhost"
DEFAULT_MQTT_PORT = 1883
DEFAULT_MQTT_USER = ""
DEFAULT_MQTT_PWD = ""
DEFAULT_MQTT_DISC = "homeassistant"
DEFAULT_MQTT_CHIRPSTACK_PREFIX = ""

CHIRPSTACK_TENANT = "HA owned"
CHIRPSTACK_APPLICATION = "HA integration"
CHIRPSTACK_API_KEY_NAME = "chirpha"

CONF_OPTIONS_START_DELAY = "options_start_delay"
DEFAULT_OPTIONS_START_DELAY = 2
CONF_OPTIONS_RESTORE_AGE = "options_restore_age"
DEFAULT_OPTIONS_RESTORE_AGE = 4
CONF_OPTIONS_DEBUG_PAYLOAD = "options_debug_print_payload"
DEFAULT_OPTIONS_DEBUG_PAYLOAD = False

MQTT_ORIGIN = "ChirpLora"
BRIDGE_VENDOR = "Chirp2MQTT"
BRIDGE_NAME = "Chirp2MQTT Bridge"
BRIDGE = "Bridge"
BRIDGE_STATE_ID = "state"
BRIDGE_ENTITY_NAME = "Connection state"
INTEGRATION_DEV_NAME = "ChirpStack LoRaWAN Integration"
CONNECTIVITY_DEVICE_CLASS = "connectivity"
BRIDGE_RESTART_ID = "restart"
BRIDGE_RESTART_NAME = "Reload devices"

STATISTICS_SENSORS = "chirp_sensors"
STATISTICS_DEVICES = "chirp_devices"
STATISTICS_UPDATED = "chirp_updated"
RELOAD_BUTTON = "chirp_reload"

CONF_OPTIONS_LOG_LEVEL = "options_log_level"
CONF_OPTIONS_ONLINE_PER_DEVICE = "options_online_per_device"
CONF_OPTIONS_EXPIRE_AFTER = "options_add_expire_after"
DEFAULT_OPTIONS_LOG_LEVEL = "info"
DEFAULT_OPTIONS_EXPIRE_AFTER = False
DEFAULT_OPTIONS_ONLINE_PER_DEVICE = 0
BRIDGE_LOGLEVEL_ID = "log_level"
BRIDGE_LOGLEVEL_NAME = "Log level"

BRIDGE_CONF_COUNT = 3

ENTITY_CATEGORY_DIAGNOSTIC = "diagnostic"

ERRMSG_CODEC_ERROR = "Profile %s discovery codec script error '%s', source code '%s' converted to json '%s'"
ERRMSG_DEVICE_IGNORED = "Discovery codec (%s->%s) missing or faulty for device %s with profile %s, device ignored"
WARMSG_APPID_WRONG = "'%s' is not valid application ID, using '%s' (tenant '%s' with ID '%s', application name '%s')"
WARMSG_DEVCLS_REMOVED = "Could not detect integration by device class %s for device %s, integration set to 'sensor', device class removed"
WARMSG_DISC_AUTO = "Profile %s discovery codec script not found, generating one, will use manufacturer name '%s', device name '%s', baterry '%s'"

DETAILED_LEVEL_NUM = 5
DETAILED_LEVEL_STR = "DETAIL"

CLASSES = {
  "alarm_control_panel": [],
  "binary_sensor": [
    "battery",
    "battery_charging",
    "carbon_monoxide",
    "cold",
    "connectivity",
    "door",
    "garage_door",
    "gas",
    "heat",
    "light",
    "lock",
    "moisture",
    "motion",
    "moving",
    "occupancy",
    "opening",
    "plug",
    "power",
    "presence",
    "problem",
    "running",
    "safety",
    "smoke",
    "sound",
    "tamper",
    "update",
    "vibration",
    "window"
  ],
  "button": ["identify", "restart", "update"],
  "camera": [],
  "climate": [],
  "cover": [
    "awning",
    "blind",
    "curtain",
    "damper",
    "door",
    "garage",
    "gate",
    "shade",
    "shutter",
    "window"
  ],
  "device_tracker": [],
  "device_trigger": [],
  "event": ["button", "doorbell", "motion"],
  "fan": [],
  "humidifier": ["humidifier", "dehumidifier"],
  "image": [],
  "integrations": [
    "sensor",
    "alarm_control_panel",
    "binary_sensor",
    "button",
    "camera",
    "cover",
    "device_tracker",
    "device_trigger",
    "event",
    "fan",
    "humidifier",
    "image",
    "climate",
    "lawn_mower",
    "light",
    "lock",
    "notify",
    "number",
    "scene",
    "select",
    "siren",
    "switch",
    "update",
    "tag_scanner",
    "text",
    "vacuum",
    "valve",
    "water_heater"
  ],
  "lawn_mower": [],
  "light": [],
  "lock": [],
  "media_player": ["tv", "speaker", "receiver"],
  "notify": [],
  "number": [
    "apparent",
    "aqi",
    "area",
    "atmospheric_pressure",
    "battery",
    "blood_glocose_concentration",
    "carbon_dioxide",
    "carbon_monoxide",
    "current",
    "data_rate",
    "data_size",
    "distance",
    "energy",
    "energy_storage",
    "frequency",
    "gas",
    "humidity",
    "illuminance",
    "irradiance",
    "moisture",
    "monetary",
    "nitrogen_dioxide",
    "nitrogen_monoxide",
    "nitrous_oxide",
    "ozone",
    "ph",
    "pm1",
    "pm10",
    "pm25",
    "power_factor",
    "power",
    "precipitation",
    "precipitation_intensity",
    "pressure",
    "reactive_power",
    "signal_strength",
    "sound_pressure",
    "speed",
    "sulphur_dioxide",
    "temperature",
    "volatile_organic_compounds",
    "voltage",
    "volume",
    "volume_flow_rate",
    "volume_storage",
    "water",
    "weight",
    "wind_speed"
  ],
  "scene": [],
  "select": [],
  "sensor": [
    "date",
    "enum",
    "timestamp",
    "apparent_power",
    "aqi",
    "atmospheric_pressure",
    "battery",
    "carbon_monoxide",
    "carbon_dioxide",
    "current",
    "data_rate",
    "data_size",
    "distance",
    "duration",
    "energy",
    "energy_storage",
    "frequency",
    "gas",
    "humidity",
    "illuminance",
    "irradiance",
    "moisture",
    "monetary",
    "nitrogen_dioxide",
    "nitrogen_monoxide",
    "nitrous_oxide",
    "ozone",
    "ph",
    "pm1",
    "pm10",
    "pm25",
    "power_factor",
    "power",
    "precipitation",
    "precipitation_intensity",
    "pressure",
    "reactive_power",
    "signal_strength",
    "sound_pressure",
    "speed",
    "sulphur_dioxide",
    "temperature",
    "volatile_organic_compounds",
    "volatile_organic_compounds_parts",
    "voltage",
    "volume",
    "volume_storage",
    "volume_flow_rate",
    "water",
    "weight",
    "wind_speed"
  ],
  "siren": [],
  "switch": ["outlet", "switch"],
  "tag_scanner": [],
  "text": [],
  "update": ["firmware"],
  "vacuum": [],
  "valve": ["water", "gas"],
  "water_heater": []
}
