from mido import MidiFile
import os

filename = 'e-competition_out/2002/chan01.mid'
mid = MidiFile(filename)

directories = ['e-competition_out/2002/', 'e-competition_out/2004/', 'e-competition_out/2006/', 'e-competition_out/2008/', 'e-competition_out/2009/', 'e-competition_out/2011/']
#directories = ['e-competition_out/2011/']

notesOnPerDirectory = [0] * len(directories)

totalFiles = 0

for directoryIndex in range(len(directories)):
	directory = directories[directoryIndex]
	print('==> Analyzing directory %s'%(directory))
	# grab the files, assume they're all midi
	numNotesOnInDirectory = 0
	files = os.listdir(directory)
	for i in range(len(files)):
		if files[i] != '.DS_Store':
			totalFiles = totalFiles + 1
			print('Processing file %g out of %g in directory: %s'%(i, len(files), files[i]))
			mid = MidiFile(directory + files[i])
			curNumNotesOn = 0
			for msg in mid:
				if (msg.type == 'note_on'):
					curNumNotesOn = curNumNotesOn + 1
			print('%g Notes on in %s'%(curNumNotesOn, files[i]))
			numNotesOnInDirectory = numNotesOnInDirectory + curNumNotesOn
		else:
			print('A .DS Store =(((((((( !!!!!!!!!!!!!!')
	print('==> Directory: %s had %g notes on, average of %f per song'%(directory, numNotesOnInDirectory, float(numNotesOnInDirectory) / len(files)))
	notesOnPerDirectory[directoryIndex] = numNotesOnInDirectory

print("==> Total Notes On: %g for %g files, avg: %f notes per song"%(sum(notesOnPerDirectory), totalFiles, float(sum(notesOnPerDirectory))/totalFiles))
print("Notes per directory: %s"%(str(notesOnPerDirectory)))
print("directories: %s"%(str(directories)))