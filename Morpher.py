from Ponto import Ponto, dist

def tri_centroid(tri_pts):
    a,b,c = tri_pts
    return Ponto( (a.x+b.x+c.x)/3.0, (a.y+b.y+c.y)/3.0, (a.z+b.z+c.z)/3.0 )

def pair_faces_by_centroid(trisA_pts, trisB_pts):
    # Mantido para referência/depuração (não usado mais no render)
    centB = [tri_centroid(t) for t in trisB_pts]
    match = []
    for ta in trisA_pts:
        ca = tri_centroid(ta)
        best_j, best_d = 0, 1e18
        for j, cb in enumerate(centB):
            d = dist(ca, cb)
            if d < best_d:
                best_d, best_j = d, j
        match.append(best_j)
    return match

def interpolate_triangles(triA_pts, triB_pts, t: float):
    out = []
    for a, b in zip(triA_pts, triB_pts):
        out.append( Ponto(
            (1.0-t)*a.x + t*b.x,
            (1.0-t)*a.y + t*b.y,
            (1.0-t)*a.z + t*b.z
        ))
    return out

def build_vertex_map_nearest(A_vertices, B_vertices):
    """
    Para cada vértice 'i' de A, encontra o índice do vértice 'j' de B mais próximo.
    Retorna lista 'mapAtoB' de mesmo tamanho de A.vertices: mapAtoB[i] = j
    Muitos-para-um é permitido (isso garante que NENHUM vértice fique sem alvo).
    """
    mapAtoB = []
    for va in A_vertices:
        best_j, best_d = 0, 1e18
        for j, vb in enumerate(B_vertices):
            d = dist(va, vb)
            if d < best_d:
                best_d, best_j = d, j
        mapAtoB.append(best_j)
    return mapAtoB