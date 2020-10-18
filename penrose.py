import tkinter as tk
import numpy as np

phi = (1 + np.sqrt(5)) / 2

def get_angle(a):
    angle = np.arccos(np.clip(a[0] / np.linalg.norm(a), -1, 1)) * 360/2/np.pi
    if a[1] < 0:
        angle = 360 - angle
    return angle

def get_arc_points(vector1, vector2, center, radius):
    #calculate the angle of the arc
    #ensure it is within the range [-180, 180]
    start_angle = get_angle(vector1)
    angle_change = get_angle(vector2) - start_angle
    if np.abs(angle_change) > 180:
        angle_change -= np.sign(angle_change)*360

    #circle radii are half the length of the long edge
    p0 = center + np.array([radius,radius])
    p1 = center - np.array([radius,radius])

    return p0, p1, start_angle, angle_change



class Triangle:
    def __init__(self, a, b, c):
        self.a = a #tip
        self.b = b #outside of full shape
        self.c = c #inside of full shape

    def render_body(self, image):
        image.create_polygon(list(np.concatenate([self.a, self.b, self.c])), fill=self.body_color, outline=self.body_color)

    def render_outline(self, image):
        image.create_line(list(np.concatenate([self.a, self.b, self.b, self.c])), fill='black', width=2)




class acTriangle(Triangle):
    def __init__(self, a, b, c):
        super().__init__(a, b, c)
        self.body_color = 'purple'

    def deflate(self):
        d = self.b + (self.a - self.b) / phi
        e = self.a + (self.c - self.a) / phi
        return [acTriangle(self.b, self.c, e),
                acTriangle(self.b, d, e),
                obTriangle(d, e, self.a)]

    def render_arcs(self, image):
        #draws connection arcs
        ac = self.c - self.a
        ab = self.b - self.a
        r = np.linalg.norm(ac) / phi
        p0, p1, start_angle, angle_change = get_arc_points(ac, ab, self.a, r)
        image.create_arc(p0[0], p0[1], p1[0], p1[1], outline='orange', style='arc', extent=-angle_change, start=-start_angle, width=2)

        ca = self.a - self.c
        cb = self.b - self.c
        r = np.linalg.norm(self.b - self.c) / phi
        p0, p1, start_angle, angle_change = get_arc_points(ca, cb, self.c, r)
        image.create_arc(p0[0], p0[1], p1[0], p1[1], outline='red', style='arc', extent=-angle_change, start=-start_angle, width=2)




class obTriangle(Triangle):
    def __init__(self, a, b, c):
        super().__init__(a, b, c)
        self.body_color = 'blue'

    def deflate(self):
        d = self.c + (self.b - self.c) / phi
        return [acTriangle(self.c, d, self.a),
                obTriangle(d, self.a, self.b)]

    def render_arcs(self, image):
        #draws connection arcs
        ac = self.c - self.a
        ab = self.b - self.a
        r = np.linalg.norm(ab) * (1 - 1 / phi)
        p0, p1, start_angle, angle_change = get_arc_points(ac, ab, self.a, r)
        image.create_arc(p0[0], p0[1], p1[0], p1[1], outline='red', style='arc', extent=-angle_change, start=-start_angle, width=2)

        ca = self.a - self.c
        cb = self.b - self.c
        r = np.linalg.norm(cb) * (1 - 1 / phi)
        p0, p1, start_angle, angle_change = get_arc_points(ca, cb, self.c, r)
        image.create_arc(p0[0], p0[1], p1[0], p1[1], outline='orange', style='arc', extent=-angle_change, start=-start_angle, width=2)



class Penrose:
    def __init__(self, width=750, height=750):
        #setup the window
        self.window = tk.Tk()
        self.window.title('Penrose Tiling')
        self.image = tk.Canvas(self.window, width=width, height=height)
        self.image.pack()
        self.image.configure(background='black')

        self.width = width
        self.height = height
        self.origin = np.array([width/2, height/2])
        #self.radius = np.sqrt(width**2 + height**2)
        self.radius = width/2



        #initial seed shape "sun" with 5 deflations
        self.initialize_sun()
        self.deflation_count = 3
        for i in range(self.deflation_count):
            self.deflate()


    def initialize_sun(self):
        self.shapes = []
        for i in range(5):
            theta1 = 2*np.pi/5 * i
            theta2 = 2*np.pi/10
            self.shapes.append(acTriangle(np.array([0, 0]),
                                          np.array([self.radius*np.cos(theta1), self.radius*np.sin(theta1)]),
                                          np.array([self.radius*np.cos(theta1+theta2), self.radius*np.sin(theta1+theta2)])))
            self.shapes.append(acTriangle(np.array([0, 0]),
                                          np.array([self.radius*np.cos(theta1+2*theta2), self.radius*np.sin(theta1+2*theta2)]),
                                          np.array([self.radius*np.cos(theta1+theta2), self.radius*np.sin(theta1+theta2)])))
        view = np.array([self.width/2, self.height/2])
        for shape in self.shapes:
            shape.a = shape.a + view
            shape.b = shape.b + view
            shape.c = shape.c + view




    def deflate(self):
        new_list = []
        for shape in self.shapes:
            for new_shape in shape.deflate():
                new_list.append(new_shape)
        self.shapes = new_list




    def render(self):
        for tri in self.shapes:
            tri.render_body(self.image) #bodies
        for tri in self.shapes:
            tri.render_outline(self.image) #outlines
        for tri in self.shapes:
            tri.render_arcs(self.image) #arcs


def deflate_event(event):
    pattern.deflation_count += 1
    pattern.deflate()
    pattern.render()

def inflate_event(event):
    if pattern.deflation_count <= 0:
        return
    pattern.deflation_count -= 1
    pattern.initialize_sun()
    for i in range(pattern.deflation_count):
        pattern.deflate()
    pattern.render()

if __name__ == '__main__':
    pattern = Penrose()
    pattern.render()

    pattern.window.bind('-', inflate_event)
    pattern.window.bind('=', deflate_event)

    pattern.window.mainloop()
