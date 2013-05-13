from random import random as rand, shuffle
import math
import simplejson as json
import os, time

from ploting import Plot
from preprocess import create_valid_train_preproc_sets, normalize_sets

dump_train_set = False

lamb = 1
odchylka = 1
width = 100
height = 55
size = [width, height]

topologie = [width * height, 300, 80, 1]

training_set = []
validation = []


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
        self.bias = 0
        self.transfer_input = 0
        self.output = 0
        self.derive = 0
        self.der_vah = []
#    @profile
    def transf_function(self):
        return sigmoid(self.tran_input)
#    @profile    
    def calculate_output(self, input_vector):        
        self.tran_input = scal(input_vector, self.weights) + self.bias
        self.output = self.transf_function()
        return self.output

    
        
        
class Layer():
    
    def __init__(self, n_neurons, n_inputs):
        self.neurons = [Neuron(n_inputs) for _ in xrange(n_neurons)]
#    @profile    
    def evaluate_neurons(self, prev_out):
        output = []
        for neuron in self.neurons:
            neuron.calculate_output(prev_out)
            output.append(neuron.output)            
        return output
            

class First_layer():

    def __init__(self, n_neurons):
        self.neurons = [Neuron(0) for _ in xrange(n_neurons)]
#    @profile
    def evaluate_neurons(self, in_put):
        output = []
        for i, neuron in enumerate(self.neurons):
            neuron.calculate_output([in_put[i]])
            output.append(neuron.output)            
        return output


class Network():
    
    def __init__(self, config):
        self.layers = []
        self.before_last = 0
        self.last = 0
        self.queue = [0.001, 0.001, 0.001]
        self.queue_eps = [0.2, 0.2, 0.2]
        self.eps = 0.1
        for i in xrange(len(config) - 1):
            self.layers.append(Layer(config[i + 1], config[i]))
#    @profile     
    def calc_out(self, in_put):
        for layer in self.layers:
            layer_out = layer.evaluate_neurons(in_put)
            in_put = layer_out
        return layer_out        
    
#    @profile
    def epsilon_update(self, time):
        self.queue_eps.pop(0)
        self.queue_eps.append(max(min(0.05 + ( sum(self.queue)/len(self.queue) ) * 50, 1), 0.005))
        if time > 2:
            self.eps = sum(self.queue_eps) / len(self.queue_eps)
        else:
            return 0.2
        
    def epsilon(self, time):
        return self.eps

#    @profile
    def net_error(self, training_set):
        output = 0
        correct_output = 0
        for vzor in training_set:
            (x,d) = vzor
            net_output = self.calc_out(x)
            output += error(net_output, d)**2
            if int(round(net_output[0])) == d[0]: #pocita kolikrat sit vyhodnotila vzor spravne
                correct_output += 1
                
        return float(correct_output)/len(training_set), ((output / len(training_set))**(0.5), output)
    
#    @profile
    def partial_derivation_of_error(self, d):
        for i, neuron in enumerate(self.layers[-1].neurons):
            neuron.derive = neuron.output - d[i]
    
        rest_of_layers = list(self.layers)
        rest_of_layers.reverse()
        rest_of_layers.pop(0)
        for i in xrange(len(rest_of_layers) - 1):
            for j, neuron in enumerate(rest_of_layers[i-1].neurons):
                mezisoucet = 0
                for neuron_nad_nim in rest_of_layers[i].neurons:
                    mezisoucet += neuron_nad_nim.derive * trans_function_derivation(neuron_nad_nim.transfer_input) * neuron_nad_nim.weights[j]
                neuron.derive = mezisoucet
    
#    @profile
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
                    neuron.weights[j] -= self.epsilon(time) * neuron.der_vah[j]

                   
net = Network(topologie)


print "Preprocessing..."
preproc_strat_time = time.time()
if dump_train_set or not os.path.isfile("trainin_set_dump.json"):
    normalize_sets()
    create_valid_train_preproc_sets(validation, training_set, size)
    
    file = open("trainin_set_dump.json", "w+")
    json.dump([training_set, validation], file)
    file.flush()
    file.close()
    
else:
    file = open("trainin_set_dump.json", "r")
    training_set, validation = json.loads(file.read())
    
    
print "    Every day I'm shuffling!!!! (data sets)"
shuffle(training_set)
training_set = training_set[0:60]
print "Preprocessing successfully finished in time: {0:.2f}secs!\n".format(time.time() - preproc_strat_time)


print "Getting clever!..."
print '    This may take a while so... Try to relax...'
learning_time = time.time()
error_plot = Plot()

for i in xrange(100):
    accuracy, current_error = net.net_error(training_set)
    error_plot.update(current_error, accuracy)
    
    net.before_last = net.last
    net.last = current_error[0]
    net.queue.pop(0)
    net.queue.append(net.before_last - net.last)
    net.epsilon_update(i)
    
    print "    Current epsilon: {0:.2f}".format(net.eps)
    
    if current_error[0] < 0.06 and current_error[1] < 0.1:
        break
    for vzor in training_set:
        net.weight_correction(vzor,i)

print "Learning finished in time: {0:.2f}sec\n".format(time.time() - learning_time)        

print "Calculating accuracy..."
acc_sum = 0
for valid_vzor in validation:
    net_out = net.calc_out(valid_vzor[0])
    if valid_vzor[1][0] == int(round(net_out[0])):
        acc_sum += 1
     
print "Network accuracy: {0:.3f}".format(float(acc_sum)/len(validation))