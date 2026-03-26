---
name: 图片优化器
description: "当压缩图片、优化Web性能、转换图片格式、批量处理图片或调整图片尺寸时，提供全面的图片优化和处理解决方案。"
license: MIT
---

# 图片优化器技能

## 概述
图片优化是提升网站性能、减少带宽消耗和改善用户体验的关键技术。通过选择合适的图片格式、压缩算法、尺寸调整和加载策略，可以在保持视觉质量的同时显著减少文件大小。

**核心原则**: 在视觉质量和文件大小之间找到最佳平衡，根据使用场景选择合适的优化策略。

## 何时使用

**始终:**
- 优化网站和移动应用图片
- 减少页面加载时间
- 节省带宽和存储空间
- 准备响应式图片资源
- 批量处理大量图片
- 转换图片格式
- 调整图片尺寸和裁剪
- 生成缩略图和预览图

**触发短语:**
- "图片压缩优化"
- "Web图片性能优化"
- "批量图片处理"
- "图片格式转换"
- "响应式图片设置"
- "图片尺寸调整"
- "图片质量优化"
- "缩略图生成"

## 图片优化技术

### 1. 格式选择
- **JPEG**: 适合照片和复杂图像
- **PNG**: 适合透明背景和简单图形
- **WebP**: 现代格式，更好的压缩率
- **AVIF**: 最新格式，最佳压缩率
- **SVG**: 矢量图形，无限缩放
- **GIF**: 简单动画（考虑用视频替代）

### 2. 压缩策略
- **有损压缩**: 牺牲部分质量换取更小文件
- **无损压缩**: 保持原始质量，减少文件大小
- **智能压缩**: 根据内容自适应调整
- **渐进式加载**: 逐步显示图片内容

### 3. 尺寸优化
- **响应式图片**: 根据设备尺寸提供合适图片
- **多尺寸生成**: 为不同场景准备多个版本
- **智能裁剪**: 保持重要内容
- **分辨率适配**: 根据屏幕密度调整

### 4. 加载优化
- **懒加载**: 延迟加载非关键图片
- **预加载**: 提前加载重要图片
- **CDN分发**: 使用就近服务器
- **缓存策略**: 设置合适的缓存头

## 常见图片问题

### 文件过大问题
```
问题:
图片文件过大影响页面加载速度

症状:
- 页面加载缓慢
- 带宽消耗过高
- 用户体验差
- SEO排名受影响

解决方案:
- 选择合适的图片格式
- 调整压缩质量设置
- 减少不必要的图片尺寸
- 使用现代图片格式
- 实施懒加载策略
```

### 质量损失问题
```
问题:
过度压缩导致图片质量明显下降

症状:
- 图片模糊不清
- 色彩失真
- 细节丢失
- 专业感不足

解决方案:
- 使用渐进式压缩
- 保持关键区域质量
- 选择合适的压缩算法
- 预览压缩效果
- 分区域优化
```

### 格式兼容性问题
```
问题:
某些浏览器不支持现代图片格式

症状:
- 图片无法显示
- 显示错误图标
- 降级到备用格式
- 性能优化失效

解决方案:
- 提供多种格式
- 使用picture元素
- 设置fallback方案
- 检测浏览器支持
- 渐进增强策略
```

## 代码实现示例

### 图片优化器核心类
```python
import os
import io
from PIL import Image, ImageOps, ImageEnhance
from PIL.ExifTags import TAGS
import pillow_avif  # AVIF格式支持
import pillow_webp  # WebP格式支持
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum
import hashlib
from pathlib import Path
import json

class ImageFormat(Enum):
    JPEG = "JPEG"
    PNG = "PNG"
    WEBP = "WEBP"
    AVIF = "AVIF"
    GIF = "GIF"

class OptimizationLevel(Enum):
    LOW = "low"      # 优先质量
    MEDIUM = "medium" # 平衡模式
    HIGH = "high"    # 优先大小

@dataclass
class ImageInfo:
    """图片信息"""
    path: str
    format: str
    size: Tuple[int, int]  # (width, height)
    file_size: int  # bytes
    mode: str  # RGB, RGBA, L等
    has_transparency: bool = False
    color_count: Optional[int] = None
    exif_data: Optional[Dict] = None

@dataclass
class OptimizationResult:
    """优化结果"""
    original_info: ImageInfo
    optimized_info: ImageInfo
    compression_ratio: float
    size_savings: int  # bytes
    quality_score: float  # 0-100
    processing_time: float  # seconds

class ImageOptimizer:
    """图片优化器"""
    
    def __init__(self):
        self.supported_formats = {
            ImageFormat.JPEG: {'quality_range': (1, 95), 'supports_transparency': False},
            ImageFormat.PNG: {'quality_range': (0, 9), 'supports_transparency': True},
            ImageFormat.WEBP: {'quality_range': (0, 100), 'supports_transparency': True},
            ImageFormat.AVIF: {'quality_range': (0, 100), 'supports_transparency': True},
            ImageFormat.GIF: {'quality_range': None, 'supports_transparency': True}
        }
        
    def get_image_info(self, image_path: str) -> ImageInfo:
        """获取图片信息"""
        with Image.open(image_path) as img:
            file_size = os.path.getsize(image_path)
            
            # 检查透明度
            has_transparency = (
                img.mode in ('RGBA', 'LA') or
                (img.mode == 'P' and 'transparency' in img.info)
            )
            
            # 计算颜色数量
            color_count = None
            if img.mode == 'P':
                color_count = len(img.getpalette()) // 3 if img.getpalette() else 256
            elif img.mode == 'RGB':
                color_count = len(set(img.getdata()))
            
            # 提取EXIF数据
            exif_data = {}
            if hasattr(img, '_getexif') and img._getexif() is not None:
                for tag_id, value in img._getexif().items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[tag] = value
            
            return ImageInfo(
                path=image_path,
                format=img.format,
                size=img.size,
                file_size=file_size,
                mode=img.mode,
                has_transparency=has_transparency,
                color_count=color_count,
                exif_data=exif_data
            )
    
    def optimize_image(self, input_path: str, output_path: str,
                      target_format: ImageFormat = None,
                      quality: int = None,
                      max_width: int = None,
                      max_height: int = None,
                      level: OptimizationLevel = OptimizationLevel.MEDIUM) -> OptimizationResult:
        """优化单张图片"""
        import time
        start_time = time.time()
        
        # 获取原始图片信息
        original_info = self.get_image_info(input_path)
        
        # 确定目标格式
        if target_format is None:
            target_format = self._recommend_format(original_info)
        
        # 确定质量设置
        if quality is None:
            quality = self._get_quality_for_level(level, target_format)
        
        with Image.open(input_path) as img:
            # 处理图片方向（基于EXIF）
            img = self._auto_rotate(img)
            
            # 调整尺寸
            if max_width or max_height:
                img = self._resize_image(img, max_width, max_height)
            
            # 移除元数据（可选）
            img = self._clean_metadata(img)
            
            # 保存优化后的图片
            optimized_info = self._save_optimized_image(
                img, output_path, target_format, quality, original_info.has_transparency
            )
        
        processing_time = time.time() - start_time
        
        # 计算优化结果
        compression_ratio = optimized_info.file_size / original_info.file_size
        size_savings = original_info.file_size - optimized_info.file_size
        quality_score = self._calculate_quality_score(original_info, optimized_info)
        
        return OptimizationResult(
            original_info=original_info,
            optimized_info=optimized_info,
            compression_ratio=compression_ratio,
            size_savings=size_savings,
            quality_score=quality_score,
            processing_time=processing_time
        )
    
    def batch_optimize(self, input_dir: str, output_dir: str,
                      file_pattern: str = "*",
                      **kwargs) -> List[OptimizationResult]:
        """批量优化图片"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        # 查找图片文件
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.avif'}
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(input_path.glob(f"{file_pattern}{ext}"))
            image_files.extend(input_path.glob(f"{file_pattern}{ext.upper()}"))
        
        print(f"找到 {len(image_files)} 个图片文件")
        
        for i, image_file in enumerate(image_files, 1):
            print(f"处理 {i}/{len(image_files)}: {image_file.name}")
            
            # 生成输出文件名
            output_file = output_path / f"{image_file.stem}_optimized{image_file.suffix}"
            
            try:
                result = self.optimize_image(str(image_file), str(output_file), **kwargs)
                results.append(result)
                
                print(f"  原始大小: {self._format_size(result.original_info.file_size)}")
                print(f"  优化后大小: {self._format_size(result.optimized_info.file_size)}")
                print(f"  节省空间: {self._format_size(result.size_savings)} ({(1-result.compression_ratio)*100:.1f}%)")
                print(f"  质量评分: {result.quality_score:.1f}/100")
                
            except Exception as e:
                print(f"  错误: {str(e)}")
        
        return results
    
    def create_responsive_images(self, input_path: str, output_dir: str,
                                sizes: List[Tuple[int, str]] = None) -> Dict[str, str]:
        """创建响应式图片"""
        if sizes is None:
            sizes = [
                (320, "small"),
                (768, "medium"),
                (1024, "large"),
                (1920, "xlarge")
            ]
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        with Image.open(input_path) as img:
            original_size = img.size
            generated_files = {}
            
            for width, suffix in sizes:
                # 计算新高度（保持宽高比）
                aspect_ratio = original_size[1] / original_size[0]
                new_height = int(width * aspect_ratio)
                
                # 调整尺寸
                resized_img = img.resize((width, new_height), Image.Resampling.LANCZOS)
                
                # 生成文件名
                input_file = Path(input_path)
                output_file = output_path / f"{input_file.stem}_{suffix}.webp"
                
                # 保存图片
                resized_img.save(output_file, 'WEBP', quality=85, optimize=True)
                generated_files[suffix] = str(output_file)
        
        return generated_files
    
    def generate_thumbnails(self, input_path: str, output_dir: str,
                          thumbnail_sizes: List[Tuple[int, int]] = None) -> List[str]:
        """生成缩略图"""
        if thumbnail_sizes is None:
            thumbnail_sizes = [
                (150, 150),   # 小缩略图
                (300, 300),   # 中缩略图
                (500, 500)    # 大缩略图
            ]
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        with Image.open(input_path) as img:
            # 转换为RGB模式（JPEG不支持透明度）
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            generated_files = []
            input_file = Path(input_path)
            
            for width, height in thumbnail_sizes:
                # 创建缩略图
                img_copy = img.copy()
                img_copy.thumbnail((width, height), Image.Resampling.LANCZOS)
                
                # 居中裁剪到指定尺寸
                left = (img_copy.width - width) // 2
                top = (img_copy.height - height) // 2
                right = left + width
                bottom = top + height
                
                thumbnail = img_copy.crop((left, top, right, bottom))
                
                # 保存缩略图
                suffix = f"{width}x{height}"
                output_file = output_path / f"{input_file.stem}_thumb_{suffix}.jpg"
                thumbnail.save(output_file, 'JPEG', quality=85, optimize=True)
                generated_files.append(str(output_file))
        
        return generated_files
    
    def _recommend_format(self, image_info: ImageInfo) -> ImageFormat:
        """推荐最佳格式"""
        # 如果有透明度，推荐PNG或WebP
        if image_info.has_transparency:
            if image_info.color_count and image_info.color_count < 256:
                return ImageFormat.PNG
            else:
                return ImageFormat.WEBP
        
        # 如果是照片类图像，推荐JPEG或WebP
        if image_info.mode in ('RGB', 'L'):
            return ImageFormat.WEBP  # WebP通常比JPEG更小
        
        # 默认推荐WebP
        return ImageFormat.WEBP
    
    def _get_quality_for_level(self, level: OptimizationLevel, format: ImageFormat) -> int:
        """根据优化级别获取质量设置"""
        quality_settings = {
            OptimizationLevel.LOW: {
                ImageFormat.JPEG: 95,
                ImageFormat.WEBP: 95,
                ImageFormat.AVIF: 95,
                ImageFormat.PNG: 1
            },
            OptimizationLevel.MEDIUM: {
                ImageFormat.JPEG: 85,
                ImageFormat.WEBP: 85,
                ImageFormat.AVIF: 85,
                ImageFormat.PNG: 6
            },
            OptimizationLevel.HIGH: {
                ImageFormat.JPEG: 75,
                ImageFormat.WEBP: 75,
                ImageFormat.AVIF: 75,
                ImageFormat.PNG: 9
            }
        }
        
        return quality_settings[level][format]
    
    def _auto_rotate(self, img: Image) -> Image:
        """根据EXIF自动旋转图片"""
        if hasattr(img, '_getexif'):
            exif = img._getexif()
            if exif is not None:
                orientation_key = 274  # Orientation tag
                if orientation_key in exif:
                    orientation = exif[orientation_key]
                    
                    if orientation == 3:
                        return img.rotate(180, expand=True)
                    elif orientation == 6:
                        return img.rotate(270, expand=True)
                    elif orientation == 8:
                        return img.rotate(90, expand=True)
        
        return img
    
    def _resize_image(self, img: Image, max_width: int, max_height: int) -> Image:
        """调整图片尺寸"""
        original_width, original_height = img.size
        
        # 计算新尺寸
        if max_width and max_height:
            # 按比例缩放
            ratio = min(max_width / original_width, max_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
        elif max_width:
            ratio = max_width / original_width
            new_width = max_width
            new_height = int(original_height * ratio)
        elif max_height:
            ratio = max_height / original_height
            new_width = int(original_width * ratio)
            new_height = max_height
        else:
            return img
        
        # 只在需要缩小时才调整
        if new_width < original_width or new_height < original_height:
            return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return img
    
    def _clean_metadata(self, img: Image) -> Image:
        """清理图片元数据"""
        # 创建新的图片对象，不包含元数据
        if img.mode in ('RGBA', 'LA'):
            cleaned = Image.new(img.mode, img.size)
            cleaned.putdata(list(img.getdata()))
        else:
            cleaned = Image.new('RGB', img.size)
            cleaned.putdata(list(img.getdata()))
        
        return cleaned
    
    def _save_optimized_image(self, img: Image, output_path: str,
                            format: ImageFormat, quality: int,
                            preserve_transparency: bool) -> ImageInfo:
        """保存优化后的图片"""
        save_kwargs = {}
        
        if format == ImageFormat.JPEG:
            if img.mode in ('RGBA', 'LA'):
                # JPEG不支持透明度，添加白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            save_kwargs = {'format': 'JPEG', 'quality': quality, 'optimize': True}
            
        elif format == ImageFormat.PNG:
            save_kwargs = {'format': 'PNG', 'optimize': True, 'compress_level': quality}
            
        elif format == ImageFormat.WEBP:
            save_kwargs = {'format': 'WEBP', 'quality': quality, 'optimize': True, 'method': 6}
            
        elif format == ImageFormat.AVIF:
            save_kwargs = {'format': 'AVIF', 'quality': quality, 'speed': 6}
            
        elif format == ImageFormat.GIF:
            save_kwargs = {'format': 'GIF', 'optimize': True}
        
        img.save(output_path, **save_kwargs)
        
        return self.get_image_info(output_path)
    
    def _calculate_quality_score(self, original: ImageInfo, optimized: ImageInfo) -> float:
        """计算质量评分"""
        # 基于文件大小和格式计算简单质量评分
        size_ratio = optimized.file_size / original.file_size
        
        # 格式质量权重
        format_weights = {
            'JPEG': 0.9,
            'WEBP': 0.95,
            'AVIF': 0.98,
            'PNG': 1.0,
            'GIF': 0.8
        }
        
        format_weight = format_weights.get(optimized.format, 0.9)
        
        # 综合评分
        score = (1 - (1 - size_ratio) * 0.3) * format_weight * 100
        
        return min(100, max(0, score))
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def generate_optimization_report(self, results: List[OptimizationResult]) -> str:
        """生成优化报告"""
        if not results:
            return "没有优化结果"
        
        total_original_size = sum(r.original_info.file_size for r in results)
        total_optimized_size = sum(r.optimized_info.file_size for r in results)
        total_savings = total_original_size - total_optimized_size
        avg_quality_score = sum(r.quality_score for r in results) / len(results)
        avg_compression_ratio = sum(r.compression_ratio for r in results) / len(results)
        
        report = f"""
# 图片优化报告

## 总体统计
- 处理图片数量: {len(results)}
- 原始总大小: {self._format_size(total_original_size)}
- 优化后总大小: {self._format_size(total_optimized_size)}
- 总节省空间: {self._format_size(total_savings)} ({(1-total_optimized_size/total_original_size)*100:.1f}%)
- 平均压缩比: {avg_compression_ratio:.3f}
- 平均质量评分: {avg_quality_score:.1f}/100

## 详细结果

"""
        
        for i, result in enumerate(results, 1):
            report += f"""
### {i}. {Path(result.original_info.path).name}
- **原始格式**: {result.original_info.format} ({result.original_info.size[0]}x{result.original_info.size[1]})
- **优化格式**: {result.optimized_info.format} ({result.optimized_info.size[0]}x{result.optimized_info.size[1]})
- **文件大小**: {self._format_size(result.original_info.file_size)} → {self._format_size(result.optimized_info.file_size)}
- **节省空间**: {self._format_size(result.size_savings)} ({(1-result.compression_ratio)*100:.1f}%)
- **压缩比**: {result.compression_ratio:.3f}
- **质量评分**: {result.quality_score:.1f}/100
- **处理时间**: {result.processing_time:.2f}秒

"""
        
        return report

# 使用示例
def main():
    """示例使用"""
    print("🖼️  图片优化器启动")
    print("=" * 50)
    
    optimizer = ImageOptimizer()
    
    # 示例：优化单张图片
    input_image = "example.jpg"
    output_image = "example_optimized.webp"
    
    if os.path.exists(input_image):
        print(f"优化图片: {input_image}")
        
        result = optimizer.optimize_image(
            input_image, output_image,
            target_format=ImageFormat.WEBP,
            quality=85,
            max_width=1920,
            level=OptimizationLevel.MEDIUM
        )
        
        print(f"✅ 优化完成!")
        print(f"原始大小: {optimizer._format_size(result.original_info.file_size)}")
        print(f"优化后大小: {optimizer._format_size(result.optimized_info.file_size)}")
        print(f"节省空间: {optimizer._format_size(result.size_savings)} ({(1-result.compression_ratio)*100:.1f}%)")
        print(f"质量评分: {result.quality_score:.1f}/100")
        
        # 生成响应式图片
        print(f"\n📱 生成响应式图片...")
        responsive_files = optimizer.create_responsive_images(input_image, "responsive")
        for size, file_path in responsive_files.items():
            print(f"  {size}: {file_path}")
        
        # 生成缩略图
        print(f"\n🖼️  生成缩略图...")
        thumbnails = optimizer.generate_thumbnails(input_image, "thumbnails")
        for thumbnail in thumbnails:
            print(f"  缩略图: {thumbnail}")
    
    else:
        print(f"示例图片 {input_image} 不存在")
        print("请提供一个图片文件进行测试")
    
    print("\n✅ 图片优化器演示完成!")

if __name__ == "__main__":
    main()
```

### Web图片懒加载工具
```python
class ImageLazyLoader:
    """图片懒加载工具"""
    
    def __init__(self):
        self.placeholder_generators = {
            'blur': self._generate_blur_placeholder,
            'color': self._generate_color_placeholder,
            'svg': self._generate_svg_placeholder
        }
    
    def generate_lazy_load_html(self, image_path: str, alt_text: str = "",
                               placeholder_type: str = 'blur',
                               loading_class: str = 'lazy-image') -> str:
        """生成懒加载HTML"""
        
        # 生成占位符
        placeholder = self.placeholder_generators[placeholder_type](image_path)
        
        # 生成HTML
        html = f'''
<img src="{placeholder}"
     data-src="{image_path}"
     alt="{alt_text}"
     class="{loading_class}"
     loading="lazy"
     onerror="this.src='{self._generate_fallback_placeholder()}'"
     onload="this.classList.add('loaded')">
'''
        
        return html.strip()
    
    def generate_picture_element(self, image_variants: Dict[str, str],
                                fallback_path: str, alt_text: str = "") -> str:
        """生成picture元素"""
        sources = []
        
        for media, path in image_variants.items():
            sources.append(f'<source media="{media}" srcset="{path}">')
        
        html = f'''
<picture>
    {''.join(sources)}
    <img src="{fallback_path}" alt="{alt_text}" loading="lazy">
</picture>
'''
        
        return html.strip()
    
    def _generate_blur_placeholder(self, image_path: str) -> str:
        """生成模糊占位符"""
        # 这里应该生成一个小的模糊版本
        # 简化版本，返回base64编码的1x1像素
        return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1' height='1'%3E%3C/svg%3E"
    
    def _generate_color_placeholder(self, image_path: str) -> str:
        """生成颜色占位符"""
        # 这里应该提取图片主色调
        # 简化版本，返回灰色占位符
        return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1' height='1'%3E%3Crect width='1' height='1' fill='%23f0f0f0'/%3E%3C/svg%3E"
    
    def _generate_svg_placeholder(self, image_path: str) -> str:
        """生成SVG占位符"""
        return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Crect width='100' height='100' fill='%23e0e0e0'/%3E%3Ctext x='50' y='50' text-anchor='middle' dy='.3em' fill='%23999' font-family='sans-serif' font-size='14'%3ELoading...%3C/text%3E%3C/svg%3E"
    
    def _generate_fallback_placeholder(self) -> str:
        """生成fallback占位符"""
        return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Crect width='100' height='100' fill='%23ff0000'/%3E%3Ctext x='50' y='50' text-anchor='middle' dy='.3em' fill='white' font-family='sans-serif' font-size='12'%3EError%3C/text%3E%3C/svg%3E"

# 使用示例
def main():
    lazy_loader = ImageLazyLoader()
    print("图片懒加载工具已准备就绪!")

if __name__ == "__main__":
    main()
```

## 图片优化最佳实践

### 格式选择指南
1. **JPEG**: 照片和复杂图像，不支持透明度
2. **PNG**: 简单图形、图标、需要透明度
3. **WebP**: 现代浏览器，更好的压缩率
4. **AVIF**: 最新标准，最佳压缩率
5. **SVG**: 矢量图形、图标、logo

### 压缩策略
1. **质量优先**: 保持高质量，适度压缩
2. **大小优先**: 最大化压缩，可接受质量损失
3. **平衡模式**: 在质量和大小间找到平衡
4. **自适应**: 根据图片内容智能调整

### 响应式设计
1. **多尺寸准备**: 为不同设备提供合适尺寸
2. **艺术指导**: 在不同尺寸下展示不同内容
3. **分辨率切换**: 根据屏幕密度提供合适分辨率
4. **格式降级**: 为不支持新格式的浏览器提供fallback

## 图片优化工具推荐

### 在线工具
- **TinyPNG**: 无损压缩PNG和JPEG
- **Squoosh**: Google开源图片压缩工具
- **ImageOptim**: Mac平台图片优化
- **Kraken.io**: 高级图片优化API

### 命令行工具
- **ImageMagick**: 强大的图片处理工具
- **cwebp**: Google WebP编码器
- **pngquant**: PNG有损压缩
- **jpegoptim**: JPEG优化工具

### 编程库
- **Pillow (Python)**: Python图片处理库
- **Sharp (Node.js)**: 高性能图片处理
- **ImageIO (Java)**: Java图片处理框架
- **libvips**: 高性能图片处理库

## 相关技能

- **web-performance** - Web性能优化
- **frontend-optimization** - 前端优化
- **responsive-design** - 响应式设计
- **image-processing** - 图像处理
- **cdn-optimization** - CDN优化
- **performance-monitoring** - 性能监控
