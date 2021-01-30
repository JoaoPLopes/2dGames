class Controller():
    ''' Simple Proportional Controller
    '''
    def __init__(self, Kp):
        self.Kp = Kp

    def control(self, ref, y):
        return (ref-y)*self.Kp