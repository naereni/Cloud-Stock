class A:
    def __init__(self,a):
        self.a = a
    
    def p(self):
        print(self.a)

class B(A):
    def __init__(self):
        super().__init__(2)

b = B()
b.p()