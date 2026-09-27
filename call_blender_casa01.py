import socket
import json

code = """
import bpy
import bmesh
from mathutils import Vector

if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
    
bpy.ops.object.select_all(action='DESELECT')

# 1. Base capsule
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=2.5, depth=3.0, location=(-15, -15, 1.5))
capsule = bpy.context.active_object

# 2. Vaulted roof
bpy.ops.object.mode_set(mode='EDIT')
mesh = bmesh.from_edit_mesh(capsule.data)
mesh.faces.ensure_lookup_table()
top_face = next(f for f in mesh.faces if f.normal.z > 0.9)
top_face.select_set(True)

bmesh.ops.inset_region(mesh, faces=[top_face], thickness=0.4)
mesh.faces.ensure_lookup_table()
new_top_face = next(f for f in mesh.faces if f.select and f.normal.z > 0.9)

extruded = bmesh.ops.extrude_discrete_faces(mesh, faces=[new_top_face])
ext_face = extruded['faces'][0]
bmesh.ops.translate(mesh, vec=(0,0,1.2), verts=ext_face.verts)
bmesh.ops.scale(mesh, vec=(0.2, 0.2, 1.0), verts=ext_face.verts)

bmesh.update_edit_mesh(capsule.data)
bpy.ops.object.mode_set(mode='OBJECT')

# 3. Compuerta de Entrada
bpy.ops.mesh.primitive_cube_add(size=2, location=(-15, -12.5, 1.2))
door = bpy.context.active_object
door.scale = (1.0, 1.5, 1.2)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

bpy.ops.object.mode_set(mode='EDIT')
mesh = bmesh.from_edit_mesh(door.data)
mesh.faces.ensure_lookup_table()
front_face = next(f for f in mesh.faces if f.normal.y > 0.9)
front_face.select_set(True)
bmesh.ops.inset_region(mesh, faces=[front_face], thickness=0.2)

mesh.faces.ensure_lookup_table()
inner_face = next(f for f in mesh.faces if f.select and f.normal.y > 0.9)
extruded = bmesh.ops.extrude_discrete_faces(mesh, faces=[inner_face])
inner_ext = extruded['faces'][0]
bmesh.ops.translate(mesh, vec=(0, -0.5, 0), verts=inner_ext.verts)

bmesh.update_edit_mesh(door.data)
bpy.ops.object.mode_set(mode='OBJECT')

# 4. Ventanas Panorámicas (+X)
bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=0.3, location=(-12.5, -15, 1.5))
win1 = bpy.context.active_object
win1.rotation_euler[1] = 1.5708
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

bpy.ops.object.mode_set(mode='EDIT')
mesh = bmesh.from_edit_mesh(win1.data)
mesh.faces.ensure_lookup_table()
ext_face = next(f for f in mesh.faces if f.normal.x > 0.9)
ext_face.select_set(True)
bmesh.ops.inset_region(mesh, faces=[ext_face], thickness=0.1)
mesh.faces.ensure_lookup_table()
inner_win = next(f for f in mesh.faces if f.select and f.normal.x > 0.9)
extruded = bmesh.ops.extrude_discrete_faces(mesh, faces=[inner_win])
ext_inner = extruded['faces'][0]
bmesh.ops.translate(mesh, vec=(-0.1, 0, 0), verts=ext_inner.verts)
bmesh.update_edit_mesh(win1.data)
bpy.ops.object.mode_set(mode='OBJECT')

# 4b. Ventanas Panorámicas (-X)
bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=0.3, location=(-17.5, -15, 1.5))
win2 = bpy.context.active_object
win2.rotation_euler[1] = 1.5708
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

bpy.ops.object.mode_set(mode='EDIT')
mesh = bmesh.from_edit_mesh(win2.data)
mesh.faces.ensure_lookup_table()
ext_face = next(f for f in mesh.faces if f.normal.x < -0.9)
ext_face.select_set(True)
bmesh.ops.inset_region(mesh, faces=[ext_face], thickness=0.1)
mesh.faces.ensure_lookup_table()
inner_win = next(f for f in mesh.faces if f.select and f.normal.x < -0.9)
extruded = bmesh.ops.extrude_discrete_faces(mesh, faces=[inner_win])
ext_inner = extruded['faces'][0]
bmesh.ops.translate(mesh, vec=(0.1, 0, 0), verts=ext_inner.verts)
bmesh.update_edit_mesh(win2.data)
bpy.ops.object.mode_set(mode='OBJECT')

# 5. Structuring
bpy.ops.object.select_all(action='DESELECT')
capsule.select_set(True)
door.select_set(True)
win1.select_set(True)
win2.select_set(True)
bpy.context.view_layer.objects.active = capsule
bpy.ops.object.join()
final_obj = bpy.context.active_object
final_obj.name = 'Casa_Habitacion_01'

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

# 6. Materials
m_cian = bpy.data.materials.get('Alien_Muro_Cian')
m_metal = bpy.data.materials.get('Alien_Metal_Oxidado')
m_neon = bpy.data.materials.get('Alien_Neon_Verde')

final_obj.data.materials.clear()
final_obj.data.materials.append(m_cian)
final_obj.data.materials.append(m_metal)
final_obj.data.materials.append(m_neon)

bpy.ops.object.mode_set(mode='EDIT')
mesh = bmesh.from_edit_mesh(final_obj.data)
mesh.faces.ensure_lookup_table()

for f in mesh.faces:
    center = f.calc_center_median()
    normal = f.normal
    
    f.material_index = 0
    
    if center.y > -13.8:
        f.material_index = 1
        if normal.y > 0.9 and center.y < -11.2:
            f.material_index = 2
            
    if center.x > -13.0:
        f.material_index = 1
        if normal.x > 0.9 and center.x < -12.4:
            f.material_index = 2
            
    if center.x < -17.0:
        f.material_index = 1
        if normal.x < -0.9 and center.x > -17.6:
            f.material_index = 2

bmesh.update_edit_mesh(final_obj.data)
bpy.ops.object.mode_set(mode='OBJECT')

# Viewport update
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'

result = {"success": True, "message": "Casa Habitacion 01 created"}
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
