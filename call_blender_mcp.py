import socket
import json

code = """
import bpy
import bmesh
from mathutils import Vector

# Limpieza Inicial
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Base del Edificio
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
base_obj = bpy.context.active_object
base_obj.scale = (3, 2, 1)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Techo Escalonado
bpy.ops.object.mode_set(mode='EDIT')
mesh = bmesh.from_edit_mesh(base_obj.data)
mesh.faces.ensure_lookup_table()
top_face = None
for f in mesh.faces:
    if f.normal.z > 0.9:
        top_face = f
        break

if top_face:
    top_face.select_set(True)
    bmesh.ops.inset_region(mesh, faces=[top_face], thickness=0.5)
    
    mesh.faces.ensure_lookup_table()
    new_top_face = None
    for f in mesh.faces:
        if f.select and f.normal.z > 0.9:
            new_top_face = f
            break
            
    if new_top_face:
        extruded = bmesh.ops.extrude_discrete_faces(mesh, faces=[new_top_face])
        ext_faces = extruded['faces']
        bmesh.ops.translate(mesh, vec=(0, 0, 1.0), verts=[v for f in ext_faces for v in f.verts])

bmesh.update_edit_mesh(base_obj.data)
bpy.ops.object.mode_set(mode='OBJECT')

# Letrero Flotante
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 4.0))
sign_obj = bpy.context.active_object
sign_obj.scale = (2, 0.2, 0.5)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Antena de Comunicaciones
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.2, depth=1.0, location=(-2.0, -1.0, 3.5))
antenna_obj = bpy.context.active_object
bpy.ops.object.mode_set(mode='EDIT')
mesh_ant = bmesh.from_edit_mesh(antenna_obj.data)
mesh_ant.faces.ensure_lookup_table()
top_face_ant = next(f for f in mesh_ant.faces if f.normal.z > 0.9)
top_face_ant.select_set(True)

for i in range(3):
    extruded = bmesh.ops.extrude_discrete_faces(mesh_ant, faces=[top_face_ant])
    top_face_ant = extruded['faces'][0]
    bmesh.ops.translate(mesh_ant, vec=(0, 0, 0.5), verts=top_face_ant.verts)
    bmesh.ops.scale(mesh_ant, vec=(0.5, 0.5, 0.5), verts=top_face_ant.verts)

bmesh.update_edit_mesh(antenna_obj.data)
bpy.ops.object.mode_set(mode='OBJECT')

# Estructuración
bpy.ops.object.select_all(action='DESELECT')
base_obj.select_set(True)
sign_obj.select_set(True)
antenna_obj.select_set(True)
bpy.context.view_layer.objects.active = base_obj

bpy.ops.object.join()
final_obj = bpy.context.active_object
final_obj.name = 'CosmicDiner_Base'

# Asegurar punto de origen en Z=0
cursor_loc = bpy.context.scene.cursor.location.copy()
bpy.context.scene.cursor.location = (0, 0, 0)

min_z = min((final_obj.matrix_world @ v.co).z for v in final_obj.data.vertices)

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.transform.translate(value=(0, 0, -min_z))
bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.context.scene.cursor.location = cursor_loc

result = {"success": True, "object_name": final_obj.name, "min_z": 0.0}
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
