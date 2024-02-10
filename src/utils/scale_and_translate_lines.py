def scale_and_translate_lines(lines, box_x, box_y):
    """
    Scale and translate lines from box X to fit within box Y, maintaining their relative size and position.

    :param lines: A list of lines defined by their start and end points, lying strictly within box X.
    :param box_x: The original box defined by the top-left and bottom-right coordinates.
    :param box_y: The target box defined by the top-left and bottom-right coordinates, with a different scale and translation.
    :return: A list of lines scaled and translated to fit within box Y.
    """

    # Unpack the coordinates of the boxes
    (x_min_x, y_min_x), (x_max_x, y_max_x) = box_x
    (x_min_y, y_min_y), (x_max_y, y_max_y) = box_y

    # Calculate scale factors for both axes
    scale_x = (x_max_y - x_min_y) / (x_max_x - x_min_x)
    scale_y = (y_max_y - y_min_y) / (y_max_x - y_min_x)

    # Calculate translation needed
    translate_x = x_min_y - (x_min_x * scale_x)
    translate_y = y_min_y - (y_min_x * scale_y)

    # Scale and translate lines
    scaled_and_translated_lines = []
    for line in lines:
        ((x0, y0), (x1, y1)) = line
        new_x0 = (x0 * scale_x) + translate_x
        new_y0 = (y0 * scale_y) + translate_y
        new_x1 = (x1 * scale_x) + translate_x
        new_y1 = (y1 * scale_y) + translate_y
        scaled_and_translated_lines.append(((new_x0, new_y0), (new_x1, new_y1)))

    return scaled_and_translated_lines

# Define boxes and lines
box_x = ((100, 100), (250, 250))
box_y = ((200, 200), (450, 450))
lines = [((100, 100), (200, 200)), ((150, 150), (250, 250))]

# Scale and translate lines
scaled_and_translated_lines = scale_and_translate_lines(lines, box_x, box_y)
scaled_and_translated_lines
