"""Common routines/constants for bridge tests."""
from unittest import mock
from unittest.mock import patch
import threading
import json
import time
import re
import logging
from pathlib import Path
import pytest
import sys

from pychirpha.const import (
    CONF_APPLICATION_ID,
    CONF_MQTT_DISC,
)
import pychirpha.start as chirpha
from pychirpha.start import INTERNAL_CONFIG
from pychirpha.const import CONF_OPTIONS_LOG_LEVEL, BRIDGE_CONF_COUNT, CONF_MQTT_CHIRPSTACK_PREFIX, CONF_OPTIONS_START_DELAY

from .patches import api, message, mqtt, set_size, get_size , grpc

_LOGGER = logging.getLogger(__name__)

REGULAR_CONFIGURATION_FILE ="test_configuration.json"
REGULAR_CONFIGURATION_FILE_INFO ="test_configuration_info_log.json"
REGULAR_CONFIGURATION_FILE_ERROR ="test_configuration_error_log.json"
REGULAR_CONFIGURATION_FILE_WRONG_LOG_LEVEL ="test_configuration_wrong_log_level.json"
PAYLOAD_PRINT_CONFIGURATION_FILE ="test_configuration_payload.json"
NO_APP_CONFIGURATION_FILE ="test_configuration_no_app.json"
WITH_DELAY_CONFIGURATION_FILE ="test_configuration_delay.json"
REGULAR_CONFIGURATION_FILE_INFO_NO_MQTT ="test_configuration_info_log_no_mqtt.json"
REGULAR_CONFIGURATION_FILE_DEBUG_NO_MQTT ="test_configuration_debug_log_no_mqtt.json"
REGULAR_CONFIGURATION_PER_DEVICE ="test_configuration_per_device.json"
REGULAR_CONFIGURATION_NONZERO_DELAYS ="test_configuration_nonzero_delays.json"
REGULAR_CONFIGURATION_EXPIRE_AFTER ="test_configuration_expire_after.json"
MIN_SLEEP = 0.1

# pytest tests/components/chirp/
# pytest tests/components/chirp/ --cov=homeassistant.components.chirp --cov-report term-missing -vv
# $PYTHONPATH rootfs/usr
# PATH  /home/modrisb/contributions/pijups/chirpstack/rootfs/usr/tests:/home/modrisb/.vscode/extensions/ms-python.python-2024.4.1/python_files/deactivate/bash:/home/modrisb/contributions/pijups/chirpstack/.venv/bin:/home/modrisb/.nvm/versions/node/v18.18.1/bin:/home/modrisb/.vscode/extensions/ms-python.python-2024.4.1/python_files/deactivate/bash:/home/modrisb/contributions/pijups/chirpstack/.venv/bin:/home/modrisb/contributions/pijups:/home/modrisb/.cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
# pytest chirp2mqtt/rootfs/usr/tests/ --cov=chirpha --cov-report term-missing
# pytest chirp2mqtt/rootfs/usr/tests/test_mqtt.py --cov=chirpha --cov-report term-missing --log-cli-level=DEBUG
# pytest chirp2mqtt/rootfs/usr/tests/ --cov=chirpha --cov-report term-missing --log-cli-level=DEBUG --capture=no

class run_chirp_ha:
    ch_tread = None
    cirpha_instance = None

    def __init__(self, configuration_file):
        self._configuration_file = configuration_file

        if str(Path(__file__).parent) not in sys.path:
            sys.path.append(str(Path(__file__).parent))

    def __enter__(self):
        if not self.cirpha_instance:
            self.cirpha_instance = chirpha.run_chirp_ha(self._configuration_file)
            self.ch_tread = threading.Thread(target=self.cirpha_instance.main)
            self.ch_tread.start()
        return self

    def __exit__(self, *args):
        if self.ch_tread.is_alive():
            mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).close()
            time.sleep(0)
            self.ch_tread.join()

def run(args, check=False, capture_output=True, text=True,):
    rv = lambda: None  # noqa: E731
    rv.stdout = "id: a-b-c-d\ntoken: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjaGlycHN0YWNrIiwiaXNzIjoiY2hpcnBzdGFjayIsInN1YiI6IjVkMTkxNzYwLWY4ZjItNDIzZC1hYTJlLTE1YWU3YzBiNTUxOCIsInR5cCI6ImtleSJ9.6yW5y8edBDufmd44i2jDyDsNGTGee2ba3ZG4egJYoyI"
    return rv

@mock.patch("pychirpha.grpc.api", new=api)
@mock.patch("pychirpha.grpc.grpc", new=grpc)
@mock.patch("pychirpha.mqtt.mqtt", new=mqtt)
@mock.patch("pychirpha.grpc.subprocess.run", new=run)
def chirp_setup_and_run_test(caplog, run_test_case, conf_file=REGULAR_CONFIGURATION_FILE, test_params=dict(), a_live_at_end=True, kill_at_end=False, check_msg_queue=True, allowed_msg_level=logging.INFO, no_ha_online=False, extra_conf=dict(), check_devices=True):
    """Execute test case in standard configuration environment with grpc/mqtt mocks."""

    path_to_conf = Path(__file__).with_name(conf_file)
    with path_to_conf.open() as file:
        config = json.load(file)
    for extra_key in extra_conf:
        INTERNAL_CONFIG[extra_key] = extra_conf[extra_key]
    config = config | INTERNAL_CONFIG

    set_size(**test_params)
    mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).get_published()
    log_level_mapping = logging.getLevelNamesMapping()
    log_level = log_level_mapping.get(config[CONF_OPTIONS_LOG_LEVEL].upper(), logging.INFO)
    with run_chirp_ha(path_to_conf.absolute()) as ch:
        caplog.set_level(log_level)
        time.sleep(config[CONF_OPTIONS_START_DELAY]+0.01)
        if ch.ch_tread.is_alive():
            mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).wait_empty_queue()
            if ch.ch_tread.is_alive():
                if not no_ha_online:
                    mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).publish(f"{config.get(CONF_MQTT_DISC)}/status", "online")
                mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).wait_empty_queue()
                if check_msg_queue:
                    for i in range(0,10):
                        ha_online = count_messages(r'homeassistant/status', r'online', keep_history=True)
                        bridge_online = count_messages(r'.*/bridge/status', r'online', keep_history=True)
                        bridge_config = count_messages(r'.*', r'"name"\: "Chirp2MQTT Bridge"', keep_history=True)
                        config_topics = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).get_published(keep_history=True)
                        mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).wait_empty_queue()
                        if bridge_online == 1:
                            break
                        time.sleep(0.1)
                    #print("ooooooo ", no_ha_online, i, ha_online, 1 if not no_ha_online else 0, bridge_config, bridge_online, config_topics)
                    assert ha_online == (1 if not no_ha_online else 0)   # 1 message conditionally sent from test environment
                    assert bridge_config == BRIDGE_CONF_COUNT
                    assert bridge_online == 1

                if run_test_case:
                    run_test_case(config)

                mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).wait_empty_queue()
                assert a_live_at_end == ch.ch_tread.is_alive()
                if ch.ch_tread.is_alive():
                    if check_devices:
                        assert mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).stat_sensors == get_size("sensors") * get_size("idevices")
                        assert mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).stat_devices == get_size("idevices")
                    for record in caplog.records:
                        assert record.levelno <= allowed_msg_level
                    if kill_at_end:
                        ch.cirpha_instance.stop_chirp_ha(None, None)
                        mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).wait_empty_queue()
        else:
            assert not a_live_at_end

def reload_devices(config):
    """Reload devices from ChirpStack server and wait for activity completion."""
    restart_topic = f"application/{config.get(CONF_APPLICATION_ID)}/bridge/restart"
    mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).publish(restart_topic, "")
    mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).wait_empty_queue()

def count_messages(topic, payload, keep_history=False):
    """Count posted mqtt messages that matche topic and payload filters."""
    messages = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).get_published(keep_history=keep_history)
    count = 0
    for msg in messages:
        mi_topic = re.search(topic, msg[0])
        if payload:
            if msg[1]:
                mi_payload = re.search(payload, msg[1])
                if mi_topic and mi_payload:
                    count += 1
        else:
            if mi_topic:
                count += 1

    return count

def count_messages_with_no_payload(topic, keep_history=False):
    """Count posted mqtt messages that matche topic and payload filters."""
    messages = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).get_published(keep_history=keep_history)
    count = 0
    for msg in messages:
        mi_topic = re.search(topic, msg[0])
        if mi_topic and not msg[1]:
            count += 1
    return count

def check_for_no_registration(config):
    """Check for no mqtt registration messages with assertion."""
    sensor_configs = count_messages(r'/config', r'"via_device": "chirp2mqtt_bridge_', keep_history=True)
    assert sensor_configs == 0  #   check for 0 devices/sensors registered
