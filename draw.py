from display import *
from matrix import *
from math import *
from gmath import *

def scanline_convert(polygons, i, screen, zbuffer, color ):
    flip = False
    BOT = 0
    TOP = 2
    MID = 1

    points = [ (polygons[i][0], polygons[i][1], polygons[i][2]),
               (polygons[i+1][0], polygons[i+1][1], polygons[i+1][2]),
               (polygons[i+2][0], polygons[i+2][1], polygons[i+2][2]) ]

    # color = [0,0,0]
    # color[RED] = (23*(i/3)) %256
    # color[GREEN] = (109*(i/3)) %256
    # color[BLUE] = (227*(i/3)) %256

    points.sort(key = lambda x: x[1])
    x0 = points[BOT][0]
    z0 = points[BOT][2]
    x1 = points[BOT][0]
    z1 = points[BOT][2]
    y = int(points[BOT][1])

    distance0 = int(points[TOP][1]) - y * 1.0
    distance1 = int(points[MID][1]) - y * 1.0
    distance2 = int(points[TOP][1]) - int(points[MID][1]) * 1.0

    dx0 = (points[TOP][0] - points[BOT][0]) / distance0 if distance0 != 0 else 0
    dz0 = (points[TOP][2] - points[BOT][2]) / distance0 if distance0 != 0 else 0
    dx1 = (points[MID][0] - points[BOT][0]) / distance1 if distance1 != 0 else 0
    dz1 = (points[MID][2] - points[BOT][2]) / distance1 if distance1 != 0 else 0

    while y <= int(points[TOP][1]):

        draw_line(int(x0), y, z0, int(x1), y, z1, screen, zbuffer, color)
        x0+= dx0
        z0+= dz0
        x1+= dx1
        z1+= dz1
        y+= 1

        if ( not flip and y >= int(points[MID][1])):
            flip = True

            dx1 = (points[TOP][0] - points[MID][0]) / distance2 if distance2 != 0 else 0
            dz1 = (points[TOP][2] - points[MID][2]) / distance2 if distance2 != 0 else 0
            x1 = points[MID][0]
            z1 = points[MID][2]

def add_polygon( polygons, x0, y0, z0, x1, y1, z1, x2, y2, z2 ):
    add_point(polygons, x0, y0, z0);
    add_point(polygons, x1, y1, z1);
    add_point(polygons, x2, y2, z2);

def draw_polygons( matrix, screen, zbuffer, view, ambient, light, areflect, dreflect, sreflect):
    if len(matrix) < 2:
        print 'Need at least 3 points to draw'
        return

    point = 0
    while point < len(matrix) - 2:

        normal = calculate_normal(matrix, point)[:]
        if dot_product(normal, view) > 0:
            color = get_lighting(normal, view, ambient, light, areflect, dreflect, sreflect )
            scanline_convert(matrix, point, screen, zbuffer, color)

            # draw_line( int(matrix[point][0]),
            #            int(matrix[point][1]),
            #            matrix[point][2],
            #            int(matrix[point+1][0]),
            #            int(matrix[point+1][1]),
            #            matrix[point+1][2],
            #            screen, zbuffer, color)
            # draw_line( int(matrix[point+2][0]),
            #            int(matrix[point+2][1]),
            #            matrix[point+2][2],
            #            int(matrix[point+1][0]),
            #            int(matrix[point+1][1]),
            #            matrix[point+1][2],
            #            screen, zbuffer, color)
            # draw_line( int(matrix[point][0]),
            #            int(matrix[point][1]),
            #            matrix[point][2],
            #            int(matrix[point+2][0]),
            #            int(matrix[point+2][1]),
            #            matrix[point+2][2],
            #            screen, zbuffer, color)
        point+= 3


def add_box( polygons, x, y, z, width, height, depth ):
    x1 = x + width
    y1 = y - height
    z1 = z - depth

    #front
    add_polygon(polygons, x, y, z, x1, y1, z, x1, y, z);
    add_polygon(polygons, x, y, z, x, y1, z, x1, y1, z);

    #back
    add_polygon(polygons, x1, y, z1, x, y1, z1, x, y, z1);
    add_polygon(polygons, x1, y, z1, x1, y1, z1, x, y1, z1);

    #right side
    add_polygon(polygons, x1, y, z, x1, y1, z1, x1, y, z1);
    add_polygon(polygons, x1, y, z, x1, y1, z, x1, y1, z1);
    #left side
    add_polygon(polygons, x, y, z1, x, y1, z, x, y, z);
    add_polygon(polygons, x, y, z1, x, y1, z1, x, y1, z);

    #top
    add_polygon(polygons, x, y, z1, x1, y, z, x1, y, z1);
    add_polygon(polygons, x, y, z1, x, y, z, x1, y, z);
    #bottom
    add_polygon(polygons, x, y1, z, x1, y1, z1, x1, y1, z);
    add_polygon(polygons, x, y1, z, x, y1, z1, x1, y1, z1);

def generate_cone( cx, cy, cz, r, h, step ):
    base_points = []
    lat_points = []

    for rotation in range(0, step):
        rot = rotation/float(step)
        for cicle in range(0, step + 1):
            circ = circle/float(step)

            x = cx + r * circ * math.cos(2*math.pi * rot)
            y = cy
            z = cz + r * circ * math.sin(2*math.pi * rot)

            base_points.append([x, y, z])

            y = cy + h * (1 - circ)

            lat_points.append([x, y, z])

    return (base_points, lat_points)
    

'''
 (t, u+1)--(t+1, u+1)      ^
    |     /   |            |
    |   /     |            y   x - >
 (t, u )----(t+1, u )
'''
# func takes two float arguments t and u that range from 0 to 1 (inclusive) and returns a list [x, y, z]
def add_parametric( edges, func, step):
    for t_int in range(0, step):
        t1 = t_int/float(step)
        t2 = (t_int + 1)/float(step)
        
        for u_int in range(0, step):
            u1 = u_int/float(step)
            u2 = (u_int + 1)/float(step)
            
            args1 = [edges] + func(t1, u1) + func(t2, u1) + func(t2, u2)
            args2 = [edges] + func(t1, u1) + func(t2, u2) + func(t1, u2)
            
            add_polygon(*args1)
            add_polygon(*args2)
            

def add_sphere( edges, cx, cy, cz, r, step):
    def parametric(t, u):
        x = r * math.cos(math.pi * t) + cx
        y = r * math.sin(math.pi * t) * math.cos(2*math.pi * u) + cy
        z = r * math.sin(math.pi * t) * math.sin(2*math.pi * u) + cz
        
        return [x, y, z]

    add_parametric( edges, parametric, step )


def add_torus( edges, cx, cy, cz, r0, r1, step ):
    def parametric(t, u):
        x = math.cos(2*math.pi * t) * (r0 * math.cos(2*math.pi * u) + r1) + cx;
        y = r0 * math.sin(2*math.pi * u) + cy;
        z = -1*math.sin(2*math.pi * t) * (r0 * math.cos(2*math.pi * u) + r1) + cz;

        return [x, y, z]

    add_parametric( edges, parametric, step )

def add_cone( edges, cx, cy, cz, r, h, step ):
    def para_base(t, u):
        x = cx + r * t * math.cos(2 * math.pi * u)
        y = cy
        z = cz + r * t * math.sin(2 * math.pi * u)

        return [x, y, z]

    def para_lateral(t, u):
        x = cx + r * u * math.cos(2 * math.pi * t)
        y = cy + h * (1 - u)
        z = cz + r * u * math.sin(2 * math.pi * t)

        return [x, y, z]

    add_parametric( edges, para_base, step )
    add_parametric( edges, para_lateral, step )

def add_coil( edges, cx, cy, cz, r0, r1, h, n, step ):

    def para_bottom(t, u):
        x = cx + r1 + t * r0 * math.cos(2 * math.pi * u)
        y = cy + t * r0 * math.sin(2 * math.pi * u)
        z = cz

        return [x, y, z]

    def para_top(t, u):
        x = cx + r1 + u * r0 * math.cos(2 * math.pi * t)
        y = cy + h + u * r0 * math.sin(2 * math.pi * t)
        z = cz

        return [x, y, z]
    
    def para_coil(t, u):
        x = math.cos(2*math.pi * t * n) * (r0 * math.cos(2*math.pi * u) + r1) + cx;
        y = r0 * math.sin(2*math.pi * u) + t * h + cy;
        z = -1*math.sin(2*math.pi * t * n) * (r0 * math.cos(2*math.pi * u) + r1) + cz;

        return [x, y, z]

    add_parametric( edges, para_bottom, step )
    add_parametric( edges, para_top, step )
    add_parametric( edges, para_coil, step * int(n))

        
    

def add_circle( points, cx, cy, cz, r, step ):
    x0 = r + cx
    y0 = cy
    i = 1
    while i <= step:
        t = float(i)/step
        x1 = r * math.cos(2*math.pi * t) + cx;
        y1 = r * math.sin(2*math.pi * t) + cy;

        add_edge(points, x0, y0, cz, x1, y1, cz)
        x0 = x1
        y0 = y1
        i+= 1

def add_curve( points, x0, y0, x1, y1, x2, y2, x3, y3, step, curve_type ):

    xcoefs = generate_curve_coefs(x0, x1, x2, x3, curve_type)[0]
    ycoefs = generate_curve_coefs(y0, y1, y2, y3, curve_type)[0]

    i = 1
    while i <= step:
        t = float(i)/step
        x = xcoefs[0] * t*t*t + xcoefs[1] * t*t + xcoefs[2] * t + xcoefs[3]
        y = ycoefs[0] * t*t*t + ycoefs[1] * t*t + ycoefs[2] * t + ycoefs[3]

        add_edge(points, x0, y0, 0, x, y, 0)
        x0 = x
        y0 = y
        i+= 1


def draw_lines( matrix, screen, zbuffer, color ):
    if len(matrix) < 2:
        print 'Need at least 2 points to draw'
        return

    point = 0
    while point < len(matrix) - 1:
        draw_line( int(matrix[point][0]),
                   int(matrix[point][1]),
                   matrix[point][2],
                   int(matrix[point+1][0]),
                   int(matrix[point+1][1]),
                   matrix[point+1][2],
                   screen, zbuffer, color)
        point+= 2

def add_edge( matrix, x0, y0, z0, x1, y1, z1 ):
    add_point(matrix, x0, y0, z0)
    add_point(matrix, x1, y1, z1)

def add_point( matrix, x, y, z=0 ):
    matrix.append( [x, y, z, 1] )


def draw_line( x0, y0, z0, x1, y1, z1, screen, zbuffer, color ):

    #swap points if going right -> left
    if x0 > x1:
        xt = x0
        yt = y0
        zt = z0
        x0 = x1
        y0 = y1
        z0 = z1
        x1 = xt
        y1 = yt
        z1 = zt

    x = x0
    y = y0
    z = z0
    A = 2 * (y1 - y0)
    B = -2 * (x1 - x0)
    wide = False
    tall = False

    if ( abs(x1-x0) >= abs(y1 - y0) ): #octants 1/8
        wide = True
        loop_start = x
        loop_end = x1
        dx_east = dx_northeast = 1
        dy_east = 0
        d_east = A
        distance = x1 - x
        if ( A > 0 ): #octant 1
            d = A + B/2
            dy_northeast = 1
            d_northeast = A + B
        else: #octant 8
            d = A - B/2
            dy_northeast = -1
            d_northeast = A - B

    else: #octants 2/7
        tall = True
        dx_east = 0
        dx_northeast = 1
        distance = abs(y1 - y)
        if ( A > 0 ): #octant 2
            d = A/2 + B
            dy_east = dy_northeast = 1
            d_northeast = A + B
            d_east = B
            loop_start = y
            loop_end = y1
        else: #octant 7
            d = A/2 - B
            dy_east = dy_northeast = -1
            d_northeast = A - B
            d_east = -1 * B
            loop_start = y1
            loop_end = y

    dz = (z1 - z0) / distance if distance != 0 else 0

    while ( loop_start < loop_end ):
        plot( screen, zbuffer, color, x, y, z )
        if ( (wide and ((A > 0 and d > 0) or (A < 0 and d < 0))) or
             (tall and ((A > 0 and d < 0) or (A < 0 and d > 0 )))):

            x+= dx_northeast
            y+= dy_northeast
            d+= d_northeast
        else:
            x+= dx_east
            y+= dy_east
            d+= d_east
        z+= dz
        loop_start+= 1
    plot( screen, zbuffer, color, x, y, z )
