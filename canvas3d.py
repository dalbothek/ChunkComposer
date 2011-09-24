# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

import Tkinter as tk


class Canvas3D:
    def __init__(self):
        self.root = tk.Tk()
        self.ca = tk.Canvas(self.root, width=600, height=800)
        self.ca.pack()
        self.polys = []

    def add(self, x, y, z, c):
        if c is None:
            return
        polys = []
        coord = (x, y, z)
        for axis in range(3):
            for side in range(2):
                poly = []
                a1 = (axis + 1) % 3
                a2 = (axis + 2) % 3
                s2 = (side + 1) % 2
                for point in range(4):
                    poly.append([side + x, side + y, side + z])
                poly[1][a1] = s2 + coord[a1]
                poly[2][a1] = s2 + coord[a1]
                poly[2][a2] = s2 + coord[a2]
                poly[3][a2] = s2 + coord[a2]
                poly.append(c)
                polys.append(poly)
        self.polys += polys

    def draw(self, wireframe=True):
        polys = sorted(self.polys, key=lambda poly: poly[0][2])

        for poly in polys:
            if poly[-1] == "":
                continue
            coords = []
            for point in poly[:-1]:
                coords.append(20 + point[0] * 20 + point[2] * 10)
                coords.append(620 - point[1] * 20 + point[2] * 10)
            self.ca.create_polygon(*coords, outline="", fill=poly[-1])

        self.ca.update()

        if wireframe:
            for poly in polys:
                coords = []
                for point in poly[:-1]:
                    coords.append(20 + point[0] * 20 + point[2] * 10)
                    coords.append(620 - point[1] * 20 + point[2] * 10)
                self.ca.create_polygon(*coords, outline="black", fill="")

        self.root.mainloop()
