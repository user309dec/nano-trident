from __future__ import annotations

import argparse
import os

import numpy as np
import torch
import torch.nn as nn

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import openslide
import skimage.color as sk_color
import skimage.filters as sk_filters


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Nano end-to-end Trident, on CPU.")
    p.add_argument("--slide", default=os.path.expanduser(
        "~/trident_lab/wsis/CMU-1-Small-Region.svs"))
    p.add_argument("--out_dir", default=os.path.expanduser("~/trident_lab/nano"))
    p.add_argument("--patch_size", type=int, default=256)
    p.add_argument("--tissue_frac", type=float, default=0.10)
    p.add_argument("--train-demo", action="store_true")
    p.add_argument("--seed", type=int, default=0)
    return p.parse_args()


def load_slide(path: str) -> openslide.OpenSlide:
    slide = openslide.OpenSlide(path)
    W, H = slide.dimensions
    mpp = slide.properties.get("openslide.mpp-x", "?")
    print(f"[1] slide loaded: {os.path.basename(path)}")
    print(f"    level-0 size = {W} x {H} px,  mpp = {mpp} um/px")
    return slide


def nano_segment(slide: openslide.OpenSlide, thumb_max: int = 512):
    W, H = slide.dimensions #the first element slide.dimensions output is width, and the second is height
    reduceportion = max(W, H) / thumb_max
    # tw, th = W / reduceportion, H / reduceportion use int cuz python automatically takes /'s result as float, not like C
    tw, th = int(W / reduceportion), int(H / reduceportion)
    slide_numpy_array = np.array(slide.get_thumbnail((tw, th)).convert("RGB")) # use get_thumbnail to get the smaller slide of tw * th, then convert to RGB. Then use np.arrary to generate array.

    #from now, slide_numpy_array is a (th, tw, 3) numpy array(numpy array takes height, width, channel as sequence)
    sat = sk_color.rgb2hsv(slide_numpy_array)[..., 1] #change rgb to hsv to get sat
    threshold = sk_filters.threshold_otsu(sat) # we have the threshold of sat
    tissue = sat > threshold #we have the bool array of whether tissue's saturation is greater than threshold or not. If it's True, then we know it's tissue.

    #from now we have everything needed: sat, tissue, numpy array
    tissue_coverage = tissue.mean() #calculate the ratio of True in this boolean array since True is 1 and False is 0

    print(f"1. slide loaded: {tw} * {th} px"
          f"2. the coverage of tissue in the slide is {tissue_coverage*100:.2f}%"
          )

    # scale = level-0 pixels per thumbnail pixel, so patch code can map between them.
    scale = W / tw #the original float reduceportion

    return tissue, scale


def nano_patch(slide, tissue_mask, mask_scale, patch_size, tissue_frac):
    W, H = slide.dimensions
    coords = []
    for y in range(0, H - patch_size + 1, patch_size):
        for x in range(0, W - patch_size + 1, patch_size):
            x0 = int(x / mask_scale)
            y0 = int(y / mask_scale)
            x1 = int((x + patch_size) / mask_scale) # adding patch size is because x1 will not be taken in the following code
            y1 = int((y + patch_size) / mask_scale) #same reason as above
            cell = tissue_mask[y0:y1, x0:x1] #numpy takes (y,x)
            if cell.size and cell.mean() >= tissue_frac: #size is product of dim length(width * height * ...) which is the sum of elements. short eval. cell mean to calculate the coverage > tissue frac as standard of keeping this grid
                coords.append((x, y)) #save the coords of original wsi to be used for next step of patch encode

    coords = np.array(coords, dtype=np.int64) # list np.arrary to a matrix array of (n,2)
    print(f"3. nano-patch: grid step={patch_size}px, kept {len(coords)} tissue patches"
          f"  ->  coords {coords.shape}")
    return coords


# This part is written by claude since i don't know how to introduce resnet50
def build_encoder():
    from torchvision.models import resnet50, ResNet50_Weights
    try:
        weights = ResNet50_Weights.IMAGENET1K_V1
        net = resnet50(weights=weights)
        preprocess = weights.transforms()
        print("[4] encoder: resnet50, dim = 2048")
    except Exception as e:
        net = resnet50(weights=None)
        preprocess = ResNet50_Weights.IMAGENET1K_V1.transforms()
        print(f"[4] encoder: resnet50 (RANDOM weights, no download: {e}), dim = 2048")
    net.fc = nn.Identity()  # drop the 1000-class head; keep the 2048-d embedding
    net.eval()
    return net, preprocess


@torch.no_grad()                      # 整个函数不追踪梯度
def nano_encode(slide, coords, patch_size, encoder, preprocess, batch_size=32):
    """把每个 patch 编码成一个 2048 维向量, 返回 (n, 2048) 的 float32 张量。"""
    device = next(encoder.parameters()).device   # 模型在哪, 数据就送到哪
    encoder.eval()

    feats = []       # 收集每个 batch 的输出
    buffer = []      # 攒够一个 batch 再一起算

    for (x, y) in coords:
        tile = slide.read_region((int(x), int(y)), 0, (patch_size, patch_size))
        tile = tile.convert("RGB")          # RGBA → RGB, 丢掉 alpha 通道
        buffer.append(preprocess(tile))     # (3, 224, 224)

        if len(buffer) == batch_size:
            batch = torch.stack(buffer).to(device)   # (batch_size, 3, 224, 224)
            out = encoder(batch)                     # (batch_size, 2048)
            feats.append(out.cpu())                  # 挪回 CPU, 别把显存堆满
            buffer = []

    if buffer:                              # 处理最后不满一个 batch 的零头
        batch = torch.stack(buffer).to(device)
        out = encoder(batch)
        feats.append(out.cpu())

    features = torch.cat(feats, dim=0).float()   # (n, 2048)
    print(features.shape)
    return features