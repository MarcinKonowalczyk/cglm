import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

__file_dir__ = Path(__file__).parent

parser = argparse.ArgumentParser()
parser.add_argument("--suffix", type=str)
args = parser.parse_args()
suffix = args.suffix

glm_vec4_file = __file_dir__ / f"glm_vec4_{suffix}.bin"
cglm_vec4_file = __file_dir__ / f"cglm_vec4_{suffix}.bin"
glm_vec3_file = __file_dir__ / f"glm_vec3_{suffix}.bin"
cglm_vec3_file = __file_dir__ / f"cglm_vec3_{suffix}.bin"
glm_vec2_file = __file_dir__ / f"glm_vec2_{suffix}.bin"
cglm_vec2_file = __file_dir__ / f"cglm_vec2_{suffix}.bin"


def load_bin(filename: str):
    data = np.fromfile(filename, dtype=np.float32)
    L, M, N = data[:3].view(np.int32)  # reinterpret as int
    return data[3:].reshape(L, M, N)


glm_vec4_data = load_bin(glm_vec4_file)
cglm_vec4_data = load_bin(cglm_vec4_file)
glm_vec3_data = load_bin(glm_vec3_file)
cglm_vec3_data = load_bin(cglm_vec3_file)
glm_vec2_data = load_bin(glm_vec2_file)
cglm_vec2_data = load_bin(cglm_vec2_file)

import plot_helpers as ph

ph.data_viewer_2(
    (glm_vec4_data, "glm::perlin(vec4)"),
    (cglm_vec4_data, "glm_perlin_vec4"),
    (glm_vec3_data, "glm::perlin(vec3)"),
    (cglm_vec3_data, "glm_perlin_vec3"),
    (glm_vec2_data, "glm::perlin(vec2)"),
    (cglm_vec2_data, "glm_perlin_vec2"),
)
