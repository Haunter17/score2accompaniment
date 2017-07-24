addpath('./chroma-ansyn/');

%% Parallel computing setup
curPool = gcp('nocreate'); 
if (isempty(curPool))
    myCluster = parcluster('local');
    numWorkers = myCluster.NumWorkers;
    % create a parallel pool with the number of workers in the cluster`
    pool = parpool(ceil(numWorkers * 0.75));
end

%% setting params for chroma feature and DTW
fftlen = 880; % tweak this
param.dn = int32([1 1 0]);
param.dm = int32([1 0 1]);
param.dw = int32([1 1 1]);
outdir = './data/';

%% reading midi list
midilist = strcat(outdir, 'midi.list');
fid = fopen(midilist);
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
    disp(['==> Processing ',name]);
    wavfile = strcat(fileName, 'a_midi.wav');
    [signal_midi, fs] = audioread(wavfile);
    chroma_midi = chromagram_IF(signal_midi, fs, fftlen);
    chroma_midi = normc(chroma_midi);
    annotfile = strcat(fileName, 'a_midi.csv');
    annot_midi = csvread(annotfile);
    annot_midi = annot_midi(:, 1);
    perflist = strcat(fileName, '.list');
    dist = dtw_batch(perflist, chroma_midi, annot_midi, ...
        fftlen, outdir, param);
    agg_dist{index} = dist;
end
agg_dist = cell2mat(agg_dist);
%% converting frame distance to time offset (ms)
fac = fs / fftlen * 4;
ms_dist = abs(agg_dist) / fac * 1000;
MakeToleranceGraph(ms_dist, strcat(outdir, 'tol'));
