from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import math

from Objeto3D import *
from Morpher import *

# Variáveis Globais
objA: Objeto3D = None
objB: Objeto3D = None

trisA_idx = [] # Lista de triângulos do Objeto A, cada item é uma tupla de 3 inteiros 
vertex_map_A_to_B = [] # Mapa de A pra B

trisB_idx = []            # Lista de triângulos do Objeto B
vertex_map_B_to_A = []  # Mapa reverso (de B pra A)
# ---------------------

winLeft = None 
winRight = None
winMorph = None

nFrames = 120 # número total de quadros da animação. Controla a duração/velocidade.
curFrame = 0 # quadro atual da animação
playing = False # Um boolean que controla se a animação está rodando ou pausada

# --- Globais da Câmera ---
cam_angle_y = 0.0 # ângulo de rotação da câmera ao redor do eixo Y, precisamos dele pra girar a câmera
cam_distance = 2.2
eye = [0.0, 0.3, 2.2]
center = [0.0, 0.0, 0.0] # Esses três definem pra onde o gluLookAt vai olhar 
up = [0.0, 1.0, 0.0]


# A luz vem de um ponto específico definido em position
def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    ambient  = [0.2, 0.2, 0.2, 1.0]
    diffuse  = [0.8, 0.8, 0.8, 1.0]
    specular = [0.2, 0.2, 0.2, 1.0]
    position = [2.0, 4.0, 2.0, 1.0]
    glLightfv(GL_LIGHT0, GL_AMBIENT,  ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular)
    glLightfv(GL_LIGHT0, GL_POSITION, position)

    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.1,0.1,0.1,1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 16.0)

# Aqui é só pra desenhar o chão mesmo
def draw_floor():
    glDisable(GL_LIGHTING)
    # Define a cor com Alpha 1.0
    glColor4f(0.85, 0.85, 0.9, 1.0)
    glBegin(GL_QUADS)
    s = 1.5
    glVertex3f(-s, -0.7, -s)
    glVertex3f( s, -0.7, -s)
    glVertex3f( s, -0.7,  s)
    glVertex3f(-s, -0.7,  s)
    glEnd()
    glEnable(GL_LIGHTING)

def apply_camera():
    rad_angle = math.radians(cam_angle_y) #Parte necessária pra girar a câmera, tem uma matemática por trás, mas já tem implementado na internet.
    eye_x = center[0] + cam_distance * math.sin(rad_angle)
    eye_z = center[2] + cam_distance * math.cos(rad_angle)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(eye_x, eye[1], eye_z, 
              center[0], center[1], center[2], 
              up[0], up[1], up[2])

def set_camera(w, h):
    if h == 0: h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(w)/float(h), 0.05, 50.0) # Configura a projeção em perspectiva, conforme exigido pelo enunciado. Os parâmetros são: ângulo do campo de visão (60 graus), proporção (aspect ratio, w/h), plano de corte próximo (near clip) e plano de corte distante (far clip).
    glMatrixMode(GL_MODELVIEW)

def init_common():
    glClearColor(0.5, 0.5, 0.9, 1.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST) #Ativa o teste de profundidade (Z-buffer), que faz com que os triângulos mais próximos da câmera sejam desenhados na frente dos mais distantes
    glDepthFunc(GL_LESS)
    glShadeModel(GL_SMOOTH)
    
    # Habilita blending para alpha
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) # Configura como a mistura funciona. Essa configuração específica é a fórmula padrão para desenhar com transparência (alpha). É essencial para o fade-in/fade-out em display_morph
    
    setup_lighting()

# ---------- Preparação do Morph ----------
def preprocess_morph():
    global trisA_idx, vertex_map_A_to_B, trisB_idx, vertex_map_B_to_A
    
    # Mapa A -> B
    trisA_idx = objA.triangulated_faces() # pegaa lista de todas as faces como triângulos
    vertex_map_A_to_B = build_vertex_map_nearest(objA.vertices, objB.vertices) # cria o mapa de associação de A pra B
    
    # Mapa B -> A (Inverso)
    trisB_idx = objB.triangulated_faces()
    vertex_map_B_to_A = build_vertex_map_nearest(objB.vertices, objA.vertices)

# ---------- Displays ----------
def display_left():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    apply_camera()
    draw_floor()
    glColor4f(0.7, 0.7, 0.75, 1.0)
    objA.Desenha()
    glutSwapBuffers()

def display_right():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    apply_camera()
    draw_floor()
    glColor4f(0.7, 0.7, 0.75, 1.0)
    objB.Desenha()
    glutSwapBuffers()

def display_morph():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    apply_camera()
    draw_floor()

    # t em [0,1]
    tf = 0.0 if nFrames < 2 else float(curFrame) / float(nFrames-1) # é o "time factor", vamos utilizar pra calcular a opacidade do objeto em transformação 

    # --- PASSO 1: Desenha A -> B (Fade-out) ---
    
    # Habilita a escrita no depth buffer (padrão)
    glDepthMask(GL_TRUE) 
    glEnable(GL_DEPTH_TEST)
    
    # A opacidade vai de 1.0 (em t=0) para 0.0 (em t=1)
    glColor4f(0.34, 0.34, 0.34, 1.0 - tf)
    glBegin(GL_TRIANGLES)
    for (i0,i1,i2) in trisA_idx:
        # Vértices origem (A)
        a0 = objA.vertices[i0]
        a1 = objA.vertices[i1]
        a2 = objA.vertices[i2]
        # Alvos (B) por mapa A->B
        j0 = vertex_map_A_to_B[i0]
        j1 = vertex_map_A_to_B[i1]
        j2 = vertex_map_A_to_B[i2]
        b0 = objB.vertices[j0]
        b1 = objB.vertices[j1]
        b2 = objB.vertices[j2]
        
        # Interpola cada vértice individualmente: (1-t)A + tB
        # Fórmula LERP: https://pt.wikipedia.org/wiki/Interpolação_linear
        v0 = Ponto((1-tf)*a0.x + tf*b0.x, (1-tf)*a0.y + tf*b0.y, (1-tf)*a0.z + tf*b0.z)
        v1 = Ponto((1-tf)*a1.x + tf*b1.x, (1-tf)*a1.y + tf*b1.y, (1-tf)*a1.z + tf*b1.z)
        v2 = Ponto((1-tf)*a2.x + tf*b2.x, (1-tf)*a2.y + tf*b2.y, (1-tf)*a2.z + tf*b2.z)
        glVertex3f(v0.x, v0.y, v0.z)
        glVertex3f(v1.x, v1.y, v1.z)
        glVertex3f(v2.x, v2.y, v2.z)
    glEnd()

    # --- PASSO 2: Desenha B -> A (Fade-in) ---
    
    # Desabilita a *escrita* no depth buffer (mas continua testando)
    glDepthMask(GL_FALSE) 
    glDisable(GL_DEPTH_TEST) #Temos que desabilitar aqui pro objeto ser inteiramente desenhado, antes tava dando erro
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # A opacidade vai de 0.0 (em t=0) para 1.0 (em t=1)
    glColor4f(0.34, 0.34, 0.34, tf)
    glBegin(GL_TRIANGLES)
    for (j0,j1,j2) in trisB_idx:
        # Vértices origem (B)
        b0 = objB.vertices[j0]
        b1 = objB.vertices[j1]
        b2 = objB.vertices[j2]
        # Alvos (A) por mapa B->A
        i0 = vertex_map_B_to_A[j0]
        i1 = vertex_map_B_to_A[j1]
        i2 = vertex_map_B_to_A[j2]
        a0 = objA.vertices[i0]
        a1 = objA.vertices[i1]
        a2 = objA.vertices[i2]

        # A interpolação é a MESMA: (1-t)A + tB
        v0 = Ponto((1-tf)*a0.x + tf*b0.x, (1-tf)*a0.y + tf*b0.y, (1-tf)*a0.z + tf*b0.z)
        v1 = Ponto((1-tf)*a1.x + tf*b1.x, (1-tf)*a1.y + tf*b1.y, (1-tf)*a1.z + tf*b1.z)
        v2 = Ponto((1-tf)*a2.x + tf*b2.x, (1-tf)*a2.y + tf*b2.y, (1-tf)*a2.z + tf*b2.z)
        glVertex3f(v0.x, v0.y, v0.z)
        glVertex3f(v1.x, v1.y, v1.z)
        glVertex3f(v2.x, v2.y, v2.z)
    glEnd()

    # Re-habilita a escrita no depth buffer para o próximo frame
    glEnable(GL_DEPTH_TEST)
    glDepthMask(GL_TRUE) 

    glutSwapBuffers()

# ---------- Reshape / Keyboard ----------
def reshape_common(w, h):
    set_camera(w, h)

def keyboard_common(key, x, y):
    global playing, curFrame, nFrames
    if isinstance(key, bytes):
        key = key.decode('utf-8', errors='ignore')
    if key == ' ': # barra de espaço
        playing = not playing
        glutIdleFunc(idle if playing else None)
    elif key in ('r','R'):
        curFrame = 0
        glutPostRedisplay()
    elif key == '+': # aumenta o número de frames
        nFrames = max(2, nFrames + 10)
        curFrame = min(curFrame, nFrames-1)
        glutPostRedisplay()
    elif key == '-': # diminui o número de frames
        nFrames = max(2, nFrames - 10)
        curFrame = min(curFrame, nFrames-1)
        glutPostRedisplay()
    elif key == '\x1b':
        sys.exit(0)

def special_keys(key, x, y): #setinhas
    global cam_angle_y
    
    angle_step = 5.0

    if key == GLUT_KEY_LEFT:
        cam_angle_y -= angle_step
    elif key == GLUT_KEY_RIGHT:
        cam_angle_y += angle_step
    else:
        return

    glutSetWindow(winLeft)
    glutPostRedisplay()
    glutSetWindow(winRight)
    glutPostRedisplay()
    glutSetWindow(winMorph)
    glutPostRedisplay()

# ---------- Idle ----------
def idle():
    global curFrame, playing
    curFrame += 1
    if curFrame >= nFrames:
        curFrame = nFrames - 1
        playing = False
        glutIdleFunc(None)
    glutSetWindow(winMorph)
    glutPostRedisplay()

# ---------- Init / Main ----------
def init_and_load():
    global objA, objB
    objA = Objeto3D()
    objB = Objeto3D()
    objA.LoadFile("Human_Head.obj")
    objB.LoadFile("easy1.obj")
    objA.normalize_unit_and_center()
    objB.normalize_unit_and_center()
    objA.rotation = (0, 1, 0, 0)
    objB.rotation = (0, 1, 0, 0)
    preprocess_morph()

def create_windows():
    global winLeft, winRight, winMorph

    glutInitWindowSize(400, 400)
    glutInitWindowPosition(20, 200)
    winLeft = glutCreateWindow(b"Objeto A")
    init_common()
    glutDisplayFunc(display_left)
    glutReshapeFunc(reshape_common)
    glutKeyboardFunc(keyboard_common)
    glutSpecialFunc(special_keys)

    glutInitWindowSize(400, 400)
    glutInitWindowPosition(520, 200)
    winRight = glutCreateWindow(b"Objeto B")
    init_common()
    glutDisplayFunc(display_right)
    glutReshapeFunc(reshape_common)
    glutKeyboardFunc(keyboard_common)
    glutSpecialFunc(special_keys)

    glutInitWindowSize(400, 400)
    glutInitWindowPosition(1020, 200)
    winMorph = glutCreateWindow(b"Morph")
    init_common()
    glutDisplayFunc(display_morph)
    glutReshapeFunc(reshape_common)
    glutKeyboardFunc(keyboard_common)
    glutSpecialFunc(special_keys)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    init_and_load()
    create_windows()
    glutMainLoop()

if __name__ == "__main__":
    main()