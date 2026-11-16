"""Master tests package — suite-wide watsonx isolation."""
import atexit
import os
import tempfile

# ---------------------------------------------------------------------------
# Suite-wide isolation: remove all WATSONX_* keys so child processes (and
# the test process itself) never hit the network or the real state file.
# A temporary state file is created and registered for atexit cleanup so
# subprocesses that inherit the environment use it instead of the default.
# ---------------------------------------------------------------------------
for _k in [k for k in list(os.environ) if k.startswith("WATSONX_")]:
    del os.environ[_k]

_SUITE_STATE_FILE = os.path.join(tempfile.gettempdir(), "watsonx_agent1_test_suite_state.json")
os.environ["WATSONX_STATE_FILE"] = _SUITE_STATE_FILE


def _cleanup_suite_state_file() -> None:
    try:
        os.unlink(_SUITE_STATE_FILE)
    except OSError:
        pass


atexit.register(_cleanup_suite_state_file)
