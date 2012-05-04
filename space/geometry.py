from math import sin, cos, pow, sqrt

# scale verts by factor s
def scale2d(verts, s):
    return [(v[0]*s, v[1]*s) for v in verts]

# rotate verts around origin theta radians
def rotate2d(verts, theta):
    cos_t = cos(theta)
    sin_t = sin(theta)
    return [(v[0]*cos_t - v[1]*sin_t, v[0]*sin_t + v[1]*cos_t) for v in verts]

# apply translation to verts
def translate2d(verts, trans):
    return [(v[0] + trans[0], v[1] + trans[1]) for v in verts]

# return unit vector with angle theta
def unit_vector(theta):
    return rotate2d([(0, -1)], theta)[0]

# add two vectors of same length
def vec_sum(a, b):
    return tuple(map(sum, zip(a, b)))

# return distance between 2d vectors a and b
def distance2d(a, b):
    return sqrt(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2))
    
