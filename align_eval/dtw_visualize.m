function [ output_args ] = dtw_visualize(ix, iy, gt_x, gt_y, savefile)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
%% plot index of alignment
plot(ix, iy, '-o', 'DisplayName','alignment');
ylim([1, length(iy)]);
hold on;

%% plot groundtruth index
plot(gt_x, gt_y, '*', 'DisplayName','groundtruth');
hold off;
legend('show')

%% saving plot
print(savefile,'-dpng');

end

