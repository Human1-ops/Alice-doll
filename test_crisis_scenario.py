import subprocess
import sys
import os

def run_scenario(inputs):
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    process = subprocess.run(
        [sys.executable, 'crisis_scenario.py'],
        input='\n'.join(inputs) + '\n',
        text=True,
        capture_output=True,
        env=env
    )
    return process.stdout

def test_path_a_yes():
    stdout = run_scenario(['a', 'yes'])
    assert "Crisis #1" in stdout
    assert "all right everyone is all gone the teacher is asking why I’m still sitting. Should I be honest yes or no" in stdout
    assert "thank you so much the teacher helped me and said it is ok everyone makes a slip up sometimes." in stdout

def test_path_a_no():
    stdout = run_scenario(['a', 'no'])
    assert "Crisis #1" in stdout
    assert "all right everyone is all gone the teacher is asking why I’m still sitting. Should I be honest yes or no" in stdout
    assert "she says the teacher walked up to me and said here’s some paper towels everyone makes mistakes sometimes." in stdout

def test_path_b():
    stdout = run_scenario(['b'])
    assert "Crisis #1" in stdout
    assert "thank you so much ripping off the bandage works so much better it was so embarrassing but I managed to survive." in stdout

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
