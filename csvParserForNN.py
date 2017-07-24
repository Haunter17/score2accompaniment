import csv
import numpy as np
import os
import scipy.io as sp
import random
# build a 3-d matrix with dim: pitch x song_length (in the chunks we're using) x 2
# the first dimension corresponds to dif notes, the second to time, the third will allow
# us to hold both velocity and duration - with 0 being duration, 1 being velocity

directory = './Processed_MIDI/'
filenames = os.listdir(directory)
random.shuffle(filenames)
# find how many to keep in your training set
numInTraining = 1267
downsamplingRate = 10

# set the shape of your window
timePerQuery = 3.0
timeChunksPerQuery = 49
timePerChunk = timePerQuery / timeChunksPerQuery
numPitches = 128
numPitchesInQuery = 25
# choose to create the duration dataset
getDuration = True # choose whether to get the duration or velocity
savefilename = 'Duration=%g_Data_%gx%g.mat'%(getDuration, numPitchesInQuery, timeChunksPerQuery)

# find how many notes you'll have, so that you can 
# initialize the matrices that will hold your data (speeds things up to pre-initialize)
numNotesTraining = 0
numNotesValidation = 0
for i in range(len(filenames)):
	with open(directory + filenames[i], 'rb') as csvfile:
		print("==> Reading File: %s to find numNotes"%(filenames[i]))
		myReader = csv.reader(csvfile)
		if i < numInTraining: 
			numNotesTraining = numNotesTraining + sum(1 for row in myReader)
		else:
			numNotesValidation = numNotesValidation + sum(1 for row in myReader)

print("There should be %g and %g train and validation notes"%(numNotesTraining, numNotesValidation))

# initialize the matrices that will hold your samples
trainSamples = np.empty((numNotesTraining, numPitchesInQuery * timeChunksPerQuery - 1))
trainLabels = np.empty((numNotesTraining,2))
valSamples = np.empty((numNotesValidation, numPitchesInQuery * timeChunksPerQuery - 1))
valLabels = np.empty((numNotesValidation,2))

trainNotesAdded = 0
valNotesAdded = 0

# loop through each file, and add a row for each note into either the training
# or validation data matrix
fileIndex = 0
for curFile in filenames:
	with open(directory + curFile, 'rb') as csvfile:
		print("==> Reading File: %s, %g out of %g, %f%%"%(curFile, fileIndex, len(filenames), 100 * float(fileIndex) / len(filenames)))
		myReader = csv.reader(csvfile)
		maxTime = max([float(row[1]) for row in myReader])
		# reset the reader
		csvfile.seek(0)

		# open it again to actually parse it, now that you know how big your matrix should be
		# will this account for the edge case where top and bottom both are in a query?
		pitchPadding = int(np.floor(numPitchesInQuery / 2.))
		timePadding = int(np.floor(timeChunksPerQuery / 2.))
		curMatrix = np.zeros((numPitches + 2 * pitchPadding, int(np.ceil(maxTime / timePerChunk)) + 2 * timePadding, 2))
		
		# read each row and add into the matrix that represents the song
		numNotes = 0
		for row in myReader:
			numNotes = numNotes + 1
			[note, curTime, velocity, duration] = [int(row[0]), float(row[1]), int(row[2]), float(row[3])]
			curMatrix[note + pitchPadding, int(np.floor(curTime / timePerChunk)) + timePadding, :] = [duration, velocity]	

	# your matrix now exists! now parse through each note by finding the indices of non-zero entries
	(nonZeroPitch, nonZeroTime) = np.nonzero(curMatrix[:,:,0]) # pull out only one layer so can avoid repeats
	
	# make space for a sample for each note
	sampleMatrix = np.zeros((numNotes, timeChunksPerQuery * numPitchesInQuery))
	labelMatrix = np.zeros((numNotes, 2)) # the duration and velocity labels
	# loop through each note
	for i in range(len(nonZeroPitch)):
		curPitch = nonZeroPitch[i]
		curTime = nonZeroTime[i]
		# save the labels
		labelMatrix[i, :] = curMatrix[curPitch, curTime, :]
		# grab the current context, then reshape into a row and save
		curContext = curMatrix[(curPitch - int(np.floor(numPitchesInQuery / 2.))):(curPitch + int(np.ceil(numPitchesInQuery / 2.))) , (curTime - int(np.floor(timeChunksPerQuery / 2.))):(curTime + int(np.ceil(timeChunksPerQuery / 2.))),:]
		# save the duration or velocity values
		if getDuration:
			# reshape the durations and add them into the sample matrix
			sampleMatrix[i,:] = np.reshape(curContext[:,:,0], (1, timeChunksPerQuery * numPitchesInQuery))
		else:
			# reshape it and add it into the sample matrix
			sampleMatrix[i,:] = np.reshape(curContext[:,:,1], (1, timeChunksPerQuery * numPitchesInQuery))

	# remove the column that represents the note we're centered on
	sampleMatrix = np.delete(sampleMatrix, timeChunksPerQuery * int(np.floor(numPitchesInQuery / 2.)) + int(np.floor(timeChunksPerQuery / 2.)), axis=1)
	if getDuration:
		sampleMatrix[np.nonzero(sampleMatrix)] = 1 # turn all non-zeros to 1s
		# map to ints to make smaller
		sampleMatrix = sampleMatrix.astype(int)
		print(type(sampleMatrix[0][0]))
	# insert the new data into the sample / label matrices
	# keep track of where you are in these matrices
	numToAdd = sampleMatrix.shape[0]
	if fileIndex < numInTraining:
		trainSamples[trainNotesAdded:(trainNotesAdded + numToAdd),:] = sampleMatrix
		trainLabels[trainNotesAdded:(trainNotesAdded + numToAdd), :] = labelMatrix
		trainNotesAdded = trainNotesAdded + numToAdd
	else:
		valSamples[valNotesAdded:(valNotesAdded + numToAdd), :] = sampleMatrix
		valLabels[valNotesAdded:(valNotesAdded + numToAdd), :] = labelMatrix
		valNotesAdded = valNotesAdded + numToAdd

	print("Train notes added: %g"%(trainNotesAdded))
	print("Val notes added: %g"%(valNotesAdded))

	# # append the new samples
	# print("here")
	# if fileIndex < numInTraining:
	# 	print("Adding to training set")
	# 	trainSamples = np.append(trainSamples, sampleMatrix, axis=0)
	# 	trainLabels = np.append(trainLabels, labelMatrix, axis=0)
	# else:
	# 	print("Adding to validation set")
	# 	valSamples = np.append(valSamples, sampleMatrix, axis=0)
	# 	valLabels = np.append(valLabels, labelMatrix, axis=0)	

	fileIndex = fileIndex + 1

# downsample
trainSamples = trainSamples[::downsamplingRate,:]
trainLabels = trainLabels[::downsamplingRate,:]
valSamples = valSamples[::downsamplingRate,:]
trainSamples = trainSamples[::downsamplingRate,:]

# save the data as a .mat file
sp.savemat({'X_train': trainSamples, 'y_train': trainLabels, 'X_val': valSamples, 'y_val': valLabels})







# # restart the reader
# myReader = csv.reader(csvfile)
# for row in myReader:
# 	[note, curTime, velocity, duration] = row
# 	# see if need to add on a column because of the time
# 	numColsNeeded = np.ceil(float(curTime) / timePerChunk)
# 	if curMatrix.shape[1] < numColsNeeded:
# 		newCols = np.zeros((numPitches, numColsNeeded - curMatrix.shape[1], 2))
# 		curMatrix = np.append(curMatrix, newCols, 1)