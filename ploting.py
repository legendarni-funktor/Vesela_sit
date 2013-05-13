import matplotlib.pyplot as plt
import numpy

class Plot():
    
    def __init__(self):
        self.error = [[],[]]
        self.x_axe = [i for i in xrange(20)]
        plt.ion()
        self.ax_len = 10
        plt.subplot(2, 1, 2)
        plt.axis([-0.05,self.ax_len,0,3])
        plt.show()
        
    def update(self, new_error):
        self.error[0].append(new_error[0])
        self.error[1].append(new_error[1])
        plt.subplot(2, 1, 2)
        if len(self.error[1]) > self.ax_len:
            self.ax_len += 2
        plt.axis([-0.05,self.ax_len,0, max(3, max(self.error[0]) + 0.1)])
        plt.plot(self.error[0],'r-.o', label='Quadratic mean of errors')
        plt.subplot(2, 1, 1)
        plt.axis([-0.05,self.ax_len,0,max(self.error[1]) + 1])
        plt.plot(self.error[1], 'g-o', label='Sum of error')# ,self.x_axe, self.error[1], 'g-')
        plt.draw()
        plt.savefig('Learning_curve')