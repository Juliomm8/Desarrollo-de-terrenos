import socket
import json

code = """
import bpy
import os

def export_casas():
    export_dir = "C:/Desarrollo de Videojuegos/Desarrollo de terrenos/Assets/Models/"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
        
    results = []
    
    # Recorrer todos los objetos
    for obj in bpy.context.scene.objects:
        if obj.name.startswith('Casa_Habitacion_'):
            # Deselecciona todo
            bpy.ops.object.select_all(action='DESELECT')
            
            # Selecciona únicamente ese objeto
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            
            filename = obj.name + ".fbx"
            filepath = os.path.join(export_dir, filename)
            
            try:
                bpy.ops.export_scene.fbx(
                    filepath=filepath,
                    use_selection=True,
                    global_scale=1.0,
                    apply_scale_options='FBX_SCALE_ALL',
                    axis_forward='-Z',
                    axis_up='Y',
                    object_types={'MESH'}
                )
                results.append({"name": obj.name, "success": True, "filepath": filepath})
            except Exception as e:
                results.append({"name": obj.name, "success": False, "error": str(e)})
                
    return {"success": True, "results": results}

result = export_casas()
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
