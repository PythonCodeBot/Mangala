import copy

class B():
    def __init__(self, value):
        self.va = value

    def set_val(self, new_value):
        self.va = new_value

    def print_val(self, msg=""):
        print(msg, self.va)

a = B(69)
b = copy.deepcopy(a)
b.set_val(420)

a.print_val("this is a:")
b.print_val("this is b:")
