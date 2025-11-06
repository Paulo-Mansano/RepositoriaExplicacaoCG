import math

class Ponto:
    def __init__(self, x=0,y=0,z=0):
        self.x = x
        self.y = y
        self.z = z
    
    def set(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def copy(self):
        return Ponto(self.x, self.y, self.z)

    def __add__(self, other):
        return Ponto(self.x+other.x, self.y+other.y, self.z+other.z)

    def __sub__(self, other):
        return Ponto(self.x-other.x, self.y-other.y, self.z-other.z)

    def __mul__(self, k: float):
        return Ponto(self.x*k, self.y*k, self.z*k)

    def __truediv__(self, k: float):
        return Ponto(self.x/k, self.y/k, self.z/k)

    def to_tuple(self):
        return (self.x, self.y, self.z)

def dist(a: Ponto, b: Ponto) -> float:
    dx = a.x - b.x
    dy = a.y - b.y
    dz = a.z - b.z
    return math.sqrt(dx*dx + dy*dy + dz*dz)

# Utilidades 2D originais (resumidas):
def intersec2d(a: Ponto, b: Ponto, c: Ponto, d: Ponto):
    den = (a.x-b.x)*(c.y-d.y)-(a.y-b.y)*(c.x-d.x)
    if abs(den) < 1e-9: return 0, 0.0, 0.0
    s = ((a.x-c.x)*(c.y-d.y)-(a.y-c.y)*(c.x-d.x))/den
    t = ((a.x-c.x)*(a.y-b.y)-(a.y-c.y)*(a.x-b.x))/den
    return 1, s, t

def HaInterseccao(k: Ponto, l: Ponto, m: Ponto, n: Ponto) -> bool:
    ret, s, t = intersec2d(k, l, m, n)
    if not ret: return False
    return s>=0.0 and s<=1.0 and t>=0.0 and t<=1.0