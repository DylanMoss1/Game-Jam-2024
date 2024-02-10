def line_clip(line, box):
    """
    Implements the Cohen-Sutherland algorithm for line clipping against a rectangular box.

    :param line: A tuple of start and end points of the line ((x0, y0), (x1, y1))
    :param box: A tuple of the top-left and bottom-right corners of the box ((x_min, y_min), (x_max, y_max))
    :return: The clipped line as a tuple of start and end points if it lies within the box, otherwise None.
    """

    # Define Cohen-Sutherland outcodes
    INSIDE = 0  # 0000
    LEFT = 1    # 0001
    RIGHT = 2   # 0010
    BOTTOM = 4  # 0100
    TOP = 8     # 1000

    # Unpack the line and box coordinates
    (x0, y0), (x1, y1) = line
    (x_min, y_min), (x_max, y_max) = box

    def compute_outcode(x, y):
        """
        Compute the outcode for a point given the box boundaries.
        """
        code = INSIDE
        if x < x_min:  # to the left of the box
            code |= LEFT
        elif x > x_max:  # to the right of the box
            code |= RIGHT
        if y < y_min:  # below the box
            code |= BOTTOM
        elif y > y_max:  # above the box
            code |= TOP
        return code

    outcode0 = compute_outcode(x0, y0)
    outcode1 = compute_outcode(x1, y1)
    accept = False

    while True:
        if not (outcode0 | outcode1):
            # Both points inside box
            accept = True
            break
        elif outcode0 & outcode1:
            # Both points share an outside zone (bitwise AND is not 0)
            break
        else:
            # Choose the point to clip
            outcode_out = outcode0 if outcode0 else outcode1

            # Find intersection point
            if outcode_out & TOP:
                x = x0 + (x1 - x0) * (y_max - y0) / (y1 - y0)
                y = y_max
            elif outcode_out & BOTTOM:
                x = x0 + (x1 - x0) * (y_min - y0) / (y1 - y0)
                y = y_min
            elif outcode_out & RIGHT:
                y = y0 + (y1 - y0) * (x_max - x0) / (x1 - x0)
                x = x_max
            elif outcode_out & LEFT:
                y = y0 + (y1 - y0) * (x_min - x0) / (x1 - x0)
                x = x_min

            # Replace outside point with intersection point
            if outcode_out == outcode0:
                x0, y0 = x, y
                outcode0 = compute_outcode(x0, y0)
            else:
                x1, y1 = x, y
                outcode1 = compute_outcode(x1, y1)

    if accept:
        return ((x0, y0), (x1, y1))
    else:
        return None

def clip_lines_within_box(lines, box):
    """
    Clips each line in a list of lines to a given box, discarding lines completely outside the box.

    :param lines: A list of lines defined by their start and end points.
    :param box: A box defined by the top-left and bottom-right coordinates.
    :return: A list of lines that lie inside or partially inside the box.
    """
    clipped_lines = []
    for line in lines:
        clipped_line = line_clip(line, box)
        if clipped_line is not None:
            clipped_lines.append(clipped_line)
    return clipped_lines

if __name__ == "__main__":
    # Test 1
    lines = [((100, 100), (200, 200)), ((200, 200), (300, 300))]
    box = ((100, 100), (250, 250))
    clipped_lines = clip_lines_within_box(lines, box)
    print(f"Clipped lines: {clipped_lines} (expected [((100, 100), (200, 200)), ((200, 200), (250, 250))])")

    # Test 2
    lines = [((-4, 4), (4, 8)), ((3, 0), (6, 12))]
    box = ((1, 1), (6, 6))
    clipped_lines = clip_lines_within_box(lines, box)
    print(f"Clipped lines: {clipped_lines} (expected [((3.25, 1), (4.5, 6))])")
