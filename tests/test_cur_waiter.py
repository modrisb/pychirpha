"""Regression test: cur_waiter must close the cur window without spinning."""

import threading
import time

from pychirpha.mqtt import ChirpToHA


def _make_bridge(cur_age):
    """Build a bare ChirpToHA with only what cur_waiter needs."""
    bridge = object.__new__(ChirpToHA)
    # attributes close() (called from __del__) touches
    bridge._client = None
    bridge._ha_online_event = None
    bridge._dev_check_event = None
    bridge._wait_for_cur = None
    bridge._wait_for_ha_online = None
    bridge._wait_for_dev_check = None
    bridge._client_closing = False
    bridge._cur_delay_event = threading.Event()
    bridge._cur_age = cur_age
    bridge._cur_open_time = time.time()
    bridge.disabled = threading.Event()
    bridge.disable_cur = bridge.disabled.set
    return bridge


def test_cur_waiter_closes_window_without_busy_loop():
    """Window not extended: cur_waiter closes it right after cur_age and uses no CPU."""
    bridge = _make_bridge(cur_age=0.2)
    cpu = {}

    def run():
        start = time.thread_time()
        bridge.cur_waiter()
        cpu["used"] = time.thread_time() - start

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    closed = bridge.disabled.wait(2)
    bridge._client_closing = True  # let a spinning loop exit so the test ends
    bridge._cur_delay_event.set()
    thread.join(2)
    assert closed, "cur window was never closed (cur_waiter stuck in its loop)"
    assert cpu["used"] < 0.1


def test_cur_waiter_honours_extended_window():
    """Window extended by enable_cur(): cur_waiter waits until the new end."""
    bridge = _make_bridge(cur_age=0.4)
    thread = threading.Thread(target=bridge.cur_waiter, daemon=True)
    started = time.time()
    thread.start()
    time.sleep(0.2)
    bridge._cur_open_time = time.time()  # what enable_cur() does
    closed = bridge.disabled.wait(2)
    elapsed = time.time() - started
    bridge._client_closing = True
    bridge._cur_delay_event.set()
    thread.join(2)
    assert closed
    assert elapsed >= 0.55, f"window closed too early ({elapsed:.2f}s)"
