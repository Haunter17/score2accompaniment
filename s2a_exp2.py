import numpy as np
import tensorflow as tf
import matplotlib
import h5py
import time
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import scipy.io

def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1, dtype=tf.float32)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape, dtype=tf.float32)
  return tf.Variable(initial)

def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='VALID')

def max_pool_2x2(x):
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding='SAME')

# reading data
print("Score2Accompaniment - EXP2 (Velocity)")
filepath = 'Duration=0_Velocity=1_Data_25x49_DS=10'
z = scipy.io.loadmat(filepath)
X_train = scipy.sparse.csc_matrix.todense(z['X_train'])
y_train = z['y_train'][:,1] #velocity
X_val = scipy.sparse.csc_matrix.todense(z['X_val'])
y_val = z['y_val'][:,1] #velocity
del z

# Set data type
X_train = np.asfarray(X_train, dtype='float32')
X_val = np.asfarray(X_val, dtype='float32')
y_train = np.asfarray(np.reshape(y_train,(-1,1)), dtype='float32')
y_val = np.asfarray(np.reshape(y_val,(-1,1)), dtype='float32')
print(X_train.shape, y_train.shape, X_val.shape, y_val.shape)

# Shuffle data (concatenate sample with label before shuffling)
allTrain = np.concatenate((X_train, y_train), axis=1)
allVal = np.concatenate((X_val, y_val), axis=1)
np.random.shuffle(allTrain)
np.random.shuffle(allVal)
print(allTrain.shape, allVal.shape)

# Separate samples from labels again
X_train = allTrain[:, :-1]
y_train = np.reshape(allTrain[:,-1], (-1,1))
X_val = allVal[:,:-1]
y_val = np.reshape(allVal[:,-1], (-1,1))

# Neural-network model set-up
numPitches = 25
numTimeFrames = 49
numFeatures = numPitches * numTimeFrames
numClass = 1
k1 = 32
k2 = 64
fc_size = 1024

sess = tf.InteractiveSession()

x = tf.placeholder(tf.float32, shape=[None, numFeatures])
y_ = tf.placeholder(tf.float32, shape=[None, numClass])

W_conv1 = weight_variable([6, 6, 1, k1])
b_conv1 = bias_variable([k1])
x_image = tf.reshape(x, [-1, numPitches, numTimeFrames,1])

h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
h_pool1 = max_pool_2x2(h_conv1)

W_conv2 = weight_variable([3, 3, k1, k2])
b_conv2 = bias_variable([k2])

h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)

h_pool2 = max_pool_2x2(h_conv2)

W_fc1 = weight_variable([4*10*k2, fc_size])
b_fc1 = bias_variable([fc_size])

h_pool2_flat = tf.reshape(h_pool2, [-1, 4*10*k2])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

keep_prob = tf.placeholder(tf.float32)
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

W_fc2 = weight_variable([fc_size, 1])
b_fc2 = bias_variable([1])

y_conv = tf.matmul(h_fc1_drop, W_fc2) + b_fc2

tolerance = tf.placeholder(tf.float32)

mse = tf.reduce_mean(tf.losses.mean_squared_error(labels=y_, predictions=y_conv))
train_step = tf.train.AdamOptimizer(learning_rate=0.001).minimize(mse)
correct_prediction = tf.less(tf.abs(y_conv-y_), tolerance)
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

sess.run(tf.global_variables_initializer())

train_err_list = []
val_err_list = []
plotx = []

batch_size = 1000
numEpochs = 100
printfreq = 2
num_training_vec = X_train.shape[0]

# Use only a subset of validation samples for speed
X_val_batch = X_val[:20000]
y_val_batch = y_val[:20000]

for epoch in range(numEpochs):
    for i in range(0,num_training_vec, batch_size):
      batch_end_point = min(i + batch_size, num_training_vec)
      train_batch_data = X_train[i : batch_end_point]
      train_batch_label = y_train[i : batch_end_point]
      train_step.run(feed_dict={x: train_batch_data, y_: train_batch_label, keep_prob: 0.5})

    if (epoch+1)%printfreq == 0:
      plotx.append(epoch)
      val_err = mse.eval(feed_dict={x:X_val_batch, y_:y_val_batch, keep_prob: 1.0})   
      train_err = mse.eval(feed_dict={x:train_batch_data, y_: train_batch_label, keep_prob: 1.0})
      train_err_list.append(train_err)
      val_err_list.append(val_err)
      print("step %d, t err %g, v err %g"%(epoch, train_err, val_err))

# Compute error per tolerance for the final model
tolerance_list = []
for tol in range(0, 40, 2):
  # tol is in milliseconds
  cur_tolerance = accuracy.eval(feed_dict={x:X_val_batch, y_: y_val_batch, keep_prob: 1.0, tolerance: tol})
  tolerance_list.append((1-cur_tolerance)*100)

# Reports
print('-- Training error: {:.4E}'.format(train_err_list[-1]))
print('-- Validation error: {:.4E}'.format(val_err_list[-1]))

print('==> Generating error plot...')
errfig = plt.figure()
trainErr = errfig.add_subplot(111)
trainErr.set_xlabel('Number of epochs')
trainErr.set_ylabel('Mean-Squared Error')
trainErr.set_title('Error vs Number of Epochs')
trainErr.scatter(plotx, train_err_list)
valErr = errfig.add_subplot(111)
valErr.scatter(plotx, val_err_list, c='r')
errfig.savefig('s2a_velocity_modelError.png')

print('==> Generating tolerance plot...')
errfig = plt.figure()
plotx = range(0, 40, 2)
plot_tolerance = errfig.add_subplot(111)
plot_tolerance.set_xlabel('Velocity Tolerance')
plot_tolerance.set_ylabel('Error (%)')
plot_tolerance.set_title('Error vs Tolerance')
plot_tolerance.scatter(plotx, tolerance_list)
errfig.savefig('s2a_velocity_toleranceError.png')
print('==> Done.')