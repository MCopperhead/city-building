#include <stdlib.h>

__declspec(dllexport) int contains(int x, int y, int x1, int y1, int x2, int y2, int x3, int y3,
             int x4, int y4, int x5, int y5, int x6, int y6) {
    int s, s1, s2, s3;

    /* calculate first triangle */
    s = abs(x2*y3-x3*y2-x1*y3+x3*y1+x1*y2-x2*y1);
    s1 = abs(x2*y3-x3*y2-x*y3+x3*y+x*y2-x2*y);
    s2 = abs(x*y3-x3*y-x1*y3+x3*y1+x1*y-x*y1);
    s3 = abs(x2*y-x*y2-x1*y+x*y1+x1*y2-x2*y1);

    if (s == s1 + s2 + s3)
    {
        return 1;
    }

    /* calculate second triangle */
    s = abs(x5*y6-x6*y5-x4*y6+x6*y4+x4*y5-x5*y4);
    s1 = abs(x5*y6-x6*y5-x*y6+x6*y+x*y5-x5*y);
    s2 = abs(x*y6-x6*y-x4*y6+x6*y4+x4*y-x*y4);
    s3 = abs(x5*y-x*y5-x4*y+x*y4+x4*y5-x2*y4);

    return s == s1 + s2 + s3;
}