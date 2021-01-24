import sys
import os
import traceback
import trimesh
import numpy as np
from pygltflib import *

sRGB_TO_LINEAR_RGB = True


if __name__ == "__main__":

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # check if it's glTF or glb
    output_ext = os.path.splitext(output_path)[-1]
    if output_ext == ".glb":
        EXPORT_AS_GLB = True
    elif output_ext == ".glTF" or output_ext == ".gltf":
        EXPORT_AS_GLB = False
    else:
        try:
            raise Exception("Unsupported file extention {0}".format(output_ext))
        except:
            traceback.print_exc()
            exit(0)

    # load mesh
    mesh = trimesh.load_mesh(input_path)

    # instantiate GLTF2
    gltf = GLTF2()
    gltf.asset = Asset()
    gltf.scenes = [Scene()]
    gltf.nodes = [Node()]       # Mesh node
    gltf.meshes = [Mesh()]
    gltf.accessors = [Accessor() for _ in range(4)]     # faces, vertices, v_colors, v_norms
    gltf.materials = [Material()]
    gltf.bufferViews = [BufferView() for _ in range(4)]
    gltf.buffers = [Buffer()]

    # asset
    gltf.asset = Asset()
    gltf.asset.generator = "OBJwVC_to_glTF"
    gltf.asset.copyright = "Tomoaki Osada (ynyBonfennil)"

    # scene
    gltf.scene = 0

    # materials
    gltf.materials[0].pbrMetallicRoughness = PbrMetallicRoughness(metallicFactor=0.0, roughnessFactor=0.5)
    gltf.materials[0].emissiveFactor = [0.0, 0.0, 0.0]
    gltf.materials[0].name = "material 001-effect"

    # store faces
    # face (indices) data must be stored as a sequence of SCALAR value
    # hense accessor.type is set to SCALAR, and accessors.count is
    # 3 times the length of face vectors
    indices_chunk = b""
    for f in mesh.faces:
        indices_chunk += struct.pack("<III", *f)
    gltf.bufferViews[0].buffer = 0
    gltf.bufferViews[0].byteOffset = 0
    gltf.bufferViews[0].byteLength = len(indices_chunk)
    gltf.bufferViews[0].target = ELEMENT_ARRAY_BUFFER
    gltf.accessors[0].bufferView = 0
    gltf.accessors[0].byteOffset = 0
    gltf.accessors[0].componentType = UNSIGNED_INT
    gltf.accessors[0].normalized = False
    gltf.accessors[0].count = len(mesh.faces) * 3
    gltf.accessors[0].type = "SCALAR"

    # store vertices
    vertices_chunk = b""
    for v in mesh.vertices:
        vertices_chunk += struct.pack("<fff", *v)
    gltf.bufferViews[1].buffer = 0
    gltf.bufferViews[1].byteOffset = gltf.bufferViews[0].byteLength
    gltf.bufferViews[1].byteLength = len(vertices_chunk)
    gltf.bufferViews[1].target = ARRAY_BUFFER
    gltf.accessors[1].bufferView = 1
    gltf.accessors[1].byteOffset = 0
    gltf.accessors[1].componentType = FLOAT
    gltf.accessors[1].normalized = False
    gltf.accessors[1].count = len(mesh.vertices)
    gltf.accessors[1].type = "VEC3"
    gltf.accessors[1].max = list(np.max(mesh.vertices.T, axis=1))       # get the max value for each xyz
    gltf.accessors[1].min = list(np.min(mesh.vertices.T, axis=1))

    # store vertex colors
    vcolor_chunk = b""
    if sRGB_TO_LINEAR_RGB:          # sRGB to Linear RGB if needed.
        vc = mesh.visual.vertex_colors[:, :3] / 255
        vc = np.clip(vc, 0, None)
        vc[vc < 0.04045] = vc[vc < 0.04045] * (1.0 / 12.92)
        vc[vc >= 0.04045] = pow((vc[vc >= 0.04045] + 0.055) * (1.0 / 1.055), 2.4)
        mesh.visual.vertex_colors[:, :3] = vc * 255
    for vc in mesh.visual.vertex_colors:
        vc_rgb = vc[:3] / 255
        vcolor_chunk += struct.pack("<fff", *vc_rgb)
    gltf.bufferViews[2].buffer = 0
    gltf.bufferViews[2].byteOffset = gltf.bufferViews[1].byteOffset + gltf.bufferViews[1].byteLength
    gltf.bufferViews[2].byteLength = len(vcolor_chunk)
    gltf.bufferViews[2].target = ARRAY_BUFFER
    gltf.accessors[2].bufferView = 2
    gltf.accessors[2].byteOffset = 0
    gltf.accessors[2].componentType = FLOAT
    gltf.accessors[2].normalized = False
    gltf.accessors[2].count = len(mesh.visual.vertex_colors)
    gltf.accessors[2].type = "VEC3"

    vnorm_chunk = b""
    for vn in mesh.vertex_normals:
        vnorm_chunk += struct.pack("<fff", *vn)
    gltf.bufferViews[3].buffer = 0
    gltf.bufferViews[3].byteOffset = gltf.bufferViews[2].byteOffset + gltf.bufferViews[2].byteLength
    gltf.bufferViews[3].byteLength = len(vnorm_chunk)
    gltf.bufferViews[3].target = ARRAY_BUFFER
    gltf.accessors[3].bufferView = 3
    gltf.accessors[3].byteOffset = 0
    gltf.accessors[3].componentType = FLOAT
    gltf.accessors[3].normalized = False
    gltf.accessors[3].count = len(mesh.vertex_normals)
    gltf.accessors[3].type = "VEC3"

    # store buffer data
    if EXPORT_AS_GLB:
        gltf.identify_uri = BufferFormat.BINARYBLOB
        gltf._glb_data = indices_chunk + vertices_chunk + vcolor_chunk + vnorm_chunk
        gltf.buffers[0].byteLength = gltf.bufferViews[3].byteOffset + gltf.bufferViews[3].byteLength
    else:
        gltf.identify_uri = BufferFormat.BINFILE
        bin_filename = output_path + ".bin"
        with open(bin_filename, "wb") as f:
            f.write(
                indices_chunk
                + vertices_chunk
                + vcolor_chunk
                + vnorm_chunk
            )
        gltf.buffers[0].uri = os.path.basename(bin_filename)
        gltf.buffers[0].byteLength = gltf.bufferViews[3].byteOffset + gltf.bufferViews[3].byteLength
    
    # mesh
    gltf.meshes[0].primitives = [
        Primitive(
            attributes=Attributes(
                POSITION=1,
                NORMAL=3,
                COLOR_0=2,
            ),
            indices=0,
            material=0
        )
    ]
    gltf.meshes[0].name = "Mesh"

    # assemble nodes
    gltf.nodes[0].mesh = 0
    gltf.nodes[0].name = "Mesh"

    gltf.scenes[0].nodes = [0]

    # export
    if EXPORT_AS_GLB:
        gltf.save_binary(output_path)
    else:
        gltf.save_json(output_path)
    