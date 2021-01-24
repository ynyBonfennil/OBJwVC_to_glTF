# Wavefront OBJ with Vertex Color to glTF2.0

Python script to convert Wavefront OBJ with Vertex Color to glTF2.0. Texture coordinate is not supported.

## How to use

### Prerequisites

Please install the following packages, or install by using `requirements.txt`.

- trimesh
- pygltflib
- numpy

### Run script

Specify input / output file path to command line argument.

```sh
$ python ./OBJwVC_to_gltf.py {input file path} {output file path}
```

## Parameters

### Export as glb (On / Off)

This script supports exporting glb along with glTF and its bin file. This script detects the file extention you select as the output file path, and exports the selected format.

### sRGB to Linear RGB (On / Off)

It seems that directly applying Wavefront OBJ's vertex color values to glTF vertex color sometimes fails (the color becomes lighter, or whiter in other words). It's because of the inconsistency of color space (sRGB or Linear RGB). Hence this script defines `sRGB_TO_LINEAR_RGB = True/False` value inside it. If you have any problem of color space, please edit this value.
