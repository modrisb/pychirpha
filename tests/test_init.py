"""Test the ChirpStack LoRaWAN integration initilization path initiated from start.py."""
import logging
import time
from tests import common
import pytest
import json
from pathlib import Path
from unittest import mock

from .patches import get_size, mqtt, set_size
from tests.common import NO_APP_CONFIGURATION_FILE, MIN_SLEEP, REGULAR_CONFIGURATION_NONZERO_DELAYS, REGULAR_CONFIGURATION_FILE
from pychirpha.const import WARMSG_APPID_WRONG, DETAILED_LEVEL_NUM
from pychirpha.start import INTERNAL_CONFIG
from pychirpha.mqtt import ChirpToHA

_LOGGER = logging.getLogger(__name__)

@pytest.fixture(autouse=True)
def cleanup():
    """Reset mock settings and close mqtt connection if needed."""
    mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).reset_mock()    #   default mock settings
    yield
    # teardown - close mqtt connection if needed
    mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).reset_mock()    #   default mock settings

def test_entry_setup_unload(caplog):
    """Test if integration unloads with default configuration."""

    common.chirp_setup_and_run_test(caplog, None)

def test_grpc_connection_failure(caplog):
    """Test app exits in case of grpc failure."""

    common.chirp_setup_and_run_test(caplog, None, test_params=dict(grpc=0), a_live_at_end=False)

def test_setup_with_no_tenants(caplog):
    """Test if missing tenant has been creted and app is up."""

    common.chirp_setup_and_run_test(caplog, None, test_params=dict(tenants=0), a_live_at_end=True, conf_file=NO_APP_CONFIGURATION_FILE, allowed_msg_level=logging.WARNING)
    i_sensor_warn = 0
    i_sensor_ten = 0
    for record in caplog.records:
        if record.msg == WARMSG_APPID_WRONG: i_sensor_warn += 1
        if "Tenant '" in record.msg: i_sensor_ten += 1
    assert i_sensor_warn == 1 and i_sensor_ten == 1

def test_setup_with_autoselected_tenant_no_apps(caplog):
    """Test if integration unloads with default configuration."""

    common.chirp_setup_and_run_test(caplog, None, test_params=dict(tenants=1, applications=0), a_live_at_end=True, conf_file=NO_APP_CONFIGURATION_FILE, allowed_msg_level=logging.WARNING)
    i_sensor_warn = 0
    i_sensor_app = 0
    for record in caplog.records:
        if record.msg == WARMSG_APPID_WRONG: i_sensor_warn += 1
        if "Application '" in record.msg: i_sensor_app += 1
    assert i_sensor_warn == 1 and i_sensor_app == 1

def test_setup_with_tenant_selection_no_apps(caplog):
    """Test if integration unloads with default configuration."""

    common.chirp_setup_and_run_test(caplog, None, conf_file=NO_APP_CONFIGURATION_FILE, test_params=dict(applications=0), a_live_at_end=True, allowed_msg_level=logging.WARNING)
    i_sensor_warn = 0
    i_sensor_app = 0
    for record in caplog.records:
        if record.msg == WARMSG_APPID_WRONG: i_sensor_warn += 1
        if "Application '" in record.msg: i_sensor_app += 1
    assert i_sensor_app == 1
    assert i_sensor_warn == 1

def test_setup_with_auto_tenant_auto_apps(caplog):
    """Test if integration unloads with default configuration."""

    common.chirp_setup_and_run_test(caplog, None, test_params=dict(tenants=1, applications=1), a_live_at_end=True, conf_file=NO_APP_CONFIGURATION_FILE, allowed_msg_level=logging.WARNING)
    i_sensor_warn = 0
    for record in caplog.records:
        if record.msg == WARMSG_APPID_WRONG: i_sensor_warn += 1
    assert i_sensor_warn == 1

def test_setup_with_auto_tenant_apps_selection(caplog):
    """Test if integration unloads with default configuration."""

    common.chirp_setup_and_run_test(caplog, None, test_params=dict(tenants=1, applications=2), a_live_at_end=True, conf_file=NO_APP_CONFIGURATION_FILE, allowed_msg_level=logging.WARNING)
    i_sensor_warn = 0
    for record in caplog.records:
        if record.msg == WARMSG_APPID_WRONG: i_sensor_warn += 1
    assert i_sensor_warn == 1

def test_setup_with_auto_tenant_auto_apps_mqtt_fail(caplog):
    """Test if chirpha gracefully exits in case of mqtt connection failure."""

    common.chirp_setup_and_run_test(caplog, None, test_params=dict(tenants=1, mqtt=0), a_live_at_end=False)
    assert "Chirp failed:" in caplog.text

def test_setup_with_auto_tenant_auto_apps_mqtt(caplog):
    """Test if integration unloads with default configuration."""

    common.chirp_setup_and_run_test(caplog, None, test_params=dict(tenants=1), a_live_at_end=True)

def test_thread_kill(caplog):
    """Test forced exit from chirpha."""

    def run_test_thread_kill(config):
        set_size(codec=7)
        common.reload_devices(config)
        assert get_size("devices") * get_size("sensors") == mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).stat_sensors

    common.chirp_setup_and_run_test(caplog, run_test_thread_kill, kill_at_end=True)
    assert "Shutdown requested" in caplog.text

def test_setup_with_failing_mqtt_publish(caplog):
    """Test if chirpha gracefully exits in case of mqtt publish failure."""

    common.chirp_setup_and_run_test(caplog, None, test_params=dict(publish=0), a_live_at_end=False, check_msg_queue=False)
    assert "Chirp failed:" in caplog.text

def test_setup_with_failing_mqtt_subscribe(caplog):
    """Test if chirpha gracefully exits in case of mqtt subscribe failure."""

    common.chirp_setup_and_run_test(caplog, None, test_params=dict(subscribe=0), a_live_at_end=False, check_msg_queue=False)
    assert "Chirp failed:" in caplog.text

def test_setup_with_failing_mqtt_unsubscribe(caplog):
    """Test if chirpha gracefully exits in case of mqtt unsubscribe failure."""
    caplog.set_level(DETAILED_LEVEL_NUM)

    def run_test_setup_with_failing_mqtt_unsubscribe(config):
        _LOGGER.info("run_test_setup_with_failing_mqtt_unsubscribe config %s", config)
        mqtt.Client(mqtt.CallbackAPIVersion.VERSION2).wait_empty_queue()
        time.sleep(1)

    common.chirp_setup_and_run_test(caplog, run_test_setup_with_failing_mqtt_unsubscribe, conf_file=REGULAR_CONFIGURATION_NONZERO_DELAYS, test_params=dict(unsubscribe=0), a_live_at_end=False, check_msg_queue=True)
    assert "Chirp failed(1):" in caplog.text

@mock.patch("pychirpha.mqtt.mqtt", new=mqtt)
def test_mqtt_connectivity_only(caplog):
    """Test if chirpha gracefully exits in case of mqtt unsubscribe failure."""
    path_to_conf = Path(__file__).with_name(REGULAR_CONFIGURATION_FILE)
    with path_to_conf.open() as file:
        config = json.load(file)
    config = config | INTERNAL_CONFIG

    grpc_client_mock = lambda: None  # noqa: E731
    grpc_client_mock.application_id = "appid0"
    grpc_client_mock.gateway_id = "gatewayid0"
    ChirpToHA(config, None, None, grpc_client_mock, connectivity_check_only=True).close()

    assert mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)._publish_count == 0
    assert not mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)._published
    assert not mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)._subscribed
    assert not mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)._connected
    assert mqtt.Client(mqtt.CallbackAPIVersion.VERSION2). on_message is None
    assert mqtt.Client(mqtt.CallbackAPIVersion.VERSION2). on_connect is None
    assert mqtt.Client(mqtt.CallbackAPIVersion.VERSION2). on_publish is None
    assert mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)._stat_start_time == 0
    assert mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)._stat_dev_eui is None
    assert mqtt.Client(mqtt.CallbackAPIVersion.VERSION2). stat_devices == 0
    assert mqtt.Client(mqtt.CallbackAPIVersion.VERSION2). stat_sensors == 0
    assert mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)._open_count == 0
    assert not mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)._run_loop
    assert mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)._block_loop

def test_exit_before_ha_online(caplog):
    """Test if chirpha gracefully exits in case of mqtt subscribe failure."""

    common.chirp_setup_and_run_test(caplog, None, a_live_at_end=True, no_ha_online=True, check_msg_queue=False, kill_at_end=True, check_devices=False)
    assert "HA online, continuing configuration" not in caplog.text
