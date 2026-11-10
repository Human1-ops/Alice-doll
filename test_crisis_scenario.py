import subprocess
import sys
import os
import json
from datetime import date

STATE_FILE = "crisis_state.json"

def setup_state():
    state = {"last_played_date": "2000-01-01", "current_crisis_index": 0}
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def cleanup_state():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)

def run_scenario(inputs):
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    mocks_dir = os.path.join(os.path.dirname(__file__), 'mocks')
    if os.path.exists(mocks_dir):
        env['PYTHONPATH'] = mocks_dir + os.pathsep + env.get('PYTHONPATH', '')
    process = subprocess.run(
        [sys.executable, 'crisis_scenario.py'],
        input='\n'.join(inputs) + '\n',
        text=True,
        capture_output=True,
        env=env
    )
    return process.stdout

def test_path_a_yes():
    setup_state()
    stdout = run_scenario(['a', 'yes'])
    assert "Crisis #1" in stdout
    assert "all right everyone is all gone the teacher is asking why I’m still sitting. Should I be honest yes or no" in stdout
    assert "thank you so much the teacher helped me and said it is ok everyone makes a slip up sometimes." in stdout
    cleanup_state()

def test_path_a_no():
    setup_state()
    stdout = run_scenario(['a', 'no'])
    assert "Crisis #1" in stdout
    assert "all right everyone is all gone the teacher is asking why I’m still sitting. Should I be honest yes or no" in stdout
    assert "she says the teacher walked up to me and said here’s some paper towels everyone makes mistakes sometimes." in stdout
    cleanup_state()

def test_path_b():
    setup_state()
    stdout = run_scenario(['b'])
    assert "Crisis #1" in stdout
    assert "thank you so much ripping off the bandage works so much better it was so embarrassing but I managed to survive." in stdout
    cleanup_state()

def test_daily_limit():
    setup_state()
    stdout1 = run_scenario(['b'])
    assert "Crisis #1" in stdout1

    stdout2 = run_scenario(['b'])
    assert "We already handled a crisis today! Let's play again tomorrow." in stdout2
    cleanup_state()

def test_all_crises_completed():
    state = {"last_played_date": "2000-01-01", "current_crisis_index": 1}
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)
    stdout = run_scenario(['b'])
    assert "We have handled all the crises!" in stdout
    cleanup_state()

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
