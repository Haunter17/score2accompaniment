function [ output_args ] = dtw_batch(filelist, signal_midi, annot_midi, outdir )
%UNTITLED4 Summary of this function goes here
%   Detailed explanation goes here

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

parfor index = 1:length(fileNameList)
    fileName = fileNameList{index};
    [pathstr,name,ext] = fileparts(fileName);
    disp(['==> Generating alignment on ',name]);
    wavfile = strcat(fileName, '.wav');
    signal_perf = audioread(wavfile);
    annotfile = strcat(fileName, '.csv');
    annot_perf = csvread(annotfile);
    annot_perf = annot_perf(:, 1);
    savefile = strcat(outdir, name);
    [dist, ix, iy] = dtw_single(signal_midi, signal_perf, annot_midi, ...
            annot_perf, savefile, 500, 22050);
end

end

