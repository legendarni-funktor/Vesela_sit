import matplotlib.pyplot as plt
import numpy

class Plot():
    
    def __init__(self, size, topologie):
        self.size = size
        self.topologie = topologie
        
        self.error = [[],[]]
        self.accuracy_list = []
        self.x_axe = [i for i in xrange(20)]
        
        plt.figure(figsize=(22, 9), dpi=80)
        plt.ion()
        self.ax_len = 10
        
    def update(self, new_error, accuracy):
        self.accuracy_list.append(accuracy)
        self.error[0].append(new_error[0])
        self.error[1].append(new_error[1])
        
        if len(self.error[1]) > self.ax_len:
            self.ax_len += 2
        
        plt.subplot(3, 1, 3)
        plt.axis([-0.05,self.ax_len,0, 1])
        plt.plot(self.accuracy_list,'b-o', label='Accuracy')
        
        plt.subplot(3, 1, 2)            
        plt.axis([-0.05,self.ax_len,0, max(self.error[0]) + 0.1])
        plt.plot(self.error[0],'r-.o', label='Quadratic mean of errors')
        
        plt.subplot(3, 1, 1)
        plt.axis([-0.05,self.ax_len,0, max(self.error[1]) + 1])
        plt.plot(self.error[1], 'g-o', label='Sum of error')# ,self.x_axe, self.error[1], 'g-')
        
        if len(self.accuracy_list) == 1:
            for i in xrange(3):
                plt.subplot(3, 1, i+1)
                plt.legend(loc='upper left')
        plt.draw()
        
        plt.savefig('Learning_curve')
        
    def save_plot(self, acc):
        
        plt.savefig('Figures/Learning_curve_Topo:' + str(self.topologie) + 'Size:' + str(self.size) + 'Acc: ' + str(int(acc*100)) + '%')