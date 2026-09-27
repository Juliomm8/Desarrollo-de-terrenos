import socket
import json

code = """
import bpy
import bmesh
from mathutils import Vector

obj = bpy.data.objects.get('CosmicDiner_Base')
if not obj:
    result = {"success": False, "error": "CosmicDiner_Base not found"}
else:
    # 1. Create Materials
    def create_material(name, color, metallic=0.0, roughness=0.5, emission=None, emission_strength=1.0):
        # Delete if exists
        if name in bpy.data.materials:
            bpy.data.materials.remove(bpy.data.materials[name])
            
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Metallic"].default_value = metallic
            bsdf.inputs["Roughness"].default_value = roughness
            if emission:
                # In Blender 4.x, Emission color and strength are inputs on Principled BSDF
                if "Emission Color" in bsdf.inputs:
                    bsdf.inputs["Emission Color"].default_value = emission
                elif "Emission" in bsdf.inputs:
                    bsdf.inputs["Emission"].default_value = emission
                bsdf.inputs["Emission Strength"].default_value = emission_strength
        return mat

    mat_pared = create_material('Diner_Pared', (0.2, 0.05, 0.3, 1.0))
    mat_techo = create_material('Diner_Techo', (0.1, 0.1, 0.1, 1.0))
    mat_metal = create_material('Diner_Metal', (0.8, 0.8, 0.8, 1.0), metallic=1.0, roughness=0.2)
    mat_neon = create_material('Diner_Neon', (1.0, 0.3, 0.0, 1.0), emission=(1.0, 0.3, 0.0, 1.0), emission_strength=5.0)

    # Clear existing slots
    obj.data.materials.clear()
    
    # 2. Add to Material Slots (0=Pared, 1=Techo, 2=Metal, 3=Neon)
    obj.data.materials.append(mat_pared)
    obj.data.materials.append(mat_techo)
    obj.data.materials.append(mat_metal)
    obj.data.materials.append(mat_neon)

    # 3. Assign with BMesh
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    mesh = bmesh.from_edit_mesh(obj.data)
    mesh.faces.ensure_lookup_table()

    for face in mesh.faces:
        # Default: Pared
        face.material_index = 0
        
        # Calculate face center to determine which part it belongs to
        center = face.calc_center_median()
        
        # The floating sign was created at Z=4 with height 0.5
        # The base origin was set to Z=0 and then translated. 
        # Actually the entire object was translated down by min_z.
        # Originally, base was Z in [0,2], inset was Z in [2,3].
        # Sign was Z in [3.75, 4.25].
        # Antenna was around X=-2, Y=-1, Z in [3, 5]
        # Wait, if min_z was 0, and the base was originally 0... wait.
        # Base cube was location=(0,0,1), scale Z=1. Bottom Z=0, Top Z=2.
        # Inset extrusion was vec=(0,0,1), so Top Z=3.
        # Sign was location=(0,0,4), scale Z=0.5, so Z=3.75 to 4.25.
        # Antenna was location=(-2,-1,3.5), depth=1.0 -> Z=3.0 to 4.0. Extrusions went higher.
        # So min_z was exactly 0. The coordinates should be exactly the same!
        
        is_sign = center.z > 3.6 and center.x > -1.5 and center.x < 1.5
        is_antenna = center.x < -1.0 and center.y < -0.5 and center.z > 2.8
        
        if is_sign:
            face.material_index = 3 # Neon
        elif is_antenna:
            face.material_index = 2 # Metal
        else:
            # Roof: pointing exactly up
            if face.normal.z > 0.99:
                face.material_index = 1 # Techo

    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Update Viewport to Material Preview
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'

    result = {"success": True, "message": "Materials assigned successfully"}
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
