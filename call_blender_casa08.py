import socket
import json

code = """
import bpy
import bmesh
from mathutils import Vector

bm = bmesh.new()

# 1. Nodo Principal
faces_before = set(bm.faces)
ret1 = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=2.5, radius2=2.5, depth=4.5)
for v in ret1['verts']:
    v.co.z += 2.25
node1_faces = [f for f in bm.faces if f not in faces_before]

# 2. Nodo Secundario
faces_before = set(bm.faces)
ret2 = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=1.8, radius2=1.8, depth=3.0)
for v in ret2['verts']:
    v.co.x += 4.0
    v.co.z += 1.5
node2_faces = [f for f in bm.faces if f not in faces_before]

# 3. Nodo Terciario
faces_before = set(bm.faces)
ret3 = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=1.5, radius2=1.5, depth=2.0)
for v in ret3['verts']:
    v.co.x -= 2.0
    v.co.y -= 3.0
    v.co.z += 1.0
node3_faces = [f for f in bm.faces if f not in faces_before]

for f in bm.faces:
    f.material_index = 0 # Muro Mostaza

bm.faces.ensure_lookup_table()

# 4. Piscinas de Energía (Techos)
bm.faces.ensure_lookup_table()
top_faces = [f for f in bm.faces if f.normal.z > 0.9]

res = bmesh.ops.inset_region(bm, faces=top_faces, thickness=0.4)
for frame_f in res.get('faces', []):
    frame_f.material_index = 1 # Metal Oxidado (bordes)

ex_top = bmesh.ops.extrude_discrete_faces(bm, faces=top_faces)
for pool_cap in ex_top['faces']:
    pool_cap.material_index = 2 # Neon Rosa
    for v in pool_cap.verts:
        v.co -= pool_cap.normal * 0.5 # Extruir hacia adentro

# 5. Compuerta del Nodo Principal
bm.faces.ensure_lookup_table()
# Nodo 1 está centrado en X=0, Y=0. Sus caras laterales están a ~2.16 de distancia.
# Nodo 2 está en X=4 y Nodo 3 en Y=-3, por lo que sus caras están más lejos de (0,0).
node1_sides = [f for f in bm.faces if abs(f.normal.z) < 0.5 and f.calc_center_median().xy.length < 2.3]
door_face = min(node1_sides, key=lambda f: f.calc_center_median().y)

res_door = bmesh.ops.inset_region(bm, faces=[door_face], thickness=0.3)
ex_door = bmesh.ops.extrude_discrete_faces(bm, faces=[door_face])
door_cap = ex_door['faces'][0]
door_cap.material_index = 2 # Neon Rosa (fondo)

for v in door_cap.verts:
    v.co -= door_cap.normal * 0.8

gate_edges = set(door_cap.edges)
cavity_walls = [f for f in bm.faces if f != door_cap and any(e in gate_edges for e in f.edges)]
for f in cavity_walls:
    if f.normal.z > 0.5:
        f.material_index = 1 # Suelo interior = Metal
    else:
        f.material_index = 0 # Paredes = Muro

# 6. Estructuración y Normalización
min_z = min(v.co.z for v in bm.verts)
for v in bm.verts:
    v.co.z -= min_z

me = bpy.data.meshes.new("Casa_Habitacion_08")
bm.to_mesh(me)
bm.free()

obj = bpy.data.objects.new("Casa_Habitacion_08", me)
col_name = 'Ciudad_Alien'
if col_name in bpy.data.collections:
    bpy.data.collections[col_name].objects.link(obj)
else:
    bpy.context.scene.collection.objects.link(obj)

obj.location = (35, -15, 0)

# 7. Materiales
m_muro = bpy.data.materials.get('Alien_Muro_Mostaza')
m_metal = bpy.data.materials.get('Alien_Metal_Oxidado')
m_neon = bpy.data.materials.get('Alien_Neon_Rosa')

if m_muro: obj.data.materials.append(m_muro)
if m_metal: obj.data.materials.append(m_metal)
if m_neon: obj.data.materials.append(m_neon)

for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'

result = {"success": True, "message": "Casa_Habitacion_08 (Hex Cluster) generated securely using pure bmesh"}
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
