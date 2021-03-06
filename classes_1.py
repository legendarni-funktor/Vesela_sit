from random import random as rand, shuffle
import math, numpy
import simplejson as json
import os, time

from ploting import Plot
from preprocess import create_valid_train_preproc_sets, normalize_sets
from support import select_path, prepare_sets

dump_data_set = False #Do you want to dump data set of preprocessed pictures?

lamb = 1
odchylka = 1
width = 100
height = 50
ratio = [0.65, 0.25, 0.1] #ratio train:valid:test
size = [width, height]

topologie = [width * height, 500, 50, 10, 1]

train_set = []
valid_set = []
test_set = []

positive = []
negative = []

#@profile
def trans_function_derivation(potencial): #Dosazena primo sigmoid - prilis caste volani.
    return lamb * (1/(1+math.e**(potencial*(-1*lamb)))) * (1 - (1/(1+math.e**(potencial*(-1*lamb)))))
##@profile
def sigmoid(x):
    return 1/(1+math.e**(x*(-1*lamb)))
#@profile
def error(v1, v2):
    output = 0
    if len(v1) != len(v2):
        print "Odecitas vektory z jine dimenze!"
    for i in xrange(len(v1)):
        output += (v1[i] - v2[i])**2
    return output/2

#@profile
def scal(v1, v2):
    output = 0
    if len(v1) != len(v2):
        print "Nasobis vektory z jine dimenze!"
    return numpy.dot(v1, v2)


class Neuron():
    
    def __init__(self, n_inputs):
        self.weights = numpy.zeros(n_inputs)
        for i in xrange(n_inputs): 
            self.weights[i] = rand() - 0.5
        self.bias = 0
        self.transfer_input = 0
        self.output = 0
        self.derive = 0
        self.der_vah = []
    #@profile
    def transf_function(self):
        return sigmoid(self.tran_input)
    #@profile    
    def calculate_output(self, input_vector):        
        self.tran_input = scal(input_vector, self.weights) + self.bias
        self.output = self.transf_function()
        return self.output

           
class Layer():
    
    def __init__(self, n_neurons, n_inputs):
        self.neurons = [Neuron(n_inputs) for _ in xrange(n_neurons)]
    #@profile    
    def evaluate_neurons(self, prev_out):
        output = []
        for neuron in self.neurons:
            neuron.calculate_output(prev_out)
            output.append(neuron.output)            
        return output
            

class First_layer():

    def __init__(self, n_neurons):
        self.neurons = [Neuron(0) for _ in xrange(n_neurons)]
    #@profile
    def evaluate_neurons(self, in_put):
        output = numpy.zeros(len(self.neurons))
        for i, neuron in enumerate(self.neurons):
            neuron.calculate_output([in_put[i]])
            output[i] = neuron.output            
        return output


class Network():
    
    def __init__(self, config):
        self.topo = config
        self.layers = []
        self.before_last = 0
        self.last = 0
        self.queue = [0.2, 0.15, 0.15]
        self.queue_eps = [0.2, 0.2, 0.2]
        self.eps = 0.1
        
        ans = raw_input("Load saved network?(y/n)\n")
        if ans == "y":
            self.load_network()
        else:
            for i in xrange(len(config) - 1):
                self.layers.append(Layer(config[i + 1], config[i]))
    #@profile     
    def calc_out(self, in_put):
        in_put_tmp = numpy.zeros(len(in_put))
        for i in xrange(len(in_put)):
            in_put_tmp[i] = in_put[i]
        in_put = in_put_tmp
        for layer in self.layers:
            layer_out = layer.evaluate_neurons(in_put)
            in_put = layer_out
        return layer_out        
    
    #@profile
    def epsilon_update(self, time):
        self.queue_eps.pop(0)
        self.queue_eps.append(max(min(0.05 + ( sum(self.queue)/len(self.queue) ) * 50, 1), 0.005))
        if time > 1:
            self.eps = sum(self.queue_eps) / len(self.queue_eps)
        else:
            return 0.2
        
    def epsilon(self, time):
        return self.eps

    #@profile
    def net_error(self, train_set):
        output = 0
        correct_output = 0
        for vzor in train_set:
            (x,d) = vzor
            net_output = self.calc_out(x)
            output += error(net_output, d)**2
            if int(round(net_output[0])) == d[0]: #pocita kolikrat sit vyhodnotila vzor spravne
                correct_output += 1
                
        return float(correct_output)/len(train_set), ((output / len(train_set))**(0.5), output)
    
    #@profile
    def partial_derivation_of_error(self, d):
        for i, neuron in enumerate(self.layers[-1].neurons):
            neuron.derive = neuron.output - d[i]
    
        rest_of_layers = list(self.layers)
        rest_of_layers.reverse()
        rest_of_layers.pop()
        for i in xrange(len(rest_of_layers) - 1):
            for j, neuron in enumerate(rest_of_layers[i + 1].neurons):
#                mezisoucet = 0 #Nahrazeno fci calculate_mezisoucet - optimalizace - mene caste volani trans_function
#                for neuron_nad_nim in rest_of_layers[i].neurons:
#                    mezisoucet += neuron_nad_nim.derive * trans_function_derivation(neuron_nad_nim.transfer_input) * neuron_nad_nim.weights[j]
#                neuron.derive = mezisoucet
                neuron.derive = self.calculate_mezisoucet(rest_of_layers[i], j)
    
    #@profile
    def calculate_mezisoucet(self, rest_of_layers_i, j):
        mezisoucet = 0
        for neuron_nad_nim in rest_of_layers_i.neurons: #ja vim, je to hnus, ale bude to rychle.
            potencial = neuron_nad_nim.transfer_input
            trans_out = lamb * (1/(1+math.e**(potencial*(-1*lamb)))) * (1 - (1/(1+math.e**(potencial*(-1*lamb)))))
            mezisoucet += neuron_nad_nim.derive * trans_out * neuron_nad_nim.weights[j]
        return mezisoucet
    
    #@profile
    def weight_correction(self, vzor, time):
        (x,d) = vzor
        self.calc_out(x)
        self.partial_derivation_of_error(d)
        for i in xrange(len(self.layers) - 1):
            for neuron in self.layers[i+1].neurons:
                neuron.der_vah = []
                self.calculate_neuron_der(i, neuron)
#                for neuron_pod_nim in self.layers[i].neurons:
#                    neuron.der_vah.append(neuron.derive * trans_function_derivation(neuron.transfer_input) * neuron_pod_nim.output)
        
        for i in range(len(self.layers)-1):
            for neuron in self.layers[i+1].neurons:
                for j in xrange(len(neuron.weights)):
                    neuron.weights[j] -= self.epsilon(time) * neuron.der_vah[j]
    #@profile
    def calculate_neuron_der(self, i, neuron):
        for neuron_pod_nim in self.layers[i].neurons:
            potencial = neuron.transfer_input
            trans_out = lamb * (1/(1+math.e**(potencial*(-1*lamb)))) * (1 - (1/(1+math.e**(potencial*(-1*lamb)))))
            neuron.der_vah.append(neuron.derive * trans_out * neuron_pod_nim.output)   
            
    def export_network(self):
        to_save = [self.topo]
        for layer in self.layers:
            to_save.append([])
            for neuron in layer.neurons:
                to_save[-1].append([w for w in neuron.weights])
        file = open("network_export_Topo:"+ str(self.topo) + ".json", "w+")
        json.dump(to_save, file)
        file.flush()
        file.close()
        
    def load_network(self):
        print "Please select the path to the json network file"
        path = select_path()
        file = open(path, "r")
        net_data = json.loads(file.read())
        self.topo = net_data[0]
        
        for i in xrange(len(self.topo) - 1):
            self.layers.append(Layer(self.topo[i + 1], self.topo[i]))
        for i, layer in enumerate(self.layers):
            for j, neuron in enumerate(layer.neurons):
                for k, weight in enumerate(net_data[i + 1][j]):
                    neuron.weights[k] = weight
                
        
        
              
net = Network(topologie)

print "Preprocessing..."
preproc_strat_time = time.time()
if dump_data_set or not os.path.isfile("trainin_set_dump_" + str(width) + "x" + str(height) + ".json"):
#    normalize_sets()
    create_valid_train_preproc_sets(positive, negative, size)
    
    file = open("trainin_set_dump_" + str(width) + "x" + str(height) + ".json", "w+")
    json.dump([positive, negative], file)
    file.flush()
    file.close()
    
else:
    file = open("trainin_set_dump_" + str(width) + "x" + str(height) + ".json", "r")
    positive, negative = json.loads(file.read())

#splits the data into train, valid and test sets
prepare_sets(positive, negative, ratio, train_set, valid_set, test_set)


print "Preprocessing successfully finished in time: {0:.2f}secs!\n".format(time.time() - preproc_strat_time)

print "Getting clever!..."
print '    This may take a while. So... Try to relax...'
learning_time = time.time()
error_plot = Plot(size, topologie)

for i in xrange(10):
    iter_time = time.time()
    
    accuracy, current_error = net.net_error(train_set)
    
    net.before_last = net.last
    net.last = current_error[0]
    net.queue.pop(0)
    net.queue.append(net.before_last - net.last)
    net.epsilon_update(i)
    
    print "    Current epsilon: {0:.2f}".format(net.eps)
    
    accuracy_valid, current_error_valid = net.net_error(valid_set)
    error_plot.update(current_error, accuracy, current_error_valid, accuracy_valid)
    
    if accuracy_valid > 0.85:
        break
    for vzor in train_set:
        net.weight_correction(vzor,i)
    print "\t\t\t\tIteration time: {0:.2f}sec".format(time.time() - iter_time)

print "Learning finished in time: {0:.2f}sec\n".format(time.time() - learning_time)        

print "Calculating accuracy..."
acc_sum = 0
for i, valid_vzor in enumerate(test_set):
    net_out = net.calc_out(valid_vzor[0])
    if valid_vzor[1][0] == int(round(net_out[0])):
        acc_sum += 1
        
        
print "Network accuracy on train set: {0:.3f}".format(float(acc_sum)/len(test_set))

acc = float(acc_sum)/len(test_set)

error_plot.save_plot(acc)

export = raw_input("Export_network?(y/n)\n")
if export == 'y':
    net.export_network()