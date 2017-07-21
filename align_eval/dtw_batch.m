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

for index = 1:length(fileNameList)
    fileName = fileNameList{index};
    [pathstr,name,ext] = fileparts(fileName);
    disp(['==> Generating alignment on ',name]);
    wavfile = strcat(fileName, '.wav');
    %% compute chroma
    [signal_perf, fs] = audioread(wavfile);
    chroma_perf = chromagram_IF(signal_perf, fs, fftlen);
    %% DTW
    [align_x, align_y] = dtw_single(chroma_midi, chroma_perf, param);
    %% visualize
    annotfile = strcat(fileName, '.csv');
    annot_perf = csvread(annotfile);
    annot_perf = annot_perf(:, 1);
    gt_midi = annot_midi * fs / fftlen * 4;
    gt_perf = annot_perf * fs / fftlen * 4;
    savefile = strcat(outdir, name);
    dtw_visualize(align_x, align_y, gt_midi, gt_perf, savefile);
    %% aggregate distance
    agg_dist{index} = calculate_offset(align_x, align_y, gt_midi, gt_perf);
end
agg_dist = cell2mat(agg_dist);
end

