function [ agg_dist ] = dtw_batch(filelist, chroma_midi, annot_midi,...
    fftlen, outdir, param )
%   dtw_batch
%
if nargin < 5
    param = {};
end
addpath('./chroma-ansyn/');

fid = fopen(filelist);
fileNameList = '';
fileIndex = 1;
curfile = fgetl(fid);
while ischar(curfile)
    fileNameList{fileIndex} = curfile;
    curfile = fgetl(fid);
    fileIndex = fileIndex + 1;
end
fclose(fid);

agg_dist = cell(1, fileIndex);

parfor index = 1:length(fileNameList)
    fileName = fileNameList{index};
    [pathstr,name,ext] = fileparts(fileName);
    disp(['==> Generating alignment on ',name]);
    wavfile = strcat(fileName, '.wav');
    %% compute chroma
    [signal_perf, fs] = audioread(wavfile);
    disp(['-- Calculating chroma features of ', name]);
    tic;
    chroma_perf = chromagram_IF(signal_perf, fs, fftlen);
    chroma_perf = normc(chroma_perf);
    toc
    %% DTW
    disp(['-- DTW alignment on ', name]);
    tic;
    [align_x, align_y] = dtw_single(chroma_midi, chroma_perf, param);
    toc
    %% visualize
    annotfile = strcat(fileName, '.csv');
    annot_perf = csvread(annotfile);
    annot_perf = annot_perf(:, 1);
    adj_x = double(align_x) * (fftlen / 4) / fs;
    adj_y = double(align_y) * (fftlen / 4) / fs;
    gt_midi = annot_midi;
    gt_perf = annot_perf;
    savefile = strcat(outdir, name);
    dtw_visualize(adj_x, adj_y, gt_midi, gt_perf, savefile);
    %% aggregate distance
    agg_dist{index} = calculate_offset(adj_x, adj_y, gt_midi, gt_perf);
    mean(agg_dist{index})
end
agg_dist = cell2mat(agg_dist);
end

