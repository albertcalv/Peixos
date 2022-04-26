import math

def add_vector_to_point(point, vector):
    return point[0] + vector[0], point[1] + vector[1]
    
def get_vector_between_points(final, inicial):
    return final[0] - inicial[0], final[1] - inicial[1]
    
def get_vector_length(vector):
    return math.hypot(vector[0], vector[1])