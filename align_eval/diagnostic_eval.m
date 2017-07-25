addpath('./chroma-ansyn/');
addpath('../DTW_MIRLab/');
%% setting params for chroma feature and DTW
fftlen = 880; % tweak this
param.dn = int32([1 1 0]);
param.dm = int32([1 0 1]);
param.dw = int32([1 1 2]);
param.subseq = false;

file1 = './data/p1a_midi';
file2 = './data/p1f_perf2';
file3 = './data/p1f_perf6';

%% generate chroma
[sig1, ~] = audioread(strcat(file1, '.wav'));
[sig2, ~] = audioread(strcat(file2, '.wav'));
[sig3, fs] = audioread(strcat(file3, '.wav'));
disp('==> Computing chroma 1...');
chroma1 = normc(chromagram_IF(sig1, fs, fftlen));
disp('==> Computing chroma 2...');
chroma2 = normc(chromagram_IF(sig2, fs, fftlen));
disp('==> Computing chroma 3...');
chroma3 = normc(chromagram_IF(sig3, fs, fftlen));

%% DTW
disp('==> DTW between chroma 1 and chroma 3...');
C = 1. - chroma3' * chroma1;
[accumCost, bestCost, steps, offset] = ...
    DTW_New_costMatrix(C, param.dn, param.dm, param.dw, param.subseq);
WP = DTW_backtrace(steps, param.dn, param.dm, offset);
ix = WP(2, :);
iy = WP(1, :);
adj_x = double(ix) * (fftlen / 4) / fs;
adj_y = double(iy) * (fftlen / 4) / fs;
gt_x = csvread(strcat(file1, '.csv'));
gt_x = gt_x(:, 1);
gt_y = csvread(strcat(file3, '.csv'));
gt_y = gt_y(:, 1);
% dtw_visualize(adj_x, adj_y, gt_x, gt_y, './out/dtw_1v3');
dist1 = calculate_offset(adj_x, adj_y, gt_x, gt_y);
MakeToleranceGraph(abs(dist1) * 1000, './out/tol_1');

disp('==> DTW between chroma 2 and chroma 3...');
C = 1. - chroma3' * chroma2;
[accumCost, bestCost, steps, offset] = ...
    DTW_New_costMatrix(C, param.dn, param.dm, param.dw, param.subseq);
WP = DTW_backtrace(steps, param.dn, param.dm, offset);
ix = WP(2, :);
iy = WP(1, :);
adj_x = double(ix) * (fftlen / 4) / fs;
adj_y = double(iy) * (fftlen / 4) / fs;
gt_x = csvread(strcat(file2, '.csv'));
gt_x = gt_x(:, 1);
% dtw_visualize(adj_x, adj_y, gt_x, gt_y, './out/dtw_2v3');
dist2 = calculate_offset(adj_x, adj_y, gt_x, gt_y);
MakeToleranceGraph(abs(dist2) * 1000, './out/tol_2');
