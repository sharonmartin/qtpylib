
import sys
import logging

from qtpylib import (
    tools, asynctools, path, futures, __version__
)

from qtpylib.crypto_updater import crypto_updater
# =============================================
# check min, python version
if sys.version_info < (3, 4):
    raise SystemError("QTPyLib requires Python version >= 3.4")

# =============================================
# Configure logging
tools.createLogger(__name__, logging.INFO)

# Disable ezIBpy logging (Blotter handles errors itself)
logging.getLogger('ezibpy').setLevel(logging.CRITICAL)

# =============================================

class BtcConn(object):

    # -----------------------------------------
    # generic callback function - can be used externally
    # -----------------------------------------
    def callback(self, timestamp, value):
        pass

    def start(self):
        crypto_updater.start_websocket(1, ["bitcoin"], self.callback)

    def stop(self):
        crypto_updater.abort_websocket()
