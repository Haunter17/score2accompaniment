function x = MakeToleranceGraph(dist, fs, fftlen)
	% arguments:
	%			dist: a list of distance
	%			fs: optional param, the sampling rate
    %           fftlen: length of FFT used for computing chroma features

    if nargin < 2
        fs = 22050;
    end
    
    if nargin < 3
        fftlen = 880;
    end
    
    %% converting frame distance to time offset (ms)
    fac = fs / fftlen * 4;
    dist = abs(dist) / fac * 1000;
    
	fprintf('==> Beginning Calculations for the tolerance graph\n');
	tolerances = 100 : 100 : 1000; % tolerance in steps - 1 second max tolerance
	percentError = zeros(1, length(tolerances));

	for index = 1:length(tolerances)
		% find the number out of tolerance
		tol = tolerances(index);
		fprintf('Evaluating with tolerance: %g \n', tol);
		count = sum(dist > tol);
		% percent error is the number out of tolerance over the number of beats
		percentError(index) = count / length(dist);
		fprintf('Percent error is: %f\n', percentError(index));
	end

	fprintf('==> Plotting\n');
	% scale up the tolerances to time using fs
	plot(tolerances, percentError);

	xlabel('Tolerance (s)');
	ylabel('Percent Error');
	title('Percent Error (DTW predicted beat in second track vs. ground truth beat in second track) vs. Tolerance');

end