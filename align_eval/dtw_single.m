function [ix, iy] = dtw_single(chroma_x, chroma_y, param)
% arguments:
	%			signal_x: signal x to be aligned
  	%			signal_y: signal y to be aligned  
    %           savefile: path to save the plots
    %           downsampling: the rate of downsampling
    
addpath('../DTW_AudioLabs/');
if nargin < 6
    fs = 22050;
end
if nargin < 7
    param = {};
end

%% DTW calculation
C = 1. - chroma_x' * chroma_y;
[~, E] = TH_DTW_C_to_DE(C, param);
WP = TH_DTW_E_to_Warpingpath(E, param);
ix = WP(1, :);
iy = WP(2, :);

end

