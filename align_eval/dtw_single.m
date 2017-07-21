function [ix, iy] = dtw_single(chroma_x, chroma_y, param)
% arguments:
	%			signal_x: signal x to be aligned
  	%			signal_y: signal y to be aligned  
    %           savefile: path to save the plots
    %           downsampling: the rate of downsampling
    
addpath('../DTW_MIRLab/');
if nargin < 6
    fs = 22050;
end
if nargin < 7
    param = {};
end

%% DTW calculation
C = 1. - chroma_x' * chroma_y;

[accumCost, bestCost, steps, offset] = DTW_New_costMatrix(C, parameter.dn, parameter.dm, parameter.dw, false);
dtwPath = DTW_backtrace(steps, parameter.dn, parameter.dm, offset);

ix = WP(1, :);
iy = WP(2, :);

end

