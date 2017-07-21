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
    param.dn = int32([1, 1, 0]);
    param.dm = int32([1, 0, 1]);
    param.dw = int32([1, 1, 1]);
end

%% DTW calculation
C = 1. - chroma_x' * chroma_y;

[accumCost, bestCost, steps, offset] = ...
    DTW_New_costMatrix(C, param.dn, param.dm, param.dw, false);
WP = DTW_backtrace(steps, param.dn, param.dm, offset);

ix = WP(1, :);
iy = WP(2, :);

end

