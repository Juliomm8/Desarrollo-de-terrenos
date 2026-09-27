import socket
import json

code = """
import bpy
import bmesh
import math

bm = bmesh.new()

rot_z225 = math.radians(22.5)
cos_z = math.cos(rot_z225)
sin_z = math.sin(rot_z225)

rot_y90 = math.radians(90)
cos_y = math.cos(rot_y90)
sin_y = math.sin(rot_y90)

# 1. Cuerpo Tubular (Z=2.5, radius=2, depth=6)
faces_before = set(bm.faces)
ret = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=2.0, radius2=2.0, depth=6.0)

for v in ret['verts']:
    x = v.co.x
    y = v.co.y
    z = v.co.z
    
    # 22.5 grados en Z para alinear caras
    nx = x * cos_z - y * sin_z
    ny = x * sin_z + y * cos_z
    nz = z
    
    # 90 grados en Y para acostarlo horizontalmente
    fnx = nx * cos_y + nz * sin_y
    fny = ny
    fnz = -nx * sin_y + nz * cos_y
    
    v.co.x = fnx
    v.co.y = fny
    v.co.z = fnz + 2.5 # Z centro = 2.5

tube_faces = [f for f in bm.faces if f not in faces_before]
for f in tube_faces:
    f.material_index = 0 # Muro

bm.faces.ensure_lookup_table()

# 2. Puntas Aerodinámicas
caps = [f for f in tube_faces if abs(f.normal.x) > 0.9]
for f in caps:
    c = f.calc_center_median()
    for v in f.verts:
        v.co.y = c.y + (v.co.y - c.y) * 0.5
        v.co.z = c.z + (v.co.z - c.z) * 0.5
        
    ex_cap = bmesh.ops.extrude_discrete_faces(bm, faces=[f])
    new_cap = ex_cap['faces'][0]
    for v in new_cap.verts:
        v.co += new_cap.normal * 0.8 # Extrusion suave hacia afuera

# 3. Cunas de Soporte
# Posicionadas en X=-2.5 y X=2.5, desde Z=0 hasta Z=1.2 (centro Z=0.6)
cradle_positions = [(-2.5, 0, 0.6), (2.5, 0, 0.6)]
for pos in cradle_positions:
    faces_before = set(bm.faces)
    ret_cube = bmesh.ops.create_cube(bm, size=1.0)
    for v in ret_cube['verts']:
        v.co.x *= 0.8
        v.co.y *= 2.2
        v.co.z *= 1.2
        v.co.x += pos[0]
        v.co.y += pos[1]
        v.co.z += pos[2]
        
    cube_faces = [f for f in bm.faces if f not in faces_before]
    for f in cube_faces:
        f.material_index = 1 # Metal Oxidado

# 4. Tragaluces de Laboratorio
bm.faces.ensure_lookup_table()
sky_faces = [f for f in bm.faces if f.normal.z > 0.9 and f.calc_center_median().z > 3.0]

for f in sky_faces:
    res = bmesh.ops.inset_region(bm, faces=[f], thickness=0.2)
    # Los bordes generados retienen el index 0
    
    ex_sky = bmesh.ops.extrude_discrete_faces(bm, faces=[f])
    sky_cap = ex_sky['faces'][0]
    sky_cap.material_index = 2 # Neon Rosa / Cristal
    
    for v in sky_cap.verts:
        v.co -= sky_cap.normal * 0.3 # Hacia el interior

# 5. Estructuración y Normalización
min_z = min(v.co.z for v in bm.verts)
for v in bm.verts:
    v.co.z -= min_z

me = bpy.data.meshes.new("Casa_Habitacion_06")
bm.to_mesh(me)
bm.free()

obj = bpy.data.objects.new("Casa_Habitacion_06", me)
col_name = 'Ciudad_Alien'
if col_name in bpy.data.collections:
    bpy.data.collections[col_name].objects.link(obj)
else:
    bpy.context.scene.collection.objects.link(obj)

obj.location = (15, -25, 0)

# 6. Materiales
m_muro = bpy.data.materials.get('Alien_Muro_Mostaza') or bpy.data.materials.get('Alien_Muro_Cian')
m_metal = bpy.data.materials.get('Alien_Metal_Oxidado')
m_neon = bpy.data.materials.get('Alien_Neon_Rosa') or bpy.data.materials.get('Alien_Cristal')

if m_muro: obj.data.materials.append(m_muro)
if m_metal: obj.data.materials.append(m_metal)
if m_neon: obj.data.materials.append(m_neon)

for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'

result = {"success": True, "message": "Casa_Habitacion_06 (Tubular Module) generated securely using pure bmesh"}
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
