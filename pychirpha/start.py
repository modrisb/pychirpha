"""The Chirpstack LoRaWAN integration - setup."""
from __future__ import annotations
__version__ = "1.1.51"

import logging
import logging.handlers
import json
import signal
import os
import sys
from pathlib import Path
from typing import Final
import threading
import traceback

from pychirpha.grpc import ChirpGrpc
from pychirpha.mqtt import ChirpToHA
from pychirpha.const import CONF_API_SERVER, CONF_API_PORT, CONF_MQTT_SERVER, CONF_MQTT_PORT, CONF_OPTIONS_LOG_LEVEL
from pychirpha.const import DEFAULT_API_SERVER, DEFAULT_API_PORT, DEFAULT_MQTT_PORT, DEFAULT_MQTT_SERVER
from pychirpha.const import CONF_MQTT_CHIRPSTACK_PREFIX, DEFAULT_MQTT_CHIRPSTACK_PREFIX, CLASSES, DETAILED_LEVEL_STR

# Date/Time formats
FORMAT_DATE: Final = "%Y-%m-%d"
FORMAT_TIME: Final = "%H:%M:%S"
FORMAT_DATETIME: Final = f"{FORMAT_DATE} {FORMAT_TIME}"
FMT = ( "%(asctime)s.%(msecs)03d chirpha %(levelname)s %(message)s" )

CONFIGURATION_FILE = '/data/options.json'

_LOGGER = logging.getLogger(__name__)

INTERNAL_CONFIG = {
  CONF_API_SERVER: DEFAULT_API_SERVER,
  CONF_API_PORT: DEFAULT_API_PORT,
  CONF_MQTT_SERVER: DEFAULT_MQTT_SERVER,
  CONF_MQTT_PORT: DEFAULT_MQTT_PORT,
  CONF_MQTT_CHIRPSTACK_PREFIX: DEFAULT_MQTT_CHIRPSTACK_PREFIX,
}

class run_chirp_ha:
    def __init__(self, configuration_file) -> None:
        self._grpc_client = None
        self._mqtt_client = None
        self._config = None
        self._configuration_file = configuration_file
        signal.signal(signal.SIGTERM, self.stop_chirp_ha)
        threading.excepthook = self.subthread_failed

    def subthread_failed(self, args):
        _LOGGER.error("Chirp failed(1): %s : %s", args.exc_value, traceback.format_tb(args.exc_traceback))
        self.close_mqtt_loop()

    def stop_chirp_ha(self, signum, frame):
        _LOGGER.info("Shutdown requested")
        self.close_mqtt_loop()

    def close_mqtt_loop(self):
        if self._mqtt_client:   # close to exit server loop
            _LOGGER.info("Closing MQTT connection")
            self._mqtt_client.close()
            self._mqtt_client = None

    def main(self):
        logging.basicConfig(level=logging.INFO, format=FMT, datefmt=FORMAT_DATETIME)
        config = None
        try:
            with open(self._configuration_file, 'r') as file:
                config = json.load(file)
            config = INTERNAL_CONFIG | config
            self._config = config
            _LOGGER.debug("Configuration %s:", self._config)
            _LOGGER.info("ChirpHA started")
            try:
                logging.getLogger().setLevel(config[CONF_OPTIONS_LOG_LEVEL].upper())
            except Exception as error:  # noqa: F841
                _LOGGER.warning("Wrong log level specified '%s', assuming 'info'", config[CONF_OPTIONS_LOG_LEVEL])
                config[CONF_OPTIONS_LOG_LEVEL] = 'info'
            _LOGGER.debug("Logging level %s", config[CONF_OPTIONS_LOG_LEVEL].upper())
            _LOGGER.detail("Current directory %s, module directory %s", os.getcwd(), str(Path(__file__).absolute().parent))
            _LOGGER.detail("Configuration file %s", self._configuration_file)
            _LOGGER.info("Version %s", __version__)
            self._grpc_client = ChirpGrpc(config, __version__)
            self._mqtt_client = ChirpToHA(config, __version__, CLASSES, self._grpc_client)
            self._mqtt_client._client.loop_forever()
        except Exception as error:
            if logging.getLogger().getEffectiveLevel() in (logging.DEBUG, DETAILED_LEVEL_STR):
                _LOGGER.exception("Chirp failed: %s", str(error))
            else:
                _LOGGER.error("Chirp failed: %s", str(error))
        finally:
            if self._mqtt_client:
                _LOGGER.info("Closing MQTT connection")
                self._mqtt_client.close()
                self._mqtt_client = None
            if self._grpc_client:
                _LOGGER.info("Closing gRPC connection")
                self._grpc_client.close()
                self._grpc_client = None
        _LOGGER.info("ChirpHA done")

if __name__=='__main__':
    run_chirp_ha(sys.argv[1] if len(sys.argv)>1 else CONFIGURATION_FILE).main()
    _LOGGER.info("Done.")
