import pickle
import numpy as np




if __name__ == '__main__':
    network_input_file = "./../Dataset/NN_input.txt"

    file = open(network_input_file,'rb')
    object_file = np.array(pickle.load(file))
    file.close()
    print(object_file)