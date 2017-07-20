function x = MakeToleranceGraph(beatX, beatY, alignmentX, alignmentY, fs)
	% arguments:
	%			beatX: a list of the indices in the alignment for the beats in the first piece
	%			beatY: a list of the indices in the alignment for the beats in the second piece
	%					beatX and beatY should be the same length, since the pieces should be of the same song
	%			alignmentX: indices of the first piece that make up the alignment
	% 			alingmentY: inices of the second piece that make up the alignment
	% 					pieceOne(alignmentX(i)) is aligned with pieceTwo(alignmentY(i)) via DTW
	%			fs: optional param, the sampling rate



	if nargin < 5
		fs = 22050;
	end

	fprintf('==> Beginning Calculations for the tolerance graph\n');

	tolerances = 1:fs/50; % tolerance in steps - 1 second max tolerance
	percentError = zeros(1, length(tolerances));

	% pull out the values of the alignment at each beat from the first track, and
	% find how far from the actual beat for the second track is
	relevantAlignmentYs = alignmentY(beatX);
	dists = abs(beatY - relevantAlignmentYs)
	for toleranceIndex = 1:length(tolerances)
		% find the number out of tolerance
		tolerance = tolerances(toleranceIndex);
		fprintf('Evaluating with tolerance: %g out of %g\n', tolerance, max(tolerances));
		numOutOfTolerance = sum(dists > tolerance);
		% percent error is the number out of tolerance over the number of beats
		percentError(toleranceIndex) = numOutOfTolerance / length(beatX);
		fprintf('Percent error is: %f\n', percentError(toleranceIndex));
	end

	fprintf('==> Plotting\n');
	% scale up the tolerances to time using fs
	toleranceInTime = tolerances * (1/fs);
	plot(toleranceInTime, percentError);

	xlabel('Tolerance (s)');
	ylabel('Percent Error');
	title('Percent Error (DTW predicted beat in second track vs. ground truth beat in second track) vs. Tolerance');

	% for toleranceIndex = 1:length(tolerances)
	% 	% for each tolerance, go through every beat and see how many are out of range
	% 	tolerance = tolerances(toleranceIndex);
	% 	fprintf('Evaluating with tolerance: %g out of %g\n', tolerance, max(tolerances));
	% 	numOutOfTolerance = 0;
	% 	for beatIndex = 1:length(beatX)
	% 		% a beat is out of range if the beat y is too far from the corresponding alignment y
	% 		curX = beatX(beatIndex);
	% 		dist = abs(beatY(beatIndex) - alignmentY(curX));
	% 		fprintf('Dist is: %f\n', dist);
	% 		if dist > tolerance
	% 			++numOutOfTolerance;
	% 		end
	% 	end
	% 	% percent error is the number out of tolerance over the number of beats
	% 	percentError(toleranceIndex) = numOutOfTolerance / length(beatX);
	% 	fprintf('Percent error is: %f\n', percentError(toleranceIndex));
	% end
end