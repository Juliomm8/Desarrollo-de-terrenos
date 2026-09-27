import socket
import json

code = """
import bpy
import bmesh
from mathutils import Vector

bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=2.5, depth=2.5, location=(0, 0, 0))
body = bpy.context.active_object
bpy.ops.object.mode_set(mode='EDIT')
mesh = bmesh.from_edit_mesh(body.data)
mesh.faces.ensure_lookup_table()

normals = []
for f in mesh.faces:
    normals.append((f.normal.x, f.normal.y, f.normal.z))

bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.delete()

result = {"success": True, "normals": normals}
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
