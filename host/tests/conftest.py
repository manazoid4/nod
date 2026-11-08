"""Give every test process (each pytest-xdist worker) its own home, so default ~/.maz-pocket
databases are never shared between parallel workers or written into the real home folder."""
import os
import tempfile

_home = tempfile.mkdtemp(prefix=f"piblo-test-{os.environ.get('PYTEST_XDIST_WORKER', 'main')}-")
os.environ["HOME"] = os.environ["USERPROFILE"] = _home
os.environ["MAZ_DATA_DIR"] = os.path.join(_home, "data")
