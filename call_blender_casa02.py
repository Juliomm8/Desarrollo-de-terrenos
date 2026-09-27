import socket
import json

code = """
import bpy
import bmesh
import math
from mathutils import Vector

if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
    
bpy.ops.object.select_all(action='DESELECT')

# 1. Platform
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=3, depth=0.5, location=(-25, -15, 3.0))
platform = bpy.context.active_object

# 2. Pillars
pillars = []
for angle in [0, 2*math.pi/3, 4*math.pi/3]:
    px = -25 + 2.5 * math.cos(angle)
    py = -15 + 2.5 * math.sin(angle)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.2, depth=2.75, location=(px, py, 1.375))
    pillars.append(bpy.context.active_object)

# 3. Main Body
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=2.5, depth=2.5, location=(-25, -15, 4.5))
body = bpy.context.active_object

bpy.ops.object.mode_set(mode='EDIT')
mesh = bmesh.from_edit_mesh(body.data)
mesh.faces.ensure_lookup_table()

# Inverted Chassis
top_face = next(f for f in mesh.faces if f.normal.z > 0.9)
top_face.select_set(True)
bmesh.ops.scale(mesh, vec=(1.4, 1.4, 1.0), verts=top_face.verts)

extruded = bmesh.ops.extrude_discrete_faces(mesh, faces=[top_face])
ext_top = extruded['faces'][0]
bmesh.ops.translate(mesh, vec=(0,0,0.5), verts=ext_top.verts)

mesh.faces.ensure_lookup_table()

# Observation Window
front_face = max([f for f in mesh.faces if abs(f.normal.z) < 0.5], key=lambda f: f.normal.y)
front_face.select_set(True)

bmesh.ops.inset_region(mesh, faces=[front_face], thickness=0.3)
mesh.faces.ensure_lookup_table()
inner_1 = max([f for f in mesh.faces if f.select and abs(f.normal.z) < 0.5], key=lambda f: f.normal.y)

extruded_out = bmesh.ops.extrude_discrete_faces(mesh, faces=[inner_1])
ext_out = extruded_out['faces'][0]
bmesh.ops.translate(mesh, vec=(0, 0.2, 0), verts=ext_out.verts)

bmesh.ops.inset_region(mesh, faces=[ext_out], thickness=0.1)
mesh.faces.ensure_lookup_table()
inner_2 = max([f for f in mesh.faces if f.select and abs(f.normal.z) < 0.5], key=lambda f: f.normal.y)

extruded_in = bmesh.ops.extrude_discrete_faces(mesh, faces=[inner_2])
ext_in = extruded_in['faces'][0]
bmesh.ops.translate(mesh, vec=(0, -0.1, 0), verts=ext_in.verts)

bmesh.update_edit_mesh(body.data)
bpy.ops.object.mode_set(mode='OBJECT')

# 4. Structuring
bpy.ops.object.select_all(action='DESELECT')
platform.select_set(True)
for p in pillars:
    p.select_set(True)
body.select_set(True)

bpy.context.view_layer.objects.active = body
bpy.ops.object.join()
final_obj = bpy.context.active_object
final_obj.name = 'Casa_Habitacion_02'

bpy.context.view_layer.update()
min_z = min((final_obj.matrix_world @ v.co).z for v in final_obj.data.vertices)

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.transform.translate(value=(0, 0, -min_z))
bpy.ops.object.mode_set(mode='OBJECT')

loc = final_obj.location.copy()
loc.z = 0
cursor_loc = bpy.context.scene.cursor.location.copy()
bpy.context.scene.cursor.location = loc
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.context.scene.cursor.location = cursor_loc

# 5. Materials
m_mostaza = bpy.data.materials.get('Alien_Muro_Mostaza')
m_metal = bpy.data.materials.get('Alien_Metal_Oxidado')
m_neon = bpy.data.materials.get('Alien_Neon_Rosa')

final_obj.data.materials.clear()
final_obj.data.materials.append(m_mostaza)
final_obj.data.materials.append(m_metal)
final_obj.data.materials.append(m_neon)

bpy.ops.object.mode_set(mode='EDIT')
mesh = bmesh.from_edit_mesh(final_obj.data)
mesh.faces.ensure_lookup_table()

for f in mesh.faces:
    center = f.calc_center_median()
    normal = f.normal
    
    f.material_index = 0 # Default Mostaza
    
    if center.z < 2.8:
        f.material_index = 1 # Pillars
        
max_y = max((f.calc_center_median().y for f in mesh.faces if abs(f.normal.z) < 0.5), default=0)
max_normal_y = max((f.normal.y for f in mesh.faces if abs(f.normal.z) < 0.5), default=0)

for f in mesh.faces:
    center = f.calc_center_median()
    if center.z >= 2.8 and center.y > max_y - 0.4:
        # Window area
        if abs(f.normal.y - max_normal_y) < 0.01 and center.y < max_y - 0.05:
            f.material_index = 2 # Glass
        else:
            f.material_index = 1 # Frame

bmesh.update_edit_mesh(final_obj.data)
bpy.ops.object.mode_set(mode='OBJECT')

for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'

result = {"success": True, "message": "Casa Habitacion 02 created"}
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
