import random
from scipy.fftpack import dct, idct
import numpy as np
from PIL import Image

def block_scramble(image_array, block_size, key):
    height, width = image_array.shape
    blocks = []

    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            block = image_array[i : i + block_size, j : j + block_size]
            blocks.append(block)

    indices = list(range(len(blocks)))
    random.seed(key)
    random.shuffle(indices)

    scrambled_blocks = [blocks[i] for i in indices]

    scrambled_array = np.zeros_like(image_array)
    idx = 0
    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            scrambled_array[i : i + block_size, j : j + block_size] = scrambled_blocks[
                idx
            ]
            idx += 1

    return scrambled_array, indices

def block_rotation(block, secret_key):
    random.seed(secret_key)
    operation = random.randint(0, 3)

    if operation == 0:
        return np.rot90(block, 1)
    elif operation == 1:
        return np.rot90(block, 2)
    elif operation == 2:
        return np.rot90(block, 3)
    else:
        return block

def block_inversion(block, secret_key):
    random.seed(secret_key)

    operation = random.randint(0, 1)

    if operation == 0:
        return np.fliplr(block)
    else:
        return np.flipud(block)


def negative_positive_transformation(block, secret_key):
    random.seed(secret_key)
    operation = random.randint(0, 1)

    if operation == 0:
        return 255 - block
    return block




def block_descramble(
    scrambled_array,
    indices,
    block_size,
):
    height, width = scrambled_array.shape

    blocks = []
    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            block = scrambled_array[i : i + block_size, j : j + block_size]
            blocks.append(block)

    original_blocks = [None] * len(blocks)
    for i, idx in enumerate(indices):
        original_blocks[idx] = blocks[i]

    descrambled_array = np.zeros_like(scrambled_array)
    idx = 0
    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            descrambled_array[i : i + block_size, j : j + block_size] = original_blocks[
                idx
            ]
            idx += 1

    return descrambled_array


def block_derotation(block, secret_key):
    random.seed(secret_key)

    # 0에서 3 사이의 무작위 회전 횟수 결정
    operation = random.randint(0, 3)

    if operation == 0:
        return np.rot90(block, 3)

    elif operation == 1:
        return np.rot90(block, 2)

    elif operation == 2:
        return np.rot90(block, 1)

    else:
        return block


def block_deinversion(block, secret_key):
    random.seed(secret_key)

    # 0 또는 1을 무작위로 결정
    operation = random.randint(0, 1)

    if operation == 0:
        return np.fliplr(block)
    else:
        return np.flipud(block)


def de_negative_positive_transformation(block, secret_key):
    random.seed(secret_key)
    operation = random.randint(0, 1)

    if operation == 0:
        return 255 - block
    return block


def idct_2d(dct_block):
    return idct(idct(dct_block, norm='ortho'), norm='ortho')

def dct_2d(dct_block):
    return dct(dct(dct_block, norm='ortho'), norm='ortho')


def dequantization(block, quality):
    return block * quality
