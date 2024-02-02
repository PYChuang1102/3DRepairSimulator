import MicroBumpLayout_pb2
import Repair_pb2

class Checker:
    def __init__(self, layouts):
        self.dies = layouts
        self.mapping = None

    def check_duplicate_signals(self):
        for array in self.dies:
            for bump in array.protomarray.MicroBump:
                if len(bump.signal) != 0:
                    return False
        return True

    def check_signal_mapping(self):
        for array in self.dies:
            # Please implement your code
            continue
        else:
            print("No signal mapping rules.")
            return False