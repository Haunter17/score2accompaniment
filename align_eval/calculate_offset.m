function [ dist ] = calculate_offset( ix, iy, gt_x, gt_y )
%UNTITLED4 Summary of this function goes here
%   Detailed explanation goes here
dist = zeros(1, length(gt_x));
for index = 1 : length(gt_x)
    x = gt_x(index);
    y = gt_y(index);
    %% interpolate
    ind_low = find(ix <= x, 1, 'last');
    if ind_low >= length(ix)
        y_pred = iy(end);
    else
        y_low = iy(ind_low);
        y_high = iy(ind_low + 1);
        fac = (x - ix(ind_low)) / (ix(ind_low + 1) - ix(ind_low));
        y_pred = (1 - fac) * y_low + fac * y_high; 
    end            
    dist(index) = y - y_pred;
end

end

