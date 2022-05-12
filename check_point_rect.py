def two_point_to_xyxy(first_point, second_point):
    x0, y0 = first_point
    x1, y1 = second_point
    x_top = min(x0, x1)
    y_top = min(y0, y1)
    x_bottom = max(x0, x1)
    y_bottom = max(y0, y1)
    return x_top, y_top, x_bottom, y_bottom