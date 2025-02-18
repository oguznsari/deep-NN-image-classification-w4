import time
import numpy as np
import h5py
import matplotlib.pyplot as plt
import scipy
import cv2
from PIL import Image
from scipy import ndimage
from dnn_app_utils_v3 import *

# matplot inline
plt.rcParams["figure.figsize"] = (5.0, 4.0)             # set default size of plots
plt.rcParams["image.interpolation"] = "nearest"
plt.rcParams["image.cmap"] = "gray"

# load_ext autoreload
# autoreload 2

np.random.seed(1)


train_x_orig, train_y, test_x_orig, test_y, classes = load_data()

index = 36
plt.imshow(train_x_orig[index])
plt.show()
print("y = " + str(train_y[0, index]) + ". It's a " + classes[train_y[0, index]].decode("utf-8") + "picture.")


# Explore your dataset
m_train = train_x_orig.shape[0]
num_px = train_x_orig.shape[1]
m_test = test_x_orig.shape[0]

print("Number of training examples: " + str(m_train))
print("Number of test examples: " + str(m_test))
print("Each image is of size: (" + str(num_px) + ", " + str(num_px) + ", 3)" )
print("train_x_orig shape: " + str(train_x_orig.shape))
print("train_y shape: " + str(train_y.shape))
print("test_x_orig shape: " + str(test_x_orig.shape))
print("test_y shape: " + str(test_y.shape))


# Reshape the training and test examples
train_x_flatten = train_x_orig.reshape(train_x_orig.shape[0], -1).T     # The "-1" makes reshape flatten the remaining dimensions
test_x_flatten = test_x_orig.reshape(test_x_orig.shape[0], -1).T
train_x = train_x_flatten / 255
test_x = test_x_flatten / 255

print("train_x's shape: " + str(train_x.shape))
print("test_x's shape: " + str(test_x.shape))


# Constants defining the parameters
n_x = train_x.shape[0]
n_h = 7
n_y = 1
layer_dims = (n_x, n_h, n_y)


# GRADED FUNCTION: two_layer_model
def two_layer_model(X, Y, layer_dims, learning_rate = 0.0075, num_iterations = 3000, print_cost = False):
    """
    Implements a two-layer neural network: LINEAR -> RELU -> LINEAR -> SIGMOID

    Arguments:
        X -- input data, of shape (n_x, number of examples)
        Y -- true "label" vector (containing 1 if cat, 0 if non-cat), of shape (1, number of examples)
        layer_dims -- dimensions of the layers (n_x, n_h, n_y)
        num_iterations -- number of iterations of the optimization loop
        learning_rate -- learning rate of the gradient descent update rule
        print_cost -- If set to True, this will print cost every 100 iterations

    Returns:
        parameters -- a dictionary containing W1, W2, b1 and b2
    """

    np.random.seed(1)
    grads = {}
    costs = []                      # to keep track of the cost
    m = X.shape[1]                  # number of examples
    (n_x, n_h, n_y) = layer_dims

    # Initialize parameters dictionary, by calling one of the functions you'd previously implemented
    parameters = initialize_parameters(n_x, n_h, n_y)
    # Get W1, b1, W2 and b2 from the dictionary parameters.
    W1 = parameters["W1"]
    b1 = parameters["b1"]
    W2 = parameters["W2"]
    b2 = parameters["b2"]

    # Loop (gradient descent)
    for i in range(0, num_iterations):
        # Forward propagation: LINEAR -> RELU -> LINEAR -> SIGMOID. Inputs: "X, W1, b1, W2, b2". Output: "A1, cache1, A2, cache2"
        A1, cache1 = linear_activation_forward(X, W1, b1, 'relu')
        A2, cache2 = linear_activation_forward(A1, W2, b2, 'sigmoid')

        # Compute cost
        cost = compute_cost(A2, Y)

        # Initializing backward propagation
        dA2 = - (np.divide(Y, A2) - np.divide(1-Y, 1-A2))                   # WHY ????

        # Backward propagation. Inputs: "dA2, cache2, cache1". Outputs: "dA1, dW2, db2; Also dA0 (not used), dW1, db1".
        dA1, dW2, db2 = linear_activation_backward(dA2, cache2, 'sigmoid')
        dA0, dW1, db1 = linear_activation_backward(dA1, cache1, 'relu')

        # Set grads['dW1'] to dW1, grads['db1'] to db1, grads['dW2'] to dW2, grads['db2'] to db2
        grads["dW1"] = dW1
        grads["db1"] = db1
        grads["dW2"] = dW2
        grads["db2"] = db2

        # Update parameters.
        parameters = update_parameters(parameters, grads, learning_rate)

        # Retrieve W1, b1, W2, b2 from parameters
        W1 = parameters["W1"]
        b1 = parameters["b1"]
        W2 = parameters["W2"]
        b2 = parameters["b2"]

        # Print the cost every 100 training example
        if print_cost and i % 100 == 0:
            print("Cost after iteration {}: {}".format(i, np.squeeze(cost)))
        if print_cost and i % 100 == 0:
            costs.append(cost)

    plt.plot(np.squeeze(costs))
    plt.ylabel("cost")
    plt.xlabel("iterations (per hundred)")
    plt.title("Learning rate =" + str(learning_rate))
    plt.show()

    return parameters

parameters = two_layer_model(train_x, train_y, layer_dims = (n_x, n_h, n_y), num_iterations = 2500, print_cost = True)
# Good thing you built a vectorized implementation! Otherwise it might have taken 10 times longer to train this.
predictions_train = predict(train_x, train_y, parameters)
predictions_test = predict(test_x, test_x, parameters)




### CONSTANTS ###
layers_dims = [12288, 20, 7, 5, 1]                       # 4-Layer model
# GRADED FUNCTION: L_layer_model
def L_layer_model(X, Y, layer_dims, learning_rate = 0.0075, num_iterations = 3000, print_cost = False):     # lr was 0.009
    """
    Implements a L-layer neural network: [LINEAR -> RELU]*(L-1) -> LINEAR -> SIGMOID

    Arguments:
        X -- data, numpy array of shape (num_px * num_px * 3, number of examples)
        Y -- true "label" vector (containing 0 if cat, 1 if non-cat), of size (1, number of examples)
        layer_dims -- list containing the input size and each layer size, of length (number of layers + 1)
        learning_rate -- learning rate of the gradient descent update rule
        num_iterations -- number of iterations of the optimization loop
        print_cost -- if True, it prints the cost every 100 steps

    Returns:
        parameters -- parameters learnt by the model. They can then be used to predict.
    """
    np.random.seed(1)
    costs = []                              # keep track of the cost

    # Parameters initialization
    parameters = initialize_parameters_deep(layer_dims)

    # Loop (gradient descent)
    for i in range(0, num_iterations):
        # Forward propagation: [LINEAR -> RELU]*(L-1) -> LINEAR -> SIGMOID.
        AL, caches = L_model_forward(X, parameters)

        # Compute cost
        cost = compute_cost(AL, Y)

        # Backward propagation
        grads = L_model_backward(AL, Y, caches)

        # Update parameters
        parameters = update_parameters(parameters, grads, learning_rate)

        # Print the cost every 100 training example
        if print_cost and i % 100 == 0:
            print("Cost after iteration %i: %f" %(i, cost))
        if print_cost and i % 100 == 0:
            costs.append(cost)

    # Plot the cost
    plt.plot(np.squeeze(costs))
    plt.ylabel("cost")
    plt.xlabel("iterations (per hundreds)")
    plt.title("Learning rate =" + str(learning_rate))
    plt.show()

    return parameters

parameters = L_layer_model(train_x, train_y, layers_dims, num_iterations = 2500, print_cost = True)
pred_train = predict(train_x, train_y, parameters)
pred_test = predict(test_x, test_y, parameters)

# Congrats! 4-Layer network has better performance (80%) than 2-layer neural network (72%) on the same test set.
# In the next course "improving deep neural networks" we will learn how to obtain even higher accuracy
# by systematically searching for better hyperparameters (learning_rate, num_iterations, and others we'll also learn in the next course


### RESULT ANALYSIS ###
# let's take a look at some images the L-layer model labeled incorrectly.
print_mislabeled_images(classes, test_x, test_y, pred_test)
# A few types of images the model tends to do poorly on include:
# - Cat body in an unusual position
# - Cat appears against a background of a similar color
# - Unusual cat color and species
# - Camera Angle
# - Brightness of the picture
# - Scale variation (cat is very large or small in image)

### Test with your own image ###
my_image = "headshot.jpg"
my_label_y = [0]            # the true class of our image (cat -> 1, non-cat ->0)

fname = "images/" + my_image
image = np.array(plt.imread(fname))
my_image = cv2.resize(image, (64, 64))
my_image = my_image.reshape(1, num_px * num_px * 3).T
my_image = my_image / 255
my_predicted_image = predict(my_image, my_label_y, parameters)


print("y = " + str(np.squeeze(my_predicted_image)) + ", your L-layer model predicts a \"" + classes[int(np.squeeze(my_predicted_image)),].decode("utf-8") + "\" picture.")
plt.imshow(image)
plt.show()