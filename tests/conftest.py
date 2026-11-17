import os
import tempfile

_tmp_dir = tempfile.mkdtemp(prefix="incident-agent-test-")
os.environ["AGENT_DB_PATH"] = os.path.join(_tmp_dir, "test_agent.db")
