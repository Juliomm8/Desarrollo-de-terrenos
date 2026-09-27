import socket
import json

code = """
import bpy
import bmesh
from mathutils import Vector

if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

collection_name = 'Ciudad_Alien'
if collection_name not in bpy.data.collections:
    new_col = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(new_col)
else:
    new_col = bpy.data.collections[collection_name]

# Find layer collection recursively to set as active
def set_active_collection(col_name):
    def traverse(layer_col):
        if layer_col.name == col_name:
            return layer_col
        for child in layer_col.children:
            res = traverse(child)
            if res:
                return res
        return None
    
    target = traverse(bpy.context.view_layer.layer_collection)
    if target:
        bpy.context.view_layer.active_layer_collection = target

set_active_collection(collection_name)

x_coords = [-10, 0, 10]
y_coords = [10, 20, 30]
locations = [(x, y, 0) for x in x_coords for y in y_coords]

mats = []
for m in ['Alien_Muro_Cian', 'Alien_Muro_Mostaza', 'Alien_Metal_Oxidado']:
    mat = bpy.data.materials.get(m)
    if mat: mats.append(mat)

def finalize_object(obj, loc, mat):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    obj.location = loc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    bpy.context.view_layer.update()
    min_z = min((obj.matrix_world @ v.co).z for v in obj.data.vertices)
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.translate(value=(0, 0, -min_z))
    bpy.ops.object.mode_set(mode='OBJECT')
    
    cursor_loc = bpy.context.scene.cursor.location.copy()
    bpy.context.scene.cursor.location = loc
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.context.scene.cursor.location = cursor_loc
    
    if mat:
        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat
            
    bpy.ops.object.select_all(action='DESELECT')

# Casa 1
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=2, depth=1, location=(0,0,0))
casa1 = bpy.context.active_object
casa1.name = "Casa_1_Hexagono"
finalize_object(casa1, locations[0], mats[0 % len(mats)] if mats else None)

# Casa 2
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=2, depth=3, location=(0,0,0))
casa2 = bpy.context.active_object
bpy.ops.object.mode_set(mode='EDIT')
mesh = bmesh.from_edit_mesh(casa2.data)
mesh.faces.ensure_lookup_table()
top_face = next(f for f in mesh.faces if f.normal.z > 0.9)
bmesh.ops.scale(mesh, vec=(0.5, 0.5, 1.0), verts=top_face.verts)
bmesh.update_edit_mesh(casa2.data)
bpy.ops.object.mode_set(mode='OBJECT')
casa2.name = "Casa_2_ConoTruncado"
finalize_object(casa2, locations[1], mats[1 % len(mats)] if mats else None)

# Casa 3
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=2.5, location=(0,0,0))
casa3 = bpy.context.active_object
bpy.ops.object.mode_set(mode='EDIT')
mesh = bmesh.from_edit_mesh(casa3.data)
verts_to_delete = [v for v in mesh.verts if v.co.z < 0]
bmesh.ops.delete(mesh, geom=verts_to_delete, context='VERTS')
bmesh.update_edit_mesh(casa3.data)
bpy.ops.object.mode_set(mode='OBJECT')
casa3.name = "Casa_3_Domo"
finalize_object(casa3, locations[2], mats[2 % len(mats)] if mats else None)

# Casa 4
bpy.ops.mesh.primitive_cube_add(size=3, location=(0,0,0))
cube1 = bpy.context.active_object
bpy.ops.mesh.primitive_cube_add(size=3, location=(0,0,0))
cube2 = bpy.context.active_object
cube2.rotation_euler[2] = 0.785398
bpy.ops.object.select_all(action='DESELECT')
cube1.select_set(True)
cube2.select_set(True)
bpy.context.view_layer.objects.active = cube1
bpy.ops.object.join()
casa4 = bpy.context.active_object
casa4.name = "Casa_4_CubosRotados"
finalize_object(casa4, locations[3], mats[3 % len(mats)] if mats else None)

# Casa 5
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=6, location=(0,0,3))
cyl = bpy.context.active_object
bpy.ops.mesh.primitive_torus_add(major_radius=2, minor_radius=0.5, location=(0,0,6))
tor = bpy.context.active_object
bpy.ops.object.select_all(action='DESELECT')
cyl.select_set(True)
tor.select_set(True)
bpy.context.view_layer.objects.active = cyl
bpy.ops.object.join()
casa5 = bpy.context.active_object
casa5.name = "Casa_5_CilindroToroide"
finalize_object(casa5, locations[4], mats[4 % len(mats)] if mats else None)

# Casa 6
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=2, depth=4, location=(0,0,0))
casa6 = bpy.context.active_object
casa6.name = "Casa_6_Piramide"
finalize_object(casa6, locations[5], mats[5 % len(mats)] if mats else None)

# Casa 7
bpy.ops.mesh.primitive_cube_add(size=2, location=(0,0,0))
casa7 = bpy.context.active_object
bpy.ops.object.mode_set(mode='EDIT')
mesh = bmesh.from_edit_mesh(casa7.data)
mesh.faces.ensure_lookup_table()
top_face = next(f for f in mesh.faces if f.normal.z > 0.9)
top_face.select_set(True)
extruded = bmesh.ops.extrude_discrete_faces(mesh, faces=[top_face])
ext_top = extruded['faces'][0]
bmesh.ops.translate(mesh, vec=(0,0,2), verts=ext_top.verts)
mesh.faces.ensure_lookup_table()
side_face = next(f for f in mesh.faces if f.normal.x > 0.9 and f.calc_center_median().z > 0.5)
extruded2 = bmesh.ops.extrude_discrete_faces(mesh, faces=[side_face])
bmesh.ops.translate(mesh, vec=(2,0,0), verts=extruded2['faces'][0].verts)
bmesh.update_edit_mesh(casa7.data)
bpy.ops.object.mode_set(mode='OBJECT')
casa7.name = "Casa_7_FormaL"
finalize_object(casa7, locations[6], mats[6 % len(mats)] if mats else None)

# Casa 8
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.5, depth=5, location=(0,0,0))
casa8 = bpy.context.active_object
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=2)
mesh = bmesh.from_edit_mesh(casa8.data)
for v in mesh.verts:
    if 0.5 < v.co.z < 1.5:
        v.co.x *= 1.5
        v.co.y *= 1.5
    if -1.5 < v.co.z < -0.5:
        v.co.x *= 0.5
        v.co.y *= 0.5
bmesh.update_edit_mesh(casa8.data)
bpy.ops.object.mode_set(mode='OBJECT')
casa8.name = "Casa_8_CortesIrregulares"
finalize_object(casa8, locations[7], mats[7 % len(mats)] if mats else None)

# Casa 9
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=3, location=(0,0,1.5))
base_cyl = bpy.context.active_object
bpy.ops.mesh.primitive_cone_add(radius1=3, depth=1.5, location=(0,0,3.75))
cone = bpy.context.active_object
cone.rotation_euler[1] = 3.14159
bpy.ops.object.transform_apply(rotation=True)
bpy.ops.object.select_all(action='DESELECT')
base_cyl.select_set(True)
cone.select_set(True)
bpy.context.view_layer.objects.active = base_cyl
bpy.ops.object.join()
casa9 = bpy.context.active_object
casa9.name = "Casa_9_Hongo"
finalize_object(casa9, locations[8], mats[8 % len(mats)] if mats else None)

result = {"success": True, "message": "9 Alien structures generated successfully"}
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
