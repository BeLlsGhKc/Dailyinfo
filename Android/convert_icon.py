# -*- coding: utf-8 -*-
"""
图标转换脚本

将 Ico/岚兮儿天下无敌好看.ico 转换为安卓所需的 PNG 格式

使用方法：
1. 安装 Pillow：pip install Pillow
2. 运行脚本：python Android/convert_icon.py
"""

import os
from PIL import Image

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICO_PATH = os.path.join(BASE_DIR, "Ico", "岚兮儿天下无敌好看.ico")
ANDROID_RES_DIR = os.path.join(BASE_DIR, "Android", "app", "src", "main", "res")

# 需要生成的尺寸
SIZES = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}


def convert_icon():
    """转换图标"""
    if not os.path.exists(ICO_PATH):
        print(f"错误: 找不到图标文件 {ICO_PATH}")
        return False

    try:
        img = Image.open(ICO_PATH)
        print(f"成功加载图标: {img.size}")

        for folder, size in SIZES.items():
            output_dir = os.path.join(ANDROID_RES_DIR, folder)
            os.makedirs(output_dir, exist_ok=True)

            output_path = os.path.join(output_dir, "ic_launcher.png")
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(output_path, "PNG")
            print(f"生成: {output_path} ({size}x{size})")

        print("\n图标转换完成！")
        return True

    except ImportError:
        print("错误: 请先安装 Pillow")
        print("运行: pip install Pillow")
        return False

    except Exception as e:
        print(f"错误: {e}")
        return False


if __name__ == "__main__":
    convert_icon()
