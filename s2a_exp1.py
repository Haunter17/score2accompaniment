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
print("Score2Accompaniment - EXP1 (Duration)")
filepath = '/pylon2/ci560sp/mint96/Duration=1_Data_25x49_DS=10.mat'
#filepath = 'Duration=1_Data_25x49_DS=10.mat'
z = scipy.io.loadmat(filepath)
X_train = scipy.sparse.csc_matrix.todense(z['X_train'])
y_train = z['y_train'][:,0]
X_val = scipy.sparse.csc_matrix.todense(z['X_val'])
y_val = z['y_val'][:,0]
del z

X_train = np.asfarray(X_train, dtype='float32')
X_val = np.asfarray(X_val, dtype='float32')
y_train = np.asfarray(np.reshape(y_train,(-1,1)), dtype='float32')
y_val = np.asfarray(np.reshape(y_val,(-1,1)), dtype='float32')
print(X_train.shape, y_train.shape, X_val.shape, y_val.shape)

# Neural-network model set-up
numPitches = 25
numTimeFrames = 49
numFeatures = numPitches * numTimeFrames
numClass = 1
k1 = 32
k2 = 64
fc_size = 256

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
train_step = tf.train.AdamOptimizer(1e-4).minimize(mse)
correct_prediction = tf.less(tf.abs(y_conv-y_)*1000, tolerance)
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

sess.run(tf.global_variables_initializer())

train_err_list = []
val_err_list = []
plotx = []

batch_size = 500
numEpochs = 100
printfreq = 2
num_training_vec = X_train.shape[0]

for epoch in range(numEpochs):
    for i in range(0,num_training_vec, batch_size):
      batch_end_point = min(i + batch_size, num_training_vec)
      train_batch_data = X_train[i : batch_end_point]
      train_batch_label = y_train[i : batch_end_point]
      train_step.run(feed_dict={x: train_batch_data, y_: train_batch_label, keep_prob: 0.5})

    if (epoch+1)%printfreq == 0:
      plotx.append(epoch)
      val_err = cross_entropy.eval(feed_dict={x:X_val, y_:y_val})   
      train_err = cross_entropy.eval(feed_dict={x:X_train, y_: y_train})
      train_err_list.append(train_err)
      val_err_list.append(val_err)
      print("step %d, t err %g, v err %g"%(epoch, train_err, val_err))

tolerance_list = []
for tol in range(0, 1000, 10):
  # tol is in milliseconds
  cur_tolerance = accuracy.eval(feed_dict={x:X_val, y_: y_val, tolerance: tol})
  tolerance_list.append((1-cur_tolerance)*100)

# Reports
print('-- Training error: {:.4E}'.format(train_err_list[-1]))
print('-- Validation error: {:.4E}'.format(val_err_list[-1]))

print('==> Generating error plot...')
errfig = plt.figure()
trainErr = errfig.add_subplot(111)
trainErr.set_xlabel('Number of epochs')
trainErr.set_ylabel('Cross-Entropy Error')
trainErr.set_title('Error vs Number of Epochs')
trainErr.scatter(plotx, train_err_list)
valErr = errfig.add_subplot(111)
valErr.scatter(plotx, val_err_list, c='r')
errfig.savefig('score2accompaniment_modelError.png')

errfig = plt.figure()
plotx = range(0, 1000, 10)
plot_tolerance = errfig.add_subplot(111)
plot_tolerance.set_xlabel('Tolerance (ms)')
plot_tolerance.set_ylabel('Error (%)')
plot_tolerance.set_title('Error vs Tolerance')
plot_tolerance.scatter(plotx, tolerance_list)
errfig.savefig('score2accompaniment_toleranceError.png')
print('==> Done.')
