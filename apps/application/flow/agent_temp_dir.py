# coding=utf-8
"""Per-run temp directories for agent shell backends."""

import os

import uuid_utils.compat as uuid


def agent_run_temp_dir(chat_id=None) -> str:
    """Return a per-run workspace under /tmp for agent shell tools.

    When ``chat_id`` is present it is included as a prefix for debugging, but
    a fresh uuid is always appended so two overlapping runs never share a
    directory that either side would ``rmtree`` on exit (#7625).
    """
    run_id = str(uuid.uuid7())
    if chat_id:
        return os.path.join("/tmp", f"{chat_id}-{run_id}")
    return os.path.join("/tmp", run_id)
