/*
 * Syntax: DTW_backtrace(btMat, stepsQ, stepsR[, endIdx])
 * btMat is a backtrace matrix where rows correspond to query frames and columns correspond to reference frames
 * stepsQ and stepsR are row vectors specifying step sizes
 * endIdx is an optional argument that specifies the reference frame index from which to backtrace (subseqDTW only)
 * returns 2xL matrix containing path coordinates
 * Note: all inputs and outputs use Matlab-style indexing (not C-style)
 * */

#include <math.h>
#include "mex.h"
#include <vector>
using namespace std;

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]) {
#define P plhs[0]
#define btMat prhs[0]
#define stepsQ    prhs[1]
#define stepsR prhs[2]
#define endIndex prhs[3]

    // initialize
    int rows = mxGetM(btMat);
    int cols = mxGetN(btMat);
    int numSteps = mxGetN(stepsQ);
    vector<int> pathQ;
    vector<int> pathR;
    int8_T *ptrBtMat = (int8_T *) mxGetData(btMat);
    int32_T *ptrStepsQ = (int32_T *) mxGetData(stepsQ);
    int32_T *ptrStepsR = (int32_T *) mxGetData(stepsR);
    int endPt;
    bool isSubSeq;
    if (nrhs < 4) {
      isSubSeq = false; // if not specified, assume full DTW
      endPt = cols  - 1; 
    } 
    else {
      isSubSeq = true; // if specified, assume subsequence DTW
      int32_T *ptrEndIndex = (int32_T *) mxGetData(endIndex);
      endPt = ptrEndIndex[0] - 1; // switch from Matlab-style indexing to C-style
    }

    // backtrace
    int curQ = rows - 1;
    int curR = endPt;
    int stepIndex;
    int count = 0;
    if (isSubSeq) { // subsequence DTW
      while (curQ > 0 && ptrBtMat[curR * rows + curQ] > 0){
	count++;
	pathQ.push_back(curQ);
	pathR.push_back(curR);
	stepIndex = ptrBtMat[curR * rows + curQ] - 1; // switch from Matlab-style indexing to C-style
	curQ = curQ - ptrStepsQ[stepIndex];
	curR = curR - ptrStepsR[stepIndex];
      }
      pathQ.push_back(curQ);
      pathR.push_back(curR);
    }
    else { // full DTW
      while (ptrBtMat[curR * rows + curQ] > 0 && (curQ > 0 || curR > 0)) {
	pathQ.push_back(curQ);
	pathR.push_back(curR);
	stepIndex = ptrBtMat[curR * rows + curQ] - 1; // see comment above
	curQ = curQ - ptrStepsQ[stepIndex];
	curR = curR - ptrStepsR[stepIndex];
      }
      pathQ.push_back(curQ);
      pathR.push_back(curR);
    }

    // copy results to return variable
    P = mxCreateNumericMatrix(2, pathQ.size(), mxINT32_CLASS, mxREAL);
    int32_T *ptrP = (int32_T *) mxGetData(P);
    int pathLen = pathQ.size();
    for (int i = 0; i < pathLen; i++) {
      ptrP[i * 2] = pathQ[pathLen - 1 - i] + 1; // switch back to Matlab-style indexing
      ptrP[i * 2 + 1] = pathR[pathLen - 1 - i] + 1;
    }

    return;
}
