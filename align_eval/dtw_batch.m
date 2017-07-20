function [ output_args ] = dtw_batch( wav_list, annot_list, signal_x, annot_x, outdir )
%UNTITLED4 Summary of this function goes here
%   Detailed explanation goes here

fid = fopen(wav_list);
wavFileList = '';
fileIndex = 1;
curfile = fgetl(fid);
while ischar(curfile)
    wavFileList{fileIndex} = curfile;
    curfile = fgetl(fid);
    fileIndex = fileIndex + 1;
end
fclose(fid);

fid = fopen(annot_list);
annotFileList = '';
fileIndex = 1;
curfile = fgetl(fid);
while ischar(curfile)
    annotFileList{fileIndex} = curfile;
    curfile = fgetl(fid);
    fileIndex = fileIndex + 1;
end
fclose(fid);

parfor index = 1:length(wavFileList)
    wavfile = wavFileList{index};
    [pathstr,name,ext] = fileparts(wavfile);
    disp(['Generating alignment on ',name]);
    signal_y = audioread(wavfile);
    annotfile = annotFileList{index};
    annot_y = csvread(annotfile); % to fix later
    savefile = strcat(outdir, name);
    [dist, ix, iy] = dtw_single(signal_x, signal_y, annot_x, ...
            annot_y, savefile, 22050);
end

end

