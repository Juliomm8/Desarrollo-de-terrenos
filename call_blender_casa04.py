import socket
import json

code = """
import bpy
import bmesh
import math

bm = bmesh.new()

# 1. Primer Nivel (Base Inclinada)
ret = bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=3.5, radius2=3.5, depth=1.5)
verts = ret['verts']

cos45 = math.cos(math.radians(45))
sin45 = math.sin(math.radians(45))

for v in verts:
    x = v.co.x
    y = v.co.y
    v.co.x = x * cos45 - y * sin45
    v.co.y = x * sin45 + y * cos45
    v.co.z += 0.75 # Translate up so bottom is at Z=0

bm.faces.ensure_lookup_table()
top_face = next(f for f in bm.faces if f.normal.z > 0.9)

for v in top_face.verts:
    v.co.x *= 0.6
    v.co.y *= 0.6

# Asignación default de materiales (0 = Muro)
for f in bm.faces:
    f.material_index = 0

# 2. Segundo Nivel
ex = bmesh.ops.extrude_discrete_faces(bm, faces=[top_face])
top_cap = ex['faces'][0]

for v in top_cap.verts:
    v.co.z += 1.2
    v.co.x *= 0.5
    v.co.y *= 0.5

top_cap.material_index = 1 # 1 = Metal Oxidado

# 3. Puerta Blindada
bm.faces.ensure_lookup_table()
# Caras inclinadas del nivel 1 tienen centro en Z ~ 0.75
inclined_faces = [f for f in bm.faces if 0.1 < f.calc_center_median().z < 1.4 and abs(f.normal.z) < 0.9]

door_face = max(inclined_faces, key=lambda f: f.calc_center_median().y)

bmesh.ops.inset_region(bm, faces=[door_face], thickness=0.4)
door_face.material_index = 1
ex_door = bmesh.ops.extrude_discrete_faces(bm, faces=[door_face])
door_cap = ex_door['faces'][0]
door_cap.material_index = 1

for v in door_cap.verts:
    v.co -= door_cap.normal * 0.6

# 4. Ranuras Panorámicas
remaining_faces = [f for f in inclined_faces if f != door_face]
for f in remaining_faces:
    bmesh.ops.inset_region(bm, faces=[f], thickness=0.3)
    
    c = f.calc_center_median()
    for v in f.verts:
        v.co.z = c.z + (v.co.z - c.z) * 0.1
        
    f.material_index = 1
    
    ex_slit = bmesh.ops.extrude_discrete_faces(bm, faces=[f])
    slit_cap = ex_slit['faces'][0]
    slit_cap.material_index = 2 # 2 = Neon
    
    for v in slit_cap.verts:
        v.co -= slit_cap.normal * 0.2

# 5. Núcleo de Energía Superior
faces_before = set(bm.faces)
ret_ico = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.6)
for v in ret_ico['verts']:
    # Techo=2.7, Altura flotante=0.5, Radio=0.6 -> Z_centro = 3.8
    v.co.z += 3.8

ico_faces = [f for f in bm.faces if f not in faces_before]
for f in ico_faces:
    f.material_index = 2

# 6. Estructuración
min_z = min(v.co.z for v in bm.verts)
for v in bm.verts:
    v.co.z -= min_z

me = bpy.data.meshes.new("Casa_Habitacion_04")
bm.to_mesh(me)
bm.free()

obj = bpy.data.objects.new("Casa_Habitacion_04", me)
col_name = 'Ciudad_Alien'
if col_name in bpy.data.collections:
    bpy.data.collections[col_name].objects.link(obj)
else:
    bpy.context.scene.collection.objects.link(obj)

obj.location = (-5, -25, 0)

# 7. Materiales
m_muro = bpy.data.materials.get('Alien_Muro_Mostaza') or bpy.data.materials.get('Alien_Muro_Cian')
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

result = {"success": True, "message": "Casa_Habitacion_04 (Bunker Zigurat) generated securely using pure bmesh"}
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
