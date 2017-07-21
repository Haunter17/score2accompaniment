function [dist, ix, iy] = dtw_single(signal_x, signal_y, annot_x, annot_y,...
    savefile, downsampling, fs)
% arguments:
	%			signal_x: signal x to be aligned
  	%			signal_y: signal y to be aligned  
    %           annot_x: annotation time stamps for signal x (in sec)
    %           annot_y: annotation time stamps for signal y (in sec)
    %           savefile: path to save the plots
    %           downsampling: the rate of downsampling
	%			fs: optional param, the sampling rate
if nargin < 6
    fs = 22050;
end
fs = round(fs / downsampling);
signal_x = signal_x(1 : downsampling : end);
signal_y = signal_y(1 : downsampling : end);

[dist, ix, iy] = dtw(signal_x, signal_y);
plot(ix, iy, '-o', 'DisplayName','alignment');
ylim([1, length(iy)]);
hold on;
ind_annot_x = fs * annot_x;
ind_annot_y = fs * annot_y;
plot(ind_annot_x, ind_annot_y, '*', 'DisplayName','groundtruth');
hold off;
legend('show')
print(savefile,'-dpng');

end

