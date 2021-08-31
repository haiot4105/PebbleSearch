import numpy as np

def dist_point_line_segment(begin, end, point):

        dot = (point - begin).dot(end - begin)
        sq_len = (end - begin).dot(end - begin)
        r = -1

        if sq_len != 0:
            r = dot / sq_len

		if r < 0.0:
			return np.linalg.norm(point - begin)
		elif r > 1.0:
			return np.linalg.norm(point - end)
		else
			return np.linalg.norm(c - (a + r * (b - a)))


    # var A = x - x1;
    # var B = y - y1;
    # var C = x2 - x1;
    # var D = y2 - y1;

    # var dot = A * C + B * D;
    # var len_sq = C * C + D * D;
    # var param = -1;
    # if (len_sq != 0) //in case of 0 length line
    #     param = dot / len_sq;

    # var xx, yy;

    # if (param < 0) {
    #     xx = x1;
    #     yy = y1;
    # }
    # else if (param > 1) {
    #     xx = x2;
    #     yy = y2;
    # }
    # else {
    #     xx = x1 + param * C;
    #     yy = y1 + param * D;
    # }

    # var dx = x - xx;
    # var dy = y - yy;
    # return Math.sqrt(dx * dx + dy * dy);