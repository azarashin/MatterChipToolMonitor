from environment import Environment
from command_executor import CommandExecutor
from chiptool_pairing import ChipToolPairing
from chiptool_endpoint_list import ChipToolEndpointList

import getpass

class ChipToolController:
  def __init__(self):
    self._env = Environment()
    self._executor = CommandExecutor()
    self._pairing = ChipToolPairing(self._env, self._executor)
    self._endpoint_list = ChipToolEndpointList(self._env, self._executor)

  def get_node_id(self):
    id = input('input NodeID:')
    return id

  def pairing(self):
    node_id = self.get_node_id()
    passcode = getpass.getpass('Passcode: ')
    descriptor = getpass.getpass('Descriptor: ')
    self._pairing.find(node_id, passcode, descriptor)
    print(self._env.get_device_info(node_id))

  def pairing_without_discriminator(self):
    node_id = self.get_node_id()
    passcode = getpass.getpass('Passcode: ')
    self._pairing.find_without_discriminator(node_id, passcode)
    print(self._env.get_device_info(node_id))

  def show_device_list(self):
    node_id = self.get_node_id()
    self._endpoint_list.get_list(node_id)
    print(self._env.get_device_info(node_id))

  def remove_all_devices(self):
    self._env.remove_all_devices()

  def run(self):
    while True:
      print('1. pairing with discriminator')
      print('2. pairing without discriminator')
      print('3. show device list')

      print('99. remove_all_devices')
      id = input('input option: ')
      if id == '1':
        self.pairing()
      if id == '2':
        self.pairing_without_discriminator()
      if id == '3':
        self.show_device_list()
      if id == '99':
        self.remove_all_devices()


if __name__ == '__main__':
  controller = ChipToolController()
  controller.run()

