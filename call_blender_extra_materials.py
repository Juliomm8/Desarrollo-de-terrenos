import socket
import json

code = """
import bpy

def create_material(name, color=None, metallic=0.0, roughness=0.5, emission=None, emission_strength=1.0, transmission=0.0):
    if name in bpy.data.materials:
        bpy.data.materials.remove(bpy.data.materials[name])
        
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.use_fake_user = True
    
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if color:
            bsdf.inputs["Base Color"].default_value = color
        
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
            
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        
        if emission:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
                
        if transmission > 0.0:
            if "Transmission Weight" in bsdf.inputs:
                bsdf.inputs["Transmission Weight"].default_value = transmission
            elif "Transmission" in bsdf.inputs:
                bsdf.inputs["Transmission"].default_value = transmission

    return mat

# Estructura
create_material('Alien_Muro_Cian', color=(0.0, 0.2, 0.3, 1.0))
create_material('Alien_Muro_Mostaza', color=(0.6, 0.5, 0.2, 1.0))
create_material('Alien_Metal_Oxidado', color=(0.3, 0.1, 0.1, 1.0), metallic=0.2, roughness=0.9)

# Neon
create_material('Alien_Neon_Verde', color=(0.0, 1.0, 0.0, 1.0), emission=(0.0, 1.0, 0.0, 1.0), emission_strength=5.0)
create_material('Alien_Neon_Rosa', color=(1.0, 0.0, 1.0, 1.0), emission=(1.0, 0.0, 1.0, 1.0), emission_strength=5.0)

# Detalle
create_material('Alien_Cristal', color=(0.6, 0.8, 1.0, 1.0), roughness=0.1, transmission=1.0)
create_material('Alien_Panel_Solar', color=(0.01, 0.02, 0.1, 1.0), metallic=0.9)

result = {"success": True, "message": "Extended materials created successfully"}
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
