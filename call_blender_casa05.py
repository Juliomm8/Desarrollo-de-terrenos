import socket
import json

code = """
import bpy
import bmesh
import math

bm = bmesh.new()

# Rotate 22.5 degrees to align octagonal faces with axes
rot_angle = math.radians(22.5)
cos_r = math.cos(rot_angle)
sin_r = math.sin(rot_angle)

# 1. Núcleo de la Torre
faces_before = set(bm.faces)
ret1 = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=1.5, radius2=1.5, depth=4)
for v in ret1['verts']:
    x = v.co.x
    y = v.co.y
    v.co.x = x * cos_r - y * sin_r
    v.co.y = x * sin_r + y * cos_r
    v.co.z += 2.0

tower_faces = [f for f in bm.faces if f not in faces_before]
for f in tower_faces:
    f.material_index = 0 # Cian

# 2. Anillo de Observación
faces_before = set(bm.faces)
ret2 = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=3.5, radius2=3.5, depth=0.5)
for v in ret2['verts']:
    x = v.co.x
    y = v.co.y
    v.co.x = x * cos_r - y * sin_r
    v.co.y = x * sin_r + y * cos_r
    v.co.z += 3.2

ring_faces = [f for f in bm.faces if f not in faces_before]
for f in ring_faces:
    f.material_index = 1 # Metal (Bordes)

# 3. Ventanal de 360 Grados
bm.faces.ensure_lookup_table()
ring_sides = [f for f in ring_faces if abs(f.normal.z) < 0.5]

for f in ring_sides:
    res = bmesh.ops.inset_region(bm, faces=[f], thickness=0.1)
    for frame_f in res.get('faces', []):
        frame_f.material_index = 1
        
    f.material_index = 1 # Cavity walls
    ex_win = bmesh.ops.extrude_discrete_faces(bm, faces=[f])
    win_cap = ex_win['faces'][0]
    win_cap.material_index = 2 # Neon verde
    for v in win_cap.verts:
        v.co -= win_cap.normal * 0.2

# 4. Cúpula de Radar
faces_before = set(bm.faces)
ret3 = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.4)
for v in ret3['verts']:
    v.co.z *= 0.5
    v.co.z += 4.2

dome_faces = [f for f in bm.faces if f not in faces_before]
for f in dome_faces:
    f.material_index = 0 # Cian

# 5. Compuerta Base
bm.faces.ensure_lookup_table()
tower_sides = [f for f in tower_faces if abs(f.normal.z) < 0.5]
door_face = max(tower_sides, key=lambda f: f.calc_center_median().y)

bmesh.ops.inset_region(bm, faces=[door_face], thickness=0.3)
door_face.material_index = 1
ex_door = bmesh.ops.extrude_discrete_faces(bm, faces=[door_face])
door_cap = ex_door['faces'][0]
door_cap.material_index = 1

for v in door_cap.verts:
    v.co -= door_cap.normal * 0.6

# 6. Estructuración y Normalización
min_z = min(v.co.z for v in bm.verts)
for v in bm.verts:
    v.co.z -= min_z

me = bpy.data.meshes.new("Casa_Habitacion_05")
bm.to_mesh(me)
bm.free()

obj = bpy.data.objects.new("Casa_Habitacion_05", me)
col_name = 'Ciudad_Alien'
if col_name in bpy.data.collections:
    bpy.data.collections[col_name].objects.link(obj)
else:
    bpy.context.scene.collection.objects.link(obj)

obj.location = (5, -25, 0)

# 7. Materiales
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

result = {"success": True, "message": "Casa_Habitacion_05 (Observatory) generated securely using pure bmesh"}
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
