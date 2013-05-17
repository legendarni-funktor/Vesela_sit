import matplotlib.pyplot as plt
import numpy

class Plot():
    
    def __init__(self, size, topologie):
        self.size = size
        self.topologie = topologie
        
        self.error = [[],[]]
        self.error_valid = [[],[]]
        self.accuracy_list = []
        self.accuracy_valid_list = []
        self.x_axe = [i for i in xrange(20)]
        
        plt.figure(figsize=(22, 9), dpi=80)
        plt.ion()
        self.ax_len = 10
        
    def update(self, new_error, accuracy, new_error_valid, accuracy_valid):
        self.accuracy_list.append(accuracy)
        self.accuracy_valid_list.append(accuracy_valid)
        self.error[0].append(new_error[0])
        self.error[1].append(new_error[1])
        self.error_valid[0].append(new_error_valid[0])
        self.error_valid[1].append(new_error_valid[1])
        
        if len(self.error[1]) > self.ax_len:
            self.ax_len += 4
        
        plt.subplot(3, 1, 3)
        plt.axis([-0.05,self.ax_len,0, 1])
        plt.plot(self.accuracy_list,'b-.o', label='Accuracy_train')
        plt.plot(self.accuracy_valid_list,'g-o', label='Accuracy_valid')
        
        plt.subplot(3, 1, 2)            
        plt.axis([-0.05,self.ax_len,0, max(self.error[0]) + 0.1])
        plt.plot(self.error[0],'r-.o', label='Quad errors')
        plt.plot(self.error_valid[0],'g-o', label='Quad errors_valid')
        
        plt.subplot(3, 1, 1)
        plt.axis([-0.05,self.ax_len,0, max(self.error[1])  + 1])
        plt.plot(self.error[1], 'b-.o', label='Sum error')# ,self.x_axe, self.error[1], 'g-')
        plt.plot(self.error_valid[1], 'g-o', label='Sum error_valid')
        
        if len(self.accuracy_list) == 1:
            for i in xrange(3):
                plt.subplot(3, 1, i+1)
                plt.legend(loc='upper right')
        plt.draw()
        
        plt.savefig('Learning_curve')
        
    def save_plot(self, acc):
        
        plt.savefig('Figures/Learning_curve_Topo:' + str(self.topologie) + 'Size:' + str(self.size) + 'Acc: ' + str(int(acc*100)) + '%')