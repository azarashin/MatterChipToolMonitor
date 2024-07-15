import subprocess
import time

class CommandExecutor:
  def __init__(self, animation=True):
    self._animation = animation

  def run(self, commands, hide_indexes = []):
    if self._animation:
      show_commands = [commands[d] if not d in hide_indexes else '*' * len(commands[d]) for d in range(len(commands))]
      body = str.join(' ', show_commands)
      for ch in body:
        print(ch, end='', flush=True)
        time.sleep(0.02)
      print('\n')

    return subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

if __name__ == '__main__':
  executor = CommandExecutor(True)
  executor.run(['echo', 'show', 'hide'], [2])
