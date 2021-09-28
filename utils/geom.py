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
	else:
		return np.linalg.norm(point - (begin + r * (end - begin)))