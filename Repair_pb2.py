# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Repair.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cRepair.proto\"3\n\x0cInterconnect\x12\x0e\n\x06source\x18\x01 \x01(\t\x12\x13\n\x0b\x64\x65stination\x18\x02 \x01(\t\"P\n\x0eSwitchingLogic\x12\r\n\x05index\x18\x01 \x01(\r\x12\x10\n\x03phy\x18\x02 \x01(\tH\x00\x88\x01\x01\x12\x15\n\x03mux\x18\x03 \x03(\x0b\x32\x08.ControlB\x06\n\x04_phy\"*\n\x07\x43ontrol\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\tselection\x18\x02 \x01(\t\"p\n\x0bRepairLogic\x12\x13\n\x06signal\x18\x01 \x01(\tH\x00\x88\x01\x01\x12 \n\x07\x64\x65\x66\x61ult\x18\x02 \x01(\x0b\x32\x0f.SwitchingLogic\x12\x1f\n\x06repair\x18\x03 \x03(\x0b\x32\x0f.SwitchingLogicB\t\n\x07_signal\"\xde\x01\n\x07\x42undles\x12\x1b\n\x13\x46nInterconnectCount\x18\x01 \x01(\x05\x12\x1c\n\x14PhyInterconnectCount\x18\x02 \x01(\x05\x12\x17\n\x0f\x44\x65tourPathCount\x18\x03 \x01(\x05\x12\x19\n\x02\x46n\x18\x04 \x03(\x0b\x32\r.Interconnect\x12\x1a\n\x03Phy\x18\x05 \x03(\x0b\x32\r.Interconnect\x12#\n\rTXRepairLogic\x18\x06 \x03(\x0b\x32\x0c.RepairLogic\x12#\n\rRXRepairLogic\x18\x07 \x03(\x0b\x32\x0c.RepairLogic\"7\n\x06\x41rrays\x12\x13\n\x0b\x42undleCount\x18\x01 \x01(\x05\x12\x18\n\x06\x42undle\x18\x02 \x03(\x0b\x32\x08.Bundlesb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'Repair_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_INTERCONNECT']._serialized_start=16
  _globals['_INTERCONNECT']._serialized_end=67
  _globals['_SWITCHINGLOGIC']._serialized_start=69
  _globals['_SWITCHINGLOGIC']._serialized_end=149
  _globals['_CONTROL']._serialized_start=151
  _globals['_CONTROL']._serialized_end=193
  _globals['_REPAIRLOGIC']._serialized_start=195
  _globals['_REPAIRLOGIC']._serialized_end=307
  _globals['_BUNDLES']._serialized_start=310
  _globals['_BUNDLES']._serialized_end=532
  _globals['_ARRAYS']._serialized_start=534
  _globals['_ARRAYS']._serialized_end=589
# @@protoc_insertion_point(module_scope)
