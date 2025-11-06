from Ponto import Ponto, dist

# Recebe os vértices de um triângulo, separa os tr~es pontos em a, b, c
# e calcula a média aritmética de cada ponto,
# e reotrna um novo Ponto com as médias calculadas, que é o centroide
def tri_centroid(tri_pts):
    a,b,c = tri_pts
    return Ponto( (a.x+b.x+c.x)/3.0, (a.y+b.y+c.y)/3.0, (a.z+b.z+c.z)/3.0 )

def build_vertex_map_nearest(A_vertices, B_vertices):
    """
    Para cada vértice i de A, encontra o índice do vértice j de B mais próximo.
    Retorna lista mapAtoB de mesmo tamanho de A.vertices: mapAtoB[i] = j
    Muitos-para-um é permitido (isso garante que NENHUM vértice fique sem alvo).
    """
    mapAtoB = []
    for va in A_vertices:
        best_j, best_d = 0, 1e18 # O best J é resetado pra zero, porque ainda não achamos o melhor, e o best D que é a melhor distância vira um número muito grande, porque daí quase qualquer distância já vai ser melhor que ele.
        for j, vb in enumerate(B_vertices):
            d = dist(va, vb)
            if d < best_d:
                best_d, best_j = d, j
        mapAtoB.append(best_j)
    return mapAtoB # tem o tamanho da lista de vértices A, cada elemento nela é um índice pra lista de vértices de B