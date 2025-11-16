#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
词云图生成器 - 合并版
包含Flask应用和启动功能
"""

import subprocess
import sys
import os
from flask import Flask, render_template, request, jsonify, send_from_directory
import numpy as np
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')  # 设置非交互式后端
import matplotlib.pyplot as plt
import io
import base64
from PIL import Image
import re
import platform
from sklearn.cluster import KMeans
import colorsys

# 全局变量
app = Flask(__name__)

# 预定义的形状模板
SHAPE_TEMPLATES = {
    'circle': '圆形',
    'heart': '心形', 
    'star': '五角星',
    'rectangle': '矩形',
    'triangle': '三角形',
    'hexagon': '六边形',
    'ellipse': '椭圆形',
    'diamond': '菱形',
    'pentagon': '五边形',
    'octagon': '八边形',
    'china_map': '中国地图',
    'shanghai_map': '上海地图'
}

# 预定义的字体选项
FONT_OPTIONS = {
    'default': '默认字体',
    'simhei': '黑体',
    'simsun': '宋体',
    'msyh': '微软雅黑',
    'simkai': '楷体',
    'simfang': '仿宋',
    'simli': '隶书',
    'simyou': '幼圆'
}

# 预定义的颜色主题
COLOR_THEMES = {
    'viridis': '青绿色系',
    'plasma': '紫红色系',
    'inferno': '黄橙红色系',
    'magma': '紫黑色系',
    'cividis': '蓝绿色系',
    'twilight': '紫蓝色系',
    'rainbow': '彩虹色系',
    'ocean': '海洋色系',
    'sunset': '日落色系',
    'forest': '森林色系',
    'fire': '火焰色系',
    'pastel': '柔和色系',
    'dark': '深色系',
    'neon': '霓虹色系'
}

def install_requirements():
    """安装项目依赖"""
    print("🔧 正在安装项目依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖安装完成！")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败，请检查网络连接和权限")
        return False

def get_font_by_name(font_name):
    """根据字体名称获取字体路径"""
    system = platform.system()
    
    if font_name == 'default':
        return get_chinese_font()  # 使用系统中可用的中文字体
    
    if system == 'Windows':
        font_paths = {
            'simhei': 'C:/Windows/Fonts/simhei.ttf',      # 黑体
            'simsun': 'C:/Windows/Fonts/simsun.ttc',      # 宋体
            'msyh': 'C:/Windows/Fonts/msyh.ttc',          # 微软雅黑
            'simkai': 'C:/Windows/Fonts/simkai.ttf',      # 楷体
            'simfang': 'C:/Windows/Fonts/simfang.ttf',    # 仿宋
            'simli': 'C:/Windows/Fonts/simli.ttf',        # 隶书
            'simyou': 'C:/Windows/Fonts/simyou.ttf'       # 幼圆
        }
    elif system == 'Darwin':  # macOS
        font_paths = {
            'simhei': '/System/Library/Fonts/STHeiti.ttc',      # 华文黑体
            'simsun': '/System/Library/Fonts/STSong.ttc',        # 华文宋体
            'msyh': '/System/Library/Fonts/PingFang.ttc',        # 苹方(类似微软雅黑)
            'simkai': '/System/Library/Fonts/STKaiti.ttc',      # 华文楷体
            'simfang': '/System/Library/Fonts/STFangsong.ttc',   # 华文仿宋
            'simli': '/System/Library/Fonts/STLiti.ttc',         # 华文隶体
            'simyou': '/System/Library/Fonts/STYuanti.ttc'       # 华文圆体
        }
    else:  # Linux
        font_paths = {
            'simhei': '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',  # 文泉驿微米黑
            'simsun': '/usr/share/fonts/truetype/arphic/uming.ttc',      # 文鼎PL中楷
            'msyh': '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',      # 文泉驿正黑
            'simkai': '/usr/share/fonts/truetype/arphic/ukai.ttc',        # 文鼎PL上海宋
            'simfang': '/usr/share/fonts/truetype/arphic/bsmi00lp.ttf',   # 文鼎PL报宋
            'simli': '/usr/share/fonts/truetype/arphic/gbsn00lp.ttf',     # 文鼎PL简宋
            'simyou': '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'      # 文泉驿正黑
        }
    
    # 返回对应的字体路径，如果不存在则返回系统中可用的中文字体
    font_path = font_paths.get(font_name, None)
    if font_path and os.path.exists(font_path):
        return font_path
    
    # 如果指定的字体不存在，返回系统中可用的中文字体
    return get_chinese_font()

def get_chinese_font():
    """获取支持中文的字体路径"""
    system = platform.system()
    
    if system == 'Windows':
        # Windows系统常见中文字体
        font_paths = [
            'C:/Windows/Fonts/msyh.ttc',        # 微软雅黑
            'C:/Windows/Fonts/simhei.ttf',      # 黑体
            'C:/Windows/Fonts/simsun.ttc',      # 宋体
            'C:/Windows/Fonts/simkai.ttf',      # 楷体
            'C:/Windows/Fonts/simfang.ttf',    # 仿宋
            'C:/Windows/Fonts/simli.ttf',      # 隶书
            'C:/Windows/Fonts/simyou.ttf'       # 幼圆
        ]
    elif system == 'Darwin':  # macOS
        font_paths = [
            '/System/Library/Fonts/PingFang.ttc',  # 苹方
            '/System/Library/Fonts/STHeiti.ttc',   # 华文黑体
            '/System/Library/Fonts/STSong.ttc',   # 华文宋体
            '/System/Library/Fonts/STKaiti.ttc',   # 华文楷体
            '/System/Library/Fonts/STFangsong.ttc' # 华文仿宋
        ]
    else:  # Linux
        font_paths = [
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',  # 文泉驿微米黑
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',    # 文泉驿正黑
            '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',  # Droid Sans
            '/usr/share/fonts/truetype/arphic/uming.ttc',      # 文鼎PL中楷
            '/usr/share/fonts/truetype/arphic/ukai.ttc'        # 文鼎PL上海宋
        ]
    
    # 检查字体文件是否存在
    for font_path in font_paths:
        if os.path.exists(font_path):
            return font_path
    
    # 如果没有找到，返回None，使用默认字体
    return None

def create_mask_from_image(image_data, width, height):
    """从上传的图片创建掩码"""
    # 解码base64图片数据
    image_data = image_data.split(',')[1]  # 移除data:image/...;base64,前缀
    image_bytes = base64.b64decode(image_data)
    
    # 打开图片并转换为灰度图
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert('L')  # 转换为灰度图
    
    # 调整图片大小到目标尺寸
    img = img.resize((width, height))
    
    # 转换为numpy数组
    img_array = np.array(img)
    
    # 创建掩码：非白色区域为True，白色区域为False
    # 这里使用阈值方法，值小于200的被认为是形状部分
    mask = img_array < 200
    
    return mask

def extract_colors_from_image(image_data, n_colors=5):
    """从图片中提取主要颜色"""
    try:
        # 解码base64图片数据
        image_data = image_data.split(',')[1]  # 移除data:image/...;base64,前缀
        image_bytes = base64.b64decode(image_data)
        
        # 打开图片
        img = Image.open(io.BytesIO(image_bytes))
        
        # 转换为RGB模式（如果不是）
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 调整图片大小以加快处理速度
        img = img.resize((150, 150))
        
        # 转换为numpy数组并重塑为像素列表
        img_array = np.array(img)
        pixels = img_array.reshape(-1, 3)
        
        # 使用K-means聚类提取主要颜色
        kmeans = KMeans(n_clusters=n_colors, random_state=42)
        kmeans.fit(pixels)
        
        # 获取聚类中心（主要颜色）
        colors = kmeans.cluster_centers_
        
        # 将颜色转换为十六进制格式
        hex_colors = []
        for color in colors:
            # 确保值在0-255范围内
            r = int(np.clip(color[0], 0, 255))
            g = int(np.clip(color[1], 0, 255))
            b = int(np.clip(color[2], 0, 255))
            hex_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
            hex_colors.append(hex_color)
        
        return hex_colors
    except Exception as e:
        print(f"颜色提取错误: {str(e)}")
        # 如果颜色提取失败，返回默认颜色
        return ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

def create_wordcloud(text, shape='circle', width=800, height=400, background_color='white', image_data=None, use_image_colors=False, font_name='default', color_theme='viridis'):
    """创建词云图"""
    # 处理文本，逗号分隔
    words = text.split(',')
    word_freq = {}
    
    # 词汇大小与顺序相关 - 越靠前的词汇越大
    for i, word in enumerate(words):
        word = word.strip()
        if word:
            # 根据位置分配权重，越靠前权重越大
            weight = len(words) - i
            word_freq[word] = weight
    
    # 创建形状掩码
    mask = None
    colors = None
    
    if shape == 'custom' and image_data:
        # 使用上传的图片作为掩码
        mask = create_mask_from_image(image_data, width, height)
        
        # 如果需要从图片中提取颜色
        if use_image_colors:
            colors = extract_colors_from_image(image_data)
    elif shape == 'circle':
        # 创建圆形掩码
        mask = np.zeros((height, width), dtype=bool)
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 2 - 10
        
        for i in range(height):
            for j in range(width):
                # 计算到中心的距离
                dx = j - center_x
                dy = i - center_y
                distance = np.sqrt(dx**2 + dy**2)
                
                # 如果距离小于等于半径，则在圆内
                if distance <= radius:
                    mask[i, j] = True
    elif shape == 'rectangle':
        # 矩形不需要特殊掩码
        mask = None
    elif shape == 'triangle':
        # 创建三角形掩码
        mask = np.zeros((height, width), dtype=bool)
        center_x = width // 2
        
        for i in range(height):
            # 计算当前行的高度比例（从顶部0到底部1）
            height_ratio = i / height
            
            # 三角形宽度随高度线性增加
            # 顶部宽度为0，底部宽度为width
            width_at_row = int(width * height_ratio)
            
            # 计算当前行的起始和结束位置
            start_x = center_x - width_at_row // 2
            end_x = center_x + width_at_row // 2
            
            # 设置掩码
            if width_at_row > 0:
                mask[i, start_x:end_x] = True
    elif shape == 'heart':
        # 创建心形掩码 - 使用更准确的心形方程，并旋转180度（倒置）
        mask = np.zeros((height, width), dtype=bool)
        center_x, center_y = width // 2, height // 2 - height // 10  # 稍微上移心形
        
        for i in range(height):
            for j in range(width):
                # 转换为相对于中心的坐标
                x = (j - center_x) / (width / 3)
                y = (i - center_y) / (height / 3)
                
                # 使用更准确的心形方程，并旋转180度（倒置）
                # 旋转180度相当于将y坐标取反
                y = -y  # 旋转180度
                heart = (x**2 + y**2 - 1)**3 - x**2 * y**3
                
                # 如果点在心形内
                if heart <= 0:
                    mask[i, j] = True
    elif shape == 'star':
        # 创建星形掩码
        mask = np.zeros((height, width), dtype=bool)
        center_x, center_y = width // 2, height // 2
        outer_radius = min(width, height) // 2 - 10
        
        for i in range(height):
            for j in range(width):
                # 计算到中心的距离和角度
                dx = j - center_x
                dy = i - center_y
                distance = np.sqrt(dx**2 + dy**2)
                
                # 计算角度
                if distance > 0:
                    angle = np.arctan2(dy, dx)
                    # 将角度映射到0-2π范围
                    if angle < 0:
                        angle += 2 * np.pi
                    
                    # 五角星有10个顶点（5个外顶点，5个内顶点）
                    # 每个顶点之间的角度是36度（π/5）
                    # 计算当前角度在哪个扇区
                    sector = int(angle / (np.pi / 5))
                    sector_angle = angle - sector * (np.pi / 5)
                    
                    # 判断是外顶点还是内顶点
                    if sector % 2 == 0:
                        # 外顶点扇区，使用外半径
                        max_radius = outer_radius
                    else:
                        # 内顶点扇区，使用内半径
                        max_radius = outer_radius * 0.4
                    
                    # 线性插值计算当前角度的半径
                    if sector % 2 == 0:
                        # 从外顶点到内顶点
                        radius_at_angle = outer_radius - (outer_radius * 0.6) * (sector_angle / (np.pi / 5))
                    else:
                        # 从内顶点到外顶点
                        radius_at_angle = outer_radius * 0.4 + (outer_radius * 0.6) * (sector_angle / (np.pi / 5))
                    
                    if distance <= radius_at_angle:
                        mask[i, j] = True
    elif shape == 'hexagon':
        # 创建六边形掩码
        mask = np.zeros((height, width), dtype=bool)
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 2 - 10
        
        for i in range(height):
            for j in range(width):
                # 计算到中心的距离
                dx = j - center_x
                dy = i - center_y
                distance = np.sqrt(dx**2 + dy**2)
                
                # 计算角度
                if distance > 0:
                    angle = np.arctan2(dy, dx)
                    if angle < 0:
                        angle += 2 * np.pi
                    
                    # 六边形有6个顶点，每个顶点之间的角度是60度（π/3）
                    # 计算当前角度在哪个扇区
                    sector = int(angle / (np.pi / 3))
                    sector_angle = angle - sector * (np.pi / 3)
                    
                    # 计算当前角度的半径
                    # 六边形的半径在每个扇区内是变化的
                    if sector % 2 == 0:
                        # 偶数扇区，使用完整半径
                        radius_at_angle = radius
                    else:
                        # 奇数扇区，使用缩小的半径
                        radius_at_angle = radius * 0.866  # cos(30°) ≈ 0.866
                    
                    if distance <= radius_at_angle:
                        mask[i, j] = True
    elif shape == 'ellipse':
        # 创建椭圆形掩码
        mask = np.zeros((height, width), dtype=bool)
        center_x, center_y = width // 2, height // 2
        
        # 椭圆的半长轴和半短轴
        a = width // 2 - 10  # x轴半长轴
        b = height // 2 - 10  # y轴半短轴
        
        for i in range(height):
            for j in range(width):
                # 计算到中心的距离
                dx = j - center_x
                dy = i - center_y
                
                # 椭圆方程：(x/a)^2 + (y/b)^2 <= 1
                if (dx**2 / a**2) + (dy**2 / b**2) <= 1:
                    mask[i, j] = True
    elif shape == 'diamond':
        # 创建菱形掩码
        mask = np.zeros((height, width), dtype=bool)
        center_x, center_y = width // 2, height // 2
        size = min(width, height) // 2 - 10
        
        for i in range(height):
            for j in range(width):
                # 计算到中心的距离
                dx = abs(j - center_x)
                dy = abs(i - center_y)
                
                # 菱形方程：|x|/a + |y|/b <= 1
                if (dx / size) + (dy / size) <= 1:
                    mask[i, j] = True
    elif shape == 'pentagon':
        # 创建五边形掩码
        mask = np.zeros((height, width), dtype=bool)
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 2 - 10
        
        for i in range(height):
            for j in range(width):
                # 计算到中心的距离和角度
                dx = j - center_x
                dy = i - center_y
                distance = np.sqrt(dx**2 + dy**2)
                
                # 计算角度
                if distance > 0:
                    angle = np.arctan2(dy, dx)
                    if angle < 0:
                        angle += 2 * np.pi
                    
                    # 五边形有5个顶点，每个顶点之间的角度是72度（2π/5）
                    # 计算当前角度在哪个扇区
                    sector = int(angle / (2 * np.pi / 5))
                    sector_angle = angle - sector * (2 * np.pi / 5)
                    
                    # 计算当前角度的半径
                    # 五边形的半径在每个扇区内是变化的
                    if sector % 2 == 0:
                        # 偶数扇区，使用完整半径
                        radius_at_angle = radius
                    else:
                        # 奇数扇区，使用缩小的半径
                        radius_at_angle = radius * 0.7265  # cos(36°) ≈ 0.7265
                    
                    if distance <= radius_at_angle:
                        mask[i, j] = True
    elif shape == 'octagon':
        # 创建八边形掩码
        mask = np.zeros((height, width), dtype=bool)
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 2 - 10
        
        for i in range(height):
            for j in range(width):
                # 计算到中心的距离和角度
                dx = j - center_x
                dy = i - center_y
                distance = np.sqrt(dx**2 + dy**2)
                
                # 计算角度
                if distance > 0:
                    angle = np.arctan2(dy, dx)
                    if angle < 0:
                        angle += 2 * np.pi
                    
                    # 八边形有8个顶点，每个顶点之间的角度是45度（π/4）
                    # 计算当前角度在哪个扇区
                    sector = int(angle / (np.pi / 4))
                    sector_angle = angle - sector * (np.pi / 4)
                    
                    # 计算当前角度的半径
                    # 八边形的半径在每个扇区内是变化的
                    if sector % 2 == 0:
                        # 偶数扇区，使用完整半径
                        radius_at_angle = radius
                    else:
                        # 奇数扇区，使用缩小的半径
                        radius_at_angle = radius * 0.7071  # cos(45°) ≈ 0.7071
                    
                    if distance <= radius_at_angle:
                        mask[i, j] = True
    elif shape == 'china_map':
        # 使用chinamap.jpg作为中国地图模板
        try:
            # 加载中国地图图片
            china_map_path = os.path.join(os.path.dirname(__file__), 'chinamap.jpg')
            china_map_img = Image.open(china_map_path)
            
            # 计算保持纵横比的缩放尺寸
            img_width, img_height = china_map_img.size
            aspect_ratio = img_width / img_height
            
            # 根据请求的尺寸和图片纵横比计算实际尺寸
            if width / height > aspect_ratio:
                # 请求的宽度相对于高度太大，以高度为准
                new_height = height
                new_width = int(height * aspect_ratio)
            else:
                # 请求的高度相对于宽度太大，以宽度为准
                new_width = width
                new_height = int(width / aspect_ratio)
            
            # 调整图片大小，保持纵横比
            china_map_img = china_map_img.resize((new_width, new_height), Image.LANCZOS)
            
            # 将图片转换为灰度图像作为掩码
            china_map_gray = china_map_img.convert('L')
            
            # 创建一个与请求尺寸相同的空白掩码
            mask = np.zeros((height, width), dtype=bool)
            
            # 将缩放后的地图居中放置在掩码中
            offset_x = (width - new_width) // 2
            offset_y = (height - new_height) // 2
            
            # 将图片数据转换为numpy数组并设置掩码
            china_map_array = np.array(china_map_gray)
            
            # 将地图图像复制到掩码的中心位置
            mask[offset_y:offset_y+new_height, offset_x:offset_x+new_width] = china_map_array < 128
            
        except Exception as e:
            print(f"加载中国地图模板失败: {e}")
            # 如果加载失败，使用简单的矩形作为后备
            mask = np.zeros((height, width), dtype=bool)
            mask[height//4:3*height//4, width//4:3*width//4] = True
    elif shape == 'shanghai_map':
        # 使用shanghai.jpg作为上海地图模板
        try:
            # 加载上海地图图片
            shanghai_map_path = os.path.join(os.path.dirname(__file__), 'shanghai.png')
            shanghai_map_img = Image.open(shanghai_map_path)
            
            # 计算保持纵横比的缩放尺寸
            img_width, img_height = shanghai_map_img.size
            aspect_ratio = img_width / img_height
            
            # 根据请求的尺寸和图片纵横比计算实际尺寸
            if width / height > aspect_ratio:
                # 请求的宽度相对于高度太大，以高度为准
                new_height = height
                new_width = int(height * aspect_ratio)
            else:
                # 请求的高度相对于宽度太大，以宽度为准
                new_width = width
                new_height = int(width / aspect_ratio)
            
            # 调整图片大小，保持纵横比
            shanghai_map_img = shanghai_map_img.resize((new_width, new_height), Image.LANCZOS)
            
            # 将图片转换为灰度图像作为掩码
            shanghai_map_gray = shanghai_map_img.convert('L')
            
            # 创建一个与请求尺寸相同的空白掩码
            mask = np.zeros((height, width), dtype=bool)
            
            # 将缩放后的地图居中放置在掩码中
            offset_x = (width - new_width) // 2
            offset_y = (height - new_height) // 2
            
            # 将图片数据转换为numpy数组并设置掩码
            shanghai_map_array = np.array(shanghai_map_gray)
            
            # 将地图图像复制到掩码的中心位置
            # 反转逻辑：较亮的区域(大于阈值)设为True(形状内)，较暗的区域设为False(形状外)
            mask[offset_y:offset_y+new_height, offset_x:offset_x+new_width] = shanghai_map_array > 128
            
        except Exception as e:
            print(f"加载上海地图模板失败: {e}")
            # 如果加载失败，使用简单的矩形作为后备
            mask = np.zeros((height, width), dtype=bool)
            mask[height//4:3*height//4, width//4:3*width//4] = True
    
    # 创建词云对象
    # 将布尔掩码转换为整数掩码（0和255）
    # WordCloud中，白色区域(255)是词云可以填充的区域，黑色区域(0)是词云不能填充的区域
    if mask is not None:
        # 对于上海地图，直接使用布尔掩码，不需要反转
        if shape == 'shanghai_map':
            mask = mask.astype(np.uint8) * 255
        else:
            # 对于其他形状，反转掩码：True(形状内) -> 255(白色)，False(形状外) -> 0(黑色)
            mask = (~mask).astype(np.uint8) * 255
    
    # 设置颜色方案
    colormap = None
    if colors:
        # 如果有从图片提取的颜色，创建自定义颜色映射
        colormap = plt.matplotlib.colors.ListedColormap(colors)
    elif color_theme in COLOR_THEMES:
        # 使用预定义的颜色主题
        colormap = color_theme
    
    # 获取字体路径
    font_path = get_font_by_name(font_name)
    if not font_path:
        print("警告：未找到合适的中文字体，可能影响中文显示")
    
    wordcloud = WordCloud(
        width=width,
        height=height,
        background_color=background_color,
        mask=mask,
        font_path=font_path,
        max_words=100,
        relative_scaling=0.5,
        colormap=colormap if colormap else 'viridis',
        color_func=None if colors else None
    ).generate_from_frequencies(word_freq)
    
    return wordcloud

@app.route('/')
def index():
    """主页面"""
    return send_from_directory('.', 'index.html')

@app.route('/generate', methods=['POST'])
def generate_wordcloud():
    """生成词云图的API接口"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        shape = data.get('shape', 'circle')
        width = int(data.get('width', 800))
        height = int(data.get('height', 400))
        background_color = data.get('background_color', 'white')
        image_data = data.get('image_data', None)
        use_image_colors = data.get('use_image_colors', False)
        font_name = data.get('font_name', 'default')
        color_theme = data.get('color_theme', 'viridis')
        
        if not text.strip():
            return jsonify({'error': '请输入词汇内容'}), 400
        
        # 如果选择了自定义图片但没有提供图片数据
        if shape == 'custom' and not image_data:
            return jsonify({'error': '请上传自定义图片模板'}), 400
        
        # 创建词云 - 使用用户输入的尺寸，默认为800x800
        width = width if width > 0 else 800
        height = height if height > 0 else 800
        wordcloud = create_wordcloud(
            text, shape, width, height, background_color, 
            image_data=image_data, 
            use_image_colors=use_image_colors,
            font_name=font_name,
            color_theme=color_theme
        )
        
        # 保存为图片并转换为base64 - 使用用户输入的尺寸
        img_buffer = io.BytesIO()
        
        # 创建词云图像
        fig = plt.figure(figsize=(width/100, height/100), dpi=100)
        ax = fig.add_subplot(111)
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        
        # 调整布局
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)
        
        # 对于中国地图和上海地图形状，保持纵横比并裁剪空白区域
        if shape in ['china_map', 'shanghai_map']:
            # 获取词云图像的数组
            wordcloud_array = np.array(wordcloud)
            
            # 将图像转换为灰度以找到非空白区域
            gray = np.mean(wordcloud_array, axis=2)
            
            # 找到非空白区域的边界
            non_empty = gray < 255  # 假设背景是白色(255)
            if np.any(non_empty):
                y_indices, x_indices = np.where(non_empty)
                min_y, max_y = np.min(y_indices), np.max(y_indices)
                min_x, max_x = np.min(x_indices), np.max(x_indices)
                
                # 裁剪到非空白区域
                cropped_array = wordcloud_array[min_y:max_y+1, min_x:max_x+1]
                
                # 创建新的图形，保持裁剪后的纵横比
                cropped_height, cropped_width = cropped_array.shape[:2]
                aspect_ratio = cropped_width / cropped_height
                
                # 计算保持纵横比的尺寸
                if width / height > aspect_ratio:
                    new_height = height
                    new_width = int(height * aspect_ratio)
                else:
                    new_width = width
                    new_height = int(width / aspect_ratio)
                
                # 创建新的图形
                plt.close(fig)  # 关闭旧图形
                fig = plt.figure(figsize=(new_width/100, new_height/100), dpi=100)
                ax = fig.add_subplot(111)
                ax.imshow(cropped_array, interpolation='bilinear')
                ax.axis('off')
                plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)
        
        # 保存图像到缓冲区
        fig.savefig(img_buffer, format='png', bbox_inches='tight', 
                   facecolor=background_color, edgecolor='none', dpi=100)
        
        # 关闭图形，释放内存
        plt.close(fig)
        
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        # 可选：保存词云图片到文件
        save_to_file = data.get('save_to_file', False)
        if save_to_file:
            filename = data.get('filename', f'wordcloud_{shape}_{width}x{height}.png')
            output_path = os.path.join(os.path.dirname(__file__), 'output', filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 将缓冲区内容保存到文件
            with open(output_path, 'wb') as f:
                f.write(img_buffer.getvalue())
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_base64}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/shapes')
def get_shapes():
    """获取可用形状列表"""
    return jsonify({'shapes': list(SHAPE_TEMPLATES.keys())})

@app.route('/fonts')
def get_fonts():
    """获取可用字体列表"""
    return jsonify({'fonts': FONT_OPTIONS})

@app.route('/themes')
def get_themes():
    """获取可用颜色主题列表"""
    return jsonify({'themes': COLOR_THEMES})

def run_app():
    """启动Flask应用"""
    print("🚀 启动词云图生成器...")
    print("📍 应用将在 http://localhost:5000 启动")
    print("🔗 请在浏览器中访问上述地址使用应用")
    print("⏹️  按 Ctrl+C 可以停止应用")
    print("-" * 50)
    
    # 确保在正确的目录中运行
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 自动打开浏览器
    import webbrowser
    import threading
    
    def open_browser():
        """延迟打开浏览器，确保服务器已启动"""
        import time
        time.sleep(1.5)  # 等待1.5秒让服务器完全启动
        webbrowser.open('http://localhost:5000')
    
    # 在新线程中打开浏览器
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 运行Flask应用
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)

def main():
    """主函数"""
    print("🎨 词云图生成器")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--install':
            install_requirements()
            return
        elif sys.argv[1] == '--help':
            print("使用说明:")
            print("  python wordcloud_app.py           - 直接启动应用")
            print("  python wordcloud_app.py --install - 安装依赖")
            print("  python wordcloud_app.py --help    - 显示帮助")
            return
    
    # 检查依赖是否已安装
    try:
        import flask
        import wordcloud
        import numpy
        import PIL
    except ImportError:
        print("⚠️  检测到缺少依赖，正在自动安装...")
        if not install_requirements():
            return
        print()
    
    # 启动应用
    run_app()

if __name__ == '__main__':
    main()