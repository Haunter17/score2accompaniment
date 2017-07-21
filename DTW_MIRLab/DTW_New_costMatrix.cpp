/*
 * Syntax: subseqDTW_costMatrix(costMat, stepsQ, stepsR, weights)
 * costMat is a cost matrix where rows correspond to query frames and columns correspond to reference frames
 * stepsQ and stepsR are both row vectors specifying possible step sizes
 * weights specifies the weighting of each step size
 * return accumulated cost and backtrace matrices
 * */

#include <math.h>
#include "mex.h"

/*
 * Calculate the accumulated cost matrix
 * The query can start matching at any offset with no penalty
 * */
void getSMat(double *ptrS, int8_T *ptrBtMat, const double *ptrCost, const int numRow, const int numCol, int32_T *ptrStepsQ, int32_T *ptrStepsR, double *ptrWeights, int numSteps, bool subsequenceBool) {
   // base case
    if (subsequenceBool)
    {
        for (int col = 0; col < numCol; col++) {
            ptrS[col * numRow] = ptrCost[col * numRow]; // no penalty for starting at any place
            ptrBtMat[col * numRow] = 0; 
        }
    }
    else
    {
        ptrS[0] = ptrCost[0]; // only initialize the first row and col
    }
   // DP
    for (int col = 0; col < numCol; col++) {
        for (int row = 0; row < numRow; row++) {
            // don't calculate the spots that have been filled in the base case
            // will be the whole first row if subsequence, just (0,0) if not
            if (!(col == 0 && row == 0) && !(subsequenceBool && row == 0))
            {
                double bestSoFar = INFINITY;
                int bestOffset = 0;
                // compare different steps
                for (int k = 0; k < numSteps; k++) {
                  int stepQ = ptrStepsQ[k];
                  int stepR = ptrStepsR[k];
                  double weight = ptrWeights[k];
                  if (row - stepQ >= 0 && col - stepR >= 0) {
                      double prevPathScore = ptrS[(col - stepR) * numRow + (row - stepQ)];
                      if (prevPathScore != INFINITY && prevPathScore + weight * ptrCost[col * numRow + row] < bestSoFar) {
                          bestSoFar = prevPathScore + weight * ptrCost[col * numRow + row];
                          bestOffset = k+1; // return results with Matlab-style indexing
                      }
                  }
                }
                // best option
                ptrS[col * numRow + row] = bestSoFar;
                ptrBtMat[col * numRow + row] = bestOffset;
            }
        }
    }
    return;
}

/*
 * Return the optimal accumulated cost,
 * the smallest value at the last row across all columns
 * */
int getMinSCostCol(const double *ptrS, const int numRow, const int numCol) {
    double optimal = INFINITY;
    int index = -1;
    for (int col = 0; col < numCol; col++) {
        if (ptrS[col * numRow + numRow - 1] < optimal) {
            optimal = ptrS[col * numRow + numRow - 1];
            index = col;
        }
    }
    return index;
}

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]) {
#define S plhs[0]
#define optSCost   plhs[1]
#define btMat plhs[2]
#define optOffset plhs[3]
#define costMat    prhs[0]
#define stepsQ    prhs[1]
#define stepsR prhs[2]
#define weights prhs[3]
#define subsequence prhs[4]

    // set matrices
    int rows = mxGetM(costMat);
    int cols = mxGetN(costMat);
    int numSteps = mxGetN(stepsQ);
    S = mxCreateDoubleMatrix(rows, cols, mxREAL);
    optSCost = mxCreateDoubleMatrix(1, 1, mxREAL);
    btMat = mxCreateNumericMatrix(rows, cols, mxINT8_CLASS, mxREAL);
    optOffset = mxCreateNumericMatrix(1, 1, mxINT32_CLASS, mxREAL);

    // set pointers
    double *ptrCost = mxGetPr(costMat);
    double *ptrS = mxGetPr(S);
    double *ptrOptSCost = mxGetPr(optSCost);
    int8_T *ptrBtMat = (int8_T *) mxGetData(btMat);
    int32_T *ptrOptOffset = (int32_T *) mxGetData(optOffset);
    int32_T *ptrStepsQ = (int32_T *) mxGetData(stepsQ);
    int32_T *ptrStepsR = (int32_T *) mxGetData(stepsR);
    double *ptrWeights = mxGetPr(weights);
    bool subsequenceBool = mxGetLogicals(subsequence)[0];
    // determine cumulative cost and backtrace matrices
    getSMat(ptrS, ptrBtMat, ptrCost, rows, cols, ptrStepsQ, ptrStepsR, ptrWeights, numSteps, subsequenceBool);
    
    // index of best path - only relevant for subsequence
    int bestColIndex = -1;
    if (subsequenceBool)
    {
        bestColIndex = getMinSCostCol(ptrS, rows, cols);    
    }
    else
    {
        bestColIndex = cols - 1;
    }
    ptrOptOffset[0] = bestColIndex + 1; // return results in Matlab-style indexing

    // optimal cost
    ptrOptSCost[0] = ptrS[bestColIndex * rows + rows - 1];

    return;
}


