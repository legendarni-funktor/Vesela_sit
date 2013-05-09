from random import random as rand, shuffle
import math

from ploting import Plot
from preprocess import create_valid_train_preproc_sets, normalize_sets

lamb = 1
odchylka = 1
topologie = [4900,700,150,1]

#training_set = [([1,2,3],[0]),([2,2,3],[0]),([1,1,1],[0]),([3,1,1],[1])]
training_set = []
validation = []

def epsilon(time):
    return 0.2
#    return max(0.3, 0.8/math.log(math.e + time + 1)**2)

def trans_function_derivation(potencial):
    return lamb * sigmoid(potencial) * (1 - sigmoid(potencial))

def sigmoid(x):
    return 1/(1+math.e**(x*(-1*lamb)))

def error(v1, v2):
    output = 0
    if len(v1) != len(v2):
        print "Odecitas vektory z jine dimenze!"
    for i in xrange(len(v1)):
        output += (v1[i] - v2[i])**2
    return output/2


def scal(v1, v2):
    output = 0
    try:
        if len(v1) != len(v2):
            print "Nasobis vektory z jine dimenze!"
    except:
        pass
    for i in xrange(len(v1)):
        output += v1[i] * v2[i]
    return output

                
                
class Neuron():
    
    def __init__(self, n_inputs):
        self.weights = [rand() - 0.5 for _ in xrange(n_inputs)]
#        self.weights = [(rand() / (n_inputs**(0.5)/3**0.5)) * (-1)**(math.floor(10*rand())%2) for _ in xrange(n_inputs)]
        self.bias = 0
        self.transfer_input = 0
        self.output = 0
        self.derive = 0
        self.der_vah = []
    
    def transf_function(self):
        return sigmoid(self.tran_input)
        
    def calculate_output(self, input_vector):        
        self.tran_input = scal(input_vector, self.weights) + self.bias
        self.output = self.transf_function()
        return self.output

    
        
        
class Layer():
    
    def __init__(self, n_neurons, n_inputs):
        self.neurons = [Neuron(n_inputs) for _ in xrange(n_neurons)]
        
    def evaluate_neurons(self, prev_out):
        output = []
        for neuron in self.neurons:
            neuron.calculate_output(prev_out)
            output.append(neuron.output)            
        return output
            

class First_layer():

    def __init__(self, n_neurons):
        self.neurons = [Neuron(0) for _ in xrange(n_neurons)]

    def evaluate_neurons(self, in_put):
        output = []
        for i, neuron in enumerate(self.neurons):
            neuron.calculate_output([in_put[i]])
            output.append(neuron.output)            
        return output


class Network():
    
    def __init__(self, config):
        self.layers = []
        for i in xrange(len(config) - 1):
            self.layers.append(Layer(config[i + 1], config[i]))
    
    def calc_out(self, in_put):
        for layer in self.layers:
            layer_out = layer.evaluate_neurons(in_put)
            in_put = layer_out
        return layer_out

    def net_error(self):
        output = 0
        for vzor in training_set:
            (x,d) = vzor
#            print self.calc_out(x)
            output += error(self.calc_out(x), d)**2
        return ((output / len(training_set))**(0.5), output)

    def partial_derivation_of_error(self, d):
        for i, neuron in enumerate(self.layers[-1].neurons):
            neuron.derive = neuron.output - d[i]
        #for i in xrange(len(self.layers[len(self.layers) - 1].neurons)):
            #self.layers[len(self.layers) - 1].neurons[i].derive = self.layers[len(self.layers) - 1].neurons[i].output - d[i]

        rest_of_layers = list(self.layers)
        rest_of_layers.reverse()
        rest_of_layers.pop(0)
        for i in xrange(len(rest_of_layers) - 1):
            for j, neuron in enumerate(rest_of_layers[i-1].neurons):
                mezisoucet = 0
                for neuron_nad_nim in rest_of_layers[i].neurons:
                    try:
                        mezisoucet += neuron_nad_nim.derive * trans_function_derivation(neuron_nad_nim.transfer_input) * neuron_nad_nim.weights[j]
                    except: 
                        pass
                neuron.derive = mezisoucet

    def weight_correction(self, vzor, time):
        (x,d) = vzor
        self.calc_out(x)
        self.partial_derivation_of_error(d)
        for i in xrange(len(self.layers) - 1):
            for neuron in self.layers[i+1].neurons:
                neuron.der_vah = []
                for neuron_pod_nim in self.layers[i].neurons:
                    neuron.der_vah.append(neuron.derive * trans_function_derivation(neuron.transfer_input) * neuron_pod_nim.output)
        
        for i in range(len(self.layers)-1):
            for neuron in self.layers[i+1].neurons:
                for j in xrange(len(neuron.weights)):
                    neuron.weights[j] -= epsilon(time) * neuron.der_vah[j]

                   
net = Network(topologie)


print "Preprocessing..."
normalize_sets()
create_valid_train_preproc_sets(validation, training_set)
shuffle(training_set)
print "Preprocessing successfully finished!\n"

print "Getting clever!..."
error_plot = Plot()

for i in xrange(100):
    current_error = net.net_error()
    error_plot.update(current_error)
    
    if current_error[0] < 0.01 and current_error[1] < 0.1:
        break
    print current_error
    for vzor in training_set:
        net.weight_correction(vzor,i)
        

for vzor in training_set:
    print str(vzor[1]) + " == " + str(net.calc_out(vzor[0]))
print 'Bagr_NO.1'
for valid_vzor in validation:    
    print str(valid_vzor[1]) + " == " + str(net.calc_out(valid_vzor[0]))
