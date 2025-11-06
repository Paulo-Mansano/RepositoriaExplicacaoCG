from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from Ponto import *

class Objeto3D:
    def __init__(self):
        self.vertices = []
        self.faces    = []
        self.position = Ponto(0,0,0)
        self.rotation = (0,0,0,0)

    def LoadFile(self, file:str):
        f = open(file, "r", encoding="utf-8")
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            values = line.split()
            if not values:
                continue

            if values[0] == 'v':
                self.vertices.append(Ponto(float(values[1]),
                                           float(values[2]),
                                           float(values[3])))

            if values[0] == 'f':
                idxs = []
                for fVertex in values[1:]:
                    fInfo = fVertex.split('/')
                    if fInfo[0] == '':
                        continue
                    idxs.append(int(fInfo[0]) - 1) # obj é 1-based
                if len(idxs) >= 3:
                    self.faces.append(idxs)
        f.close()

    # ---------- Métodos auxiliares (NOVOS) ----------
    def compute_bbox(self):
        if not self.vertices:
            return Ponto(0,0,0), Ponto(0,0,0)
        xs = [v.x for v in self.vertices]
        ys = [v.y for v in self.vertices]
        zs = [v.z for v in self.vertices]
        return Ponto(min(xs),min(ys),min(zs)), Ponto(max(xs),max(ys),max(zs))

    def normalize_unit_and_center(self):
        mn, mx = self.compute_bbox()
        cx, cy, cz = 0.5*(mn.x+mx.x), 0.5*(mn.y+mx.y), 0.5*(mn.z+mx.z)
        ext_x, ext_y, ext_z = mx.x-mn.x, mx.y-mn.y, mx.z-mn.z
        max_ext = max(ext_x, ext_y, ext_z) if max(ext_x, ext_y, ext_z) > 0 else 1.0
        s = 1.0/max_ext
        for v in self.vertices:
            v.x = (v.x - cx)*s
            v.y = (v.y - cy)*s
            v.z = (v.z - cz)*s

    def triangulated_faces(self):
        tris = []
        for f in self.faces:
            if len(f) == 3:
                tris.append( (f[0], f[1], f[2]) )
            elif len(f) > 3:
                for i in range(1, len(f)-1):
                    tris.append( (f[0], f[i], f[i+1]) )
        return tris
    # ------------------------------------------------

    def DesenhaVertices(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(.1, .1, .8)
        glPointSize(8)
        glBegin(GL_POINTS)
        for v in self.vertices:
            glVertex3f(v.x, v.y, v.z)
        glEnd()
        glPopMatrix()

    def DesenhaWireframe(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(0, 0, 0)
        glLineWidth(2)
        for f in self.faces:
            glBegin(GL_LINE_LOOP)
            for iv in f:
                v = self.vertices[iv]
                glVertex3f(v.x, v.y, v.z)
            glEnd()
        glPopMatrix()

    def Desenha(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(0.34, .34, .34)
        glLineWidth(2)
        for f in self.faces:
            glBegin(GL_TRIANGLE_FAN)
            for iv in f:
                v = self.vertices[iv]
                glVertex3f(v.x, v.y, v.z)
            glEnd()
        glPopMatrix()