import socket
import json

code = """
import bpy
import bmesh

bm = bmesh.new()

# 1. Platform (Z=0.2, radius=2, depth=0.4)
ret1 = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=2.0, radius2=2.0, depth=0.4)
platform_verts = ret1['verts']
bmesh.ops.translate(bm, vec=(0, 0, 0.2), verts=platform_verts)
for f in bm.faces:
    if f.material_index == -1 or f.material_index == 0:
        f.material_index = 1 # Metal

# 2. Beam (Z=2.4, radius=0.3, depth=2.5)
faces_before = set(bm.faces)
ret2 = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.3, radius2=0.3, depth=2.5)
beam_verts = ret2['verts']
bmesh.ops.translate(bm, vec=(0, 0, 2.4), verts=beam_verts)
for f in bm.faces:
    if f not in faces_before:
        f.material_index = 2 # Neon

# 3. Floating Capsule (Z=4.5, radius=2.5)
faces_before = set(bm.faces)
ret3 = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=2.5)
capsule_verts = ret3['verts']
bmesh.ops.translate(bm, vec=(0, 0, 4.5), verts=capsule_verts)
capsule_faces = [f for f in bm.faces if f not in faces_before]
for f in capsule_faces:
    f.material_index = 0 # Cian

# 4. Equatorial Windows
bm.faces.ensure_lookup_table()
window_faces = [f for f in capsule_faces if abs(f.normal.z) < 0.3]

for f in window_faces:
    res = bmesh.ops.inset_region(bm, faces=[f], thickness=0.15)
    for frame_f in res.get('faces', []):
        frame_f.material_index = 1 # Frame is metal
        
    f.material_index = 1 # Prepare for cavity walls
    ex = bmesh.ops.extrude_discrete_faces(bm, faces=[f])
    glass_f = ex['faces'][0]
    glass_f.material_index = 2 # Glass is neon
    
    bmesh.ops.translate(bm, vec=-0.2 * glass_f.normal, verts=glass_f.verts)

# 5. Z=0 Structuring
min_z = min(v.co.z for v in bm.verts)
bmesh.ops.translate(bm, vec=(0, 0, -min_z), verts=bm.verts)

# 6. Object Creation
me = bpy.data.meshes.new("Casa_Habitacion_03")
bm.to_mesh(me)
bm.free()

obj = bpy.data.objects.new("Casa_Habitacion_03", me)
collection_name = 'Ciudad_Alien'
if collection_name in bpy.data.collections:
    bpy.data.collections[collection_name].objects.link(obj)
else:
    bpy.context.scene.collection.objects.link(obj)

# Anchor precisely
obj.location = (-15, -25, 0)

# 7. Materials
m_cian = bpy.data.materials.get('Alien_Muro_Cian')
m_metal = bpy.data.materials.get('Alien_Metal_Oxidado')
m_neon = bpy.data.materials.get('Alien_Neon_Verde')

if m_cian: obj.data.materials.append(m_cian) # index 0
if m_metal: obj.data.materials.append(m_metal) # index 1
if m_neon: obj.data.materials.append(m_neon) # index 2

# Update Viewport
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'

result = {"success": True, "message": "Casa_Habitacion_03 (Anti-gravity) generated securely using pure bmesh"}
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
