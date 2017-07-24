function MakeToleranceGraph(dist, savefile)
	% arguments:
	%			dist: a list of distance
    
	fprintf('==> Beginning Calculations for the tolerance graph\n');
	tolerances = 100 : 500 : 5000; % tolerance in steps - 1 second max tolerance
	percentError = zeros(1, length(tolerances));

	for index = 1:length(tolerances)
		% find the number out of tolerance
		tol = tolerances(index);
		fprintf('Evaluating with tolerance: %g ms\n', tol);
		count = sum(dist > tol);
		% percent error is the number out of tolerance over the number of beats
		percentError(index) = count / length(dist);
		fprintf('Percent error is: %f\n', percentError(index));
	end

	fprintf('==> Plotting\n');
	% scale up the tolerances to time using fs
	plot(tolerances, percentError);

	xlabel('Tolerance (ms)');
	ylabel('Percent Error');
	title('Percent Error (DTW predicted beat in second track vs. ground truth beat in second track) vs. Tolerance');
    %% saving plot
    print(savefile,'-dpng');
end