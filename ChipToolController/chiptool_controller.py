from environment import Environment
from command_executor import CommandExecutor
from chiptool_pairing import ChipToolPairing
from chiptool_endpoint_list import ChipToolEndpointList
from device_type import DeviceType
from cluster import Cluster
from chiptool_device_list import ChipToolDeviceList
from chiptool_server_cluster_list import ChipToolServerClusterList
from chiptool_client_cluster_list import ChipToolClientClusterList

import getpass
import json

class ChipToolController:
  def __init__(self):
    self._env = Environment()
    self._executor = CommandExecutor()
    self._device_type_dic = DeviceType()
    self._cluster_dic = Cluster()
    self._pairing = ChipToolPairing(self._env, self._executor)
    self._endpoint_list = ChipToolEndpointList(self._env, self._executor)
    self._device_type_list = ChipToolDeviceList(self._env, self._executor, self._device_type_dic)
    self._server_cluster_list = ChipToolServerClusterList(self._env, self._executor, self._cluster_dic)
    self._client_cluster_list = ChipToolClientClusterList(self._env, self._executor, self._cluster_dic)

  def get_node_id(self):
    id = input('input NodeID:')
    return int(id)

  def get_endpoint_id(self):
    id = input('input EndpointID:')
    return int(id)

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

  def show_endpoint_list(self):
    node_id = self.get_node_id()
    ret, raw = self._endpoint_list.get_list(node_id)
#    ret, raw = self._endpoint_list.get_list(1234)
    print(json.dumps(ret, indent=4, ensure_ascii=False))
    print(self._env.get_device_info(node_id))

  def show_device_type_list(self):
    node_id = self.get_node_id()
    endpoint_id = self.get_endpoint_id()
    ret, raw = self._device_type_list.get_list(node_id, endpoint_id)
    print(json.dumps(ret, indent=4, ensure_ascii=False))
    print(self._env.get_device_info(node_id))

  def show_server_cluster_list(self):
    node_id = self.get_node_id()
    endpoint_id = self.get_endpoint_id()
    ret, raw = self._server_cluster_list.get_list(node_id, endpoint_id)
    print(json.dumps(ret, indent=4, ensure_ascii=False))
    print(self._env.get_device_info(node_id))

  def show_client_cluster_list(self):
    node_id = self.get_node_id()
    endpoint_id = self.get_endpoint_id()
    ret, raw = self._client_cluster_list.get_list(node_id, endpoint_id)
    print(json.dumps(ret, indent=4, ensure_ascii=False))
    print(self._env.get_device_info(node_id))

  def show_device_info(self):
    node_id = self.get_node_id()
    print(self._env.get_device_info(node_id))
    print(self._env.get_endpoint_id_list(node_id))

  def remove_all_devices(self):
    self._env.remove_all_devices()

  def auto_pairing(self):
    node_id = self.get_node_id()
    passcode = getpass.getpass('Passcode: ')
    self._pairing.find_without_discriminator(node_id, passcode)
    self._endpoint_list.get_list(node_id)
    endpoint_ids = self._env.get_endpoint_id_list(node_id)
    for endpoint_id in endpoint_ids:
      self._device_type_list.get_list(node_id, endpoint_id)
      self._server_cluster_list.get_list(node_id, endpoint_id)
      self._client_cluster_list.get_list(node_id, endpoint_id)


  def run(self):
    while True:
      print('0. pairing then get all infomation automatically')
      print('1. pairing with discriminator')
      print('2. pairing without discriminator')
      print('3. show endpoint list')
      print('4. show device type list')
      print('5. show server cluster list')
      print('6. show client cluster list')
      print('90. show device info')

      print('99. remove_all_devices')
      id = input('input option: ')
      if id == '0':
        self.auto_pairing()
      if id == '1':
        self.pairing()
      if id == '2':
        self.pairing_without_discriminator()
      if id == '3':
        self.show_endpoint_list()
      if id == '4':
        self.show_device_type_list()
      if id == '5':
        self.show_server_cluster_list()
      if id == '6':
        self.show_client_cluster_list()
      if id == '90':
        self.show_device_info()
      if id == '99':
        self.remove_all_devices()


if __name__ == '__main__':
  controller = ChipToolController()
  controller.run()

