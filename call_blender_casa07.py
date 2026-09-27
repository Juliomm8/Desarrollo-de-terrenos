import socket
import json

code = """
import bpy
import bmesh
import math

bm = bmesh.new()

# 1. Chasis Triangular
faces_before = set(bm.faces)
ret = bmesh.ops.create_cone(bm, cap_ends=True, segments=3, radius1=3.5, radius2=3.5, depth=5.0)

# Rotaciones: primero 90 en Z para alinear el borde plano a Y, luego 90 en X para tumbarlo.
rot_z90 = math.radians(90)
cos_z = math.cos(rot_z90)
sin_z = math.sin(rot_z90)

rot_x90 = math.radians(90)
cos_x = math.cos(rot_x90)
sin_x = math.sin(rot_x90)

for v in ret['verts']:
    x = v.co.x
    y = v.co.y
    z = v.co.z
    
    # Rot Z 90
    nx = x * cos_z - y * sin_z
    ny = x * sin_z + y * cos_z
    nz = z
    
    # Rot X 90
    fnx = nx
    fny = ny * cos_x - nz * sin_x
    fnz = ny * sin_x + nz * cos_x
    
    v.co.x = fnx
    v.co.y = fny
    v.co.z = fnz + 2.0

tube_faces = [f for f in bm.faces if f not in faces_before]
for f in tube_faces:
    f.material_index = 0 # Muro Cian

# 2. Alerones de Estabilidad
bm.faces.ensure_lookup_table()
min_z = min(v.co.z for v in bm.verts)
base_verts = [v for v in bm.verts if v.co.z < min_z + 0.1]
for v in base_verts:
    v.co.x *= 1.6 # Ensanchar la base (X local) para crear alerones

# La cara inferior (alerones base / piso exterior)
floor_face = next(f for f in tube_faces if f.normal.z < -0.9)
floor_face.material_index = 1 # Metal Oxidado

# 3. Compuerta Angulada
caps = [f for f in tube_faces if abs(f.normal.y) > 0.9]
front_face = max(caps, key=lambda f: f.calc_center_median().y)

bmesh.ops.inset_region(bm, faces=[front_face], thickness=0.5)
# La cara interior se mantiene
ex_gate = bmesh.ops.extrude_discrete_faces(bm, faces=[front_face])
gate_cap = ex_gate['faces'][0]
gate_cap.material_index = 2 # Fondo = Neon Verde

for v in gate_cap.verts:
    v.co -= gate_cap.normal * 1.2

# Encontrar el suelo de la compuerta
gate_cap_edges = set(gate_cap.edges)
cavity_walls = [f for f in bm.faces if f != gate_cap and any(e in gate_cap_edges for e in f.edges)]
for f in cavity_walls:
    if f.normal.z > 0.5: # Suelo apunta hacia arriba
        f.material_index = 1 # Metal Oxidado

# 4. Líneas de Energía
roof_faces = [f for f in tube_faces if f not in caps and f != floor_face]
for f in roof_faces:
    bmesh.ops.inset_region(bm, faces=[f], thickness=0.4)
    ex_roof = bmesh.ops.extrude_discrete_faces(bm, faces=[f])
    roof_cap = ex_roof['faces'][0]
    roof_cap.material_index = 2 # Paneles = Neon Verde
    for v in roof_cap.verts:
        v.co -= roof_cap.normal * 0.1 # Retraer ligeramente

# 5. Estructuración y Normalización
final_min_z = min(v.co.z for v in bm.verts)
for v in bm.verts:
    v.co.z -= final_min_z

me = bpy.data.meshes.new("Casa_Habitacion_07")
bm.to_mesh(me)
bm.free()

obj = bpy.data.objects.new("Casa_Habitacion_07", me)
col_name = 'Ciudad_Alien'
if col_name in bpy.data.collections:
    bpy.data.collections[col_name].objects.link(obj)
else:
    bpy.context.scene.collection.objects.link(obj)

obj.location = (25, -15, 0)

# 6. Materiales
m_cian = bpy.data.materials.get('Alien_Muro_Cian')
m_metal = bpy.data.materials.get('Alien_Metal_Oxidado')
m_neon = bpy.data.materials.get('Alien_Neon_Verde')

if m_cian: obj.data.materials.append(m_cian)
if m_metal: obj.data.materials.append(m_metal)
if m_neon: obj.data.materials.append(m_neon)

for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'

result = {"success": True, "message": "Casa_Habitacion_07 (A-Frame Cabin) generated securely using pure bmesh"}
"""

req = {
    "type": "execute",
    "code": code,
    "strict_json": True
}

payload = json.dumps(req).encode('utf-8') + b'\0'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 9876))
s.sendall(payload)

resp = bytearray()
while b'\0' not in resp:
    chunk = s.recv(4096)
    if not chunk:
        break
    resp.extend(chunk)

s.close()
resp_str = resp.split(b'\0')[0].decode('utf-8')
print("Response:", resp_str)
