# 图像优化器参考文档

## 图像优化器概述

### 什么是图像优化器
图像优化器是一个专门用于优化图像文件大小、质量和性能的工具。该工具支持多种图像格式、压缩算法、尺寸调整和智能优化功能，提供批量处理、实时监控、质量控制和性能优化等完整功能，帮助开发团队和应用系统提升图像加载速度、减少存储空间和改善用户体验。

### 主要功能
- **多格式支持**: 支持JPEG、PNG、WebP、GIF、SVG等多种图像格式
- **智能压缩**: 提供有损和无损压缩算法，智能平衡质量和大小
- **尺寸调整**: 支持按比例缩放、固定尺寸和智能裁剪
- **格式转换**: 自动选择最优格式，支持现代图像格式
- **批量处理**: 高效的批量图像处理和并发优化
- **质量控制**: 精确的质量评估和阈值控制

## 图像优化引擎

### 优化处理器
```python
# image_optimizer.py
import os
import io
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import logging
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time
import json

class ImageFormat(Enum):
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    SVG = "svg"
    AVIF = "avif"
    HEIC = "heic"

class CompressionMode(Enum):
    LOSSY = "lossy"
    LOSSLESS = "lossless"
    AUTO = "auto"

class ResizeMode(Enum):
    NONE = "none"
    PROPORTIONAL = "proportional"
    FIXED = "fixed"
    ADAPTIVE = "adaptive"
    SMART = "smart"

class QualityMode(Enum):
    SIZE_PRIORITY = "size_priority"
    QUALITY_PRIORITY = "quality_priority"
    BALANCED = "balanced"

@dataclass
class OptimizationConfig:
    # 基础配置
    input_path: str
    output_path: str
    output_format: Optional[ImageFormat] = None
    compression_mode: CompressionMode = CompressionMode.AUTO
    quality: int = 85
    
    # 尺寸配置
    resize_mode: ResizeMode = ResizeMode.NONE
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    fixed_width: Optional[int] = None
    fixed_height: Optional[int] = None
    
    # 高级配置
    progressive_jpeg: bool = True
    optimize_png: bool = True
    remove_metadata: bool = True
    add_watermark: bool = False
    watermark_text: Optional[str] = None
    watermark_position: str = "bottom_right"
    
    # 性能配置
    use_gpu: bool = False
    thread_count: int = 4
    batch_size: int = 100
    cache_enabled: bool = True
    
    # 质量控制
    min_quality: int = 60
    max_file_size: Optional[int] = None  # KB
    quality_mode: QualityMode = QualityMode.BALANCED

@dataclass
class OptimizationResult:
    success: bool
    input_file: str
    output_file: str
    input_size: int
    output_size: int
    compression_ratio: float
    quality_score: float
    processing_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ImageOptimizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.processed_count = 0
        self.total_input_size = 0
        self.total_output_size = 0
    
    def optimize_image(self, config: OptimizationConfig) -> OptimizationResult:
        """优化单个图像"""
        start_time = time.time()
        
        try:
            # 检查输入文件
            if not os.path.exists(config.input_path):
                return OptimizationResult(
                    success=False,
                    input_file=config.input_path,
                    output_file="",
                    input_size=0,
                    output_size=0,
                    compression_ratio=0,
                    quality_score=0,
                    processing_time=0,
                    error_message="输入文件不存在"
                )
            
            # 获取输入文件大小
            input_size = os.path.getsize(config.input_path)
            
            # 检查缓存
            cache_key = self._get_cache_key(config)
            if config.cache_enabled and cache_key in self.cache:
                cached_result = self.cache[cache_key]
                self.logger.info(f"使用缓存结果: {config.input_path}")
                return cached_result
            
            # 加载图像
            image = self._load_image(config.input_path)
            if image is None:
                return OptimizationResult(
                    success=False,
                    input_file=config.input_path,
                    output_file="",
                    input_size=input_size,
                    output_size=0,
                    compression_ratio=0,
                    quality_score=0,
                    processing_time=0,
                    error_message="无法加载图像"
                )
            
            # 优化图像
            optimized_image = self._optimize_image_data(image, config)
            
            # 保存图像
            output_file = self._save_image(optimized_image, config)
            
            # 获取输出文件大小
            output_size = os.path.getsize(output_file)
            
            # 计算压缩比和质量分数
            compression_ratio = (input_size - output_size) / input_size * 100
            quality_score = self._calculate_quality_score(image, optimized_image)
            
            # 创建结果
            result = OptimizationResult(
                success=True,
                input_file=config.input_path,
                output_file=output_file,
                input_size=input_size,
                output_size=output_size,
                compression_ratio=compression_ratio,
                quality_score=quality_score,
                processing_time=time.time() - start_time,
                metadata={
                    "original_format": image.format,
                    "optimized_format": config.output_format.value if config.output_format else image.format,
                    "original_size": (image.width, image.height),
                    "optimized_size": (optimized_image.width, optimized_image.height)
                }
            )
            
            # 缓存结果
            if config.cache_enabled:
                self.cache[cache_key] = result
            
            # 更新统计
            self._update_statistics(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"优化图像失败 {config.input_path}: {e}")
            return OptimizationResult(
                success=False,
                input_file=config.input_path,
                output_file="",
                input_size=input_size if 'input_size' in locals() else 0,
                output_size=0,
                compression_ratio=0,
                quality_score=0,
                processing_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _load_image(self, file_path: str) -> Optional[Image.Image]:
        """加载图像"""
        try:
            image = Image.open(file_path)
            # 转换为RGB模式（如果需要）
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            return image
        except Exception as e:
            self.logger.error(f"加载图像失败 {file_path}: {e}")
            return None
    
    def _optimize_image_data(self, image: Image.Image, config: OptimizationConfig) -> Image.Image:
        """优化图像数据"""
        optimized = image.copy()
        
        # 尺寸调整
        if config.resize_mode != ResizeMode.NONE:
            optimized = self._resize_image(optimized, config)
        
        # 智能优化
        optimized = self._apply_smart_optimizations(optimized, config)
        
        # 添加水印
        if config.add_watermark and config.watermark_text:
            optimized = self._add_watermark(optimized, config)
        
        return optimized
    
    def _resize_image(self, image: Image.Image, config: OptimizationConfig) -> Image.Image:
        """调整图像尺寸"""
        original_width, original_height = image.size
        
        if config.resize_mode == ResizeMode.PROPORTIONAL:
            # 按比例缩放
            if config.max_width and original_width > config.max_width:
                ratio = config.max_width / original_width
                new_height = int(original_height * ratio)
                image = image.resize((config.max_width, new_height), Image.Resampling.LANCZOS)
            
            if config.max_height and image.size[1] > config.max_height:
                ratio = config.max_height / image.size[1]
                new_width = int(image.size[0] * ratio)
                image = image.resize((new_width, config.max_height), Image.Resampling.LANCZOS)
        
        elif config.resize_mode == ResizeMode.FIXED:
            # 固定尺寸
            new_width = config.fixed_width or original_width
            new_height = config.fixed_height or original_height
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        elif config.resize_mode == ResizeMode.SMART:
            # 智能裁剪
            image = self._smart_crop(image, config)
        
        return image
    
    def _smart_crop(self, image: Image.Image, config: OptimizationConfig) -> Image.Image:
        """智能裁剪"""
        # 这里可以实现基于内容的智能裁剪算法
        # 简化版本：中心裁剪
        target_width = config.max_width or image.width
        target_height = config.max_height or image.height
        
        # 计算裁剪区域
        left = (image.width - target_width) // 2
        top = (image.height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        # 确保裁剪区域在图像范围内
        left = max(0, left)
        top = max(0, top)
        right = min(image.width, right)
        bottom = min(image.height, bottom)
        
        return image.crop((left, top, right, bottom))
    
    def _apply_smart_optimizations(self, image: Image.Image, config: OptimizationConfig) -> Image.Image:
        """应用智能优化"""
        # 锐化处理
        if config.quality_mode == QualityMode.QUALITY_PRIORITY:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
        
        # 对比度调整
        if config.quality_mode == QualityMode.QUALITY_PRIORITY:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.05)
        
        # 降噪处理
        if config.compression_mode == CompressionMode.LOSSY:
            image = image.filter(ImageFilter.MedianFilter(size=3))
        
        return image
    
    def _add_watermark(self, image: Image.Image, config: OptimizationConfig) -> Image.Image:
        """添加水印"""
        from PIL import ImageDraw, ImageFont
        
        # 创建绘制对象
        draw = ImageDraw.Draw(image)
        
        # 尝试加载字体
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        # 计算水印位置
        bbox = draw.textbbox((0, 0), config.watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        margin = 20
        if config.watermark_position == "bottom_right":
            x = image.width - text_width - margin
            y = image.height - text_height - margin
        elif config.watermark_position == "bottom_left":
            x = margin
            y = image.height - text_height - margin
        elif config.watermark_position == "top_right":
            x = image.width - text_width - margin
            y = margin
        else:  # top_left
            x = margin
            y = margin
        
        # 添加半透明水印
        watermark = Image.new('RGBA', image.size, (0, 0, 0, 0))
        watermark_draw = ImageDraw.Draw(watermark)
        watermark_draw.text((x, y), config.watermark_text, font=font, fill=(255, 255, 255, 128))
        
        # 合成水印
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        return Image.alpha_composite(image, watermark)
    
    def _save_image(self, image: Image.Image, config: OptimizationConfig) -> str:
        """保存图像"""
        # 确定输出格式
        output_format = config.output_format or self._detect_best_format(image, config)
        
        # 创建输出目录
        output_dir = os.path.dirname(config.output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 保存参数
        save_kwargs = {}
        
        if output_format == ImageFormat.JPEG:
            save_kwargs.update({
                'format': 'JPEG',
                'quality': config.quality,
                'optimize': True,
                'progressive': config.progressive_jpeg
            })
        elif output_format == ImageFormat.PNG:
            save_kwargs.update({
                'format': 'PNG',
                'optimize': config.optimize_png,
                'compress_level': 6
            })
        elif output_format == ImageFormat.WEBP:
            save_kwargs.update({
                'format': 'WEBP',
                'quality': config.quality,
                'optimize': True,
                'method': 6
            })
        
        # 移除元数据
        if config.remove_metadata:
            image.info = {}
        
        # 保存图像
        image.save(config.output_path, **save_kwargs)
        
        return config.output_path
    
    def _detect_best_format(self, image: Image.Image, config: OptimizationConfig) -> ImageFormat:
        """检测最佳输出格式"""
        # 基于图像内容和使用场景选择最佳格式
        if image.mode == 'RGBA' or 'transparency' in image.info:
            return ImageFormat.PNG
        elif config.quality_mode == QualityMode.SIZE_PRIORITY:
            return ImageFormat.WEBP
        else:
            return ImageFormat.JPEG
    
    def _calculate_quality_score(self, original: Image.Image, optimized: Image.Image) -> float:
        """计算质量分数"""
        # 简化的质量评估，实际应用中可以使用更复杂的算法
        try:
            # 转换为numpy数组
            original_array = np.array(original)
            optimized_array = np.array(optimized)
            
            # 调整尺寸以便比较
            if original_array.shape != optimized_array.shape:
                optimized_array = cv2.resize(optimized_array, 
                                           (original_array.shape[1], original_array.shape[0]))
            
            # 计算PSNR
            mse = np.mean((original_array.astype(float) - optimized_array.astype(float)) ** 2)
            if mse == 0:
                return 100.0
            
            psnr = 20 * np.log10(255.0 / np.sqrt(mse))
            
            # 转换为0-100分数
            quality_score = min(100, max(0, psnr / 0.3))
            
            return quality_score
            
        except Exception as e:
            self.logger.warning(f"计算质量分数失败: {e}")
            return 85.0  # 默认分数
    
    def _get_cache_key(self, config: OptimizationConfig) -> str:
        """生成缓存键"""
        # 基于文件内容和配置生成缓存键
        file_hash = self._get_file_hash(config.input_path)
        config_str = json.dumps(asdict(config), sort_keys=True)
        combined = f"{file_hash}_{config_str}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_file_hash(self, file_path: str) -> str:
        """获取文件哈希"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _update_statistics(self, result: OptimizationResult):
        """更新统计信息"""
        self.processed_count += 1
        self.total_input_size += result.input_size
        self.total_output_size += result.output_size
    
    def optimize_batch(self, configs: List[OptimizationConfig]) -> List[OptimizationResult]:
        """批量优化图像"""
        results = []
        
        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_config = {executor.submit(self.optimize_image, config): config 
                              for config in configs}
            
            for future in future_to_config:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    config = future_to_config[future]
                    self.logger.error(f"批量处理失败 {config.input_path}: {e}")
                    results.append(OptimizationResult(
                        success=False,
                        input_file=config.input_path,
                        output_file="",
                        input_size=0,
                        output_size=0,
                        compression_ratio=0,
                        quality_score=0,
                        processing_time=0,
                        error_message=str(e)
                    ))
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if self.processed_count == 0:
            return {
                "processed_count": 0,
                "total_input_size": 0,
                "total_output_size": 0,
                "total_compression_ratio": 0,
                "average_quality_score": 0
            }
        
        total_compression_ratio = (self.total_input_size - self.total_output_size) / self.total_input_size * 100
        
        return {
            "processed_count": self.processed_count,
            "total_input_size": self.total_input_size,
            "total_output_size": self.total_output_size,
            "total_compression_ratio": total_compression_ratio,
            "cache_size": len(self.cache)
        }

# 使用示例
optimizer = ImageOptimizer()

# 单个图像优化
config = OptimizationConfig(
    input_path="input.jpg",
    output_path="output.jpg",
    output_format=ImageFormat.WEBP,
    compression_mode=CompressionMode.LOSSY,
    quality=80,
    resize_mode=ResizeMode.PROPORTIONAL,
    max_width=1920,
    max_height=1080,
    progressive_jpeg=True,
    remove_metadata=True,
    cache_enabled=True
)

result = optimizer.optimize_image(config)
print(f"优化结果: {result.success}")
print(f"压缩比: {result.compression_ratio:.2f}%")
print(f"质量分数: {result.quality_score:.2f}")
print(f"处理时间: {result.processing_time:.2f}秒")

# 批量优化
configs = []
for i in range(1, 6):
    config = OptimizationConfig(
        input_path=f"image_{i}.jpg",
        output_path=f"optimized_{i}.webp",
        output_format=ImageFormat.WEBP,
        quality=75,
        resize_mode=ResizeMode.PROPORTIONAL,
        max_width=1280,
        max_height=720
    )
    configs.append(config)

batch_results = optimizer.optimize_batch(configs)
print(f"批量优化完成: {len(batch_results)} 个文件")

# 获取统计信息
stats = optimizer.get_statistics()
print(f"统计信息: {stats}")
```

## 智能优化器

### AI驱动优化
```python
# smart_optimizer.py
import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from PIL import Image, ImageEnhance
import tensorflow as tf
from sklearn.cluster import KMeans

class SmartImageOptimizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.content_analyzer = ContentAnalyzer()
        self.quality_predictor = QualityPredictor()
        self.format_selector = FormatSelector()
    
    def smart_optimize(self, image_path: str, output_path: str, 
                      target_size: Optional[int] = None,
                      quality_target: Optional[float] = None) -> Dict[str, Any]:
        """智能优化图像"""
        # 加载图像
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法加载图像: {image_path}")
        
        # 分析图像内容
        content_info = self.content_analyzer.analyze(image)
        
        # 选择最佳格式
        best_format = self.format_selector.select_format(content_info, target_size)
        
        # 预测最佳质量
        optimal_quality = self.quality_predictor.predict_quality(
            image, content_info, target_size, quality_target
        )
        
        # 智能调整尺寸
        optimized_image = self._smart_resize(image, content_info, target_size)
        
        # 智能压缩
        compressed_image = self._smart_compress(optimized_image, optimal_quality, best_format)
        
        # 保存结果
        cv2.imwrite(output_path, compressed_image)
        
        # 返回优化信息
        return {
            "original_size": os.path.getsize(image_path),
            "optimized_size": os.path.getsize(output_path),
            "compression_ratio": (os.path.getsize(image_path) - os.path.getsize(output_path)) / os.path.getsize(image_path) * 100,
            "selected_format": best_format,
            "optimal_quality": optimal_quality,
            "content_info": content_info
        }
    
    def _smart_resize(self, image: np.ndarray, content_info: Dict[str, Any], 
                     target_size: Optional[int]) -> np.ndarray:
        """智能调整尺寸"""
        if target_size is None:
            return image
        
        # 基于内容分析决定调整策略
        if content_info.get("has_faces", False):
            # 有人脸，保持面部区域清晰
            return self._resize_with_face_protection(image, target_size)
        elif content_info.get("has_text", False):
            # 有文字，保持文字清晰
            return self._resize_with_text_protection(image, target_size)
        else:
            # 普通图像，标准调整
            return self._standard_resize(image, target_size)
    
    def _resize_with_face_protection(self, image: np.ndarray, target_size: int) -> np.ndarray:
        """带人脸保护的尺寸调整"""
        # 检测人脸
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return self._standard_resize(image, target_size)
        
        # 保护人脸区域
        h, w = image.shape[:2]
        scale = min(1.0, np.sqrt(target_size * 1000 / (w * h)))
        
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # 使用高质量插值
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        return resized
    
    def _resize_with_text_protection(self, image: np.ndarray, target_size: int) -> np.ndarray:
        """带文字保护的尺寸调整"""
        # 检测文字区域
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 使用MSER检测文字区域
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)
        
        if len(regions) == 0:
            return self._standard_resize(image, target_size)
        
        # 保护文字区域
        h, w = image.shape[:2]
        scale = min(1.0, np.sqrt(target_size * 1000 / (w * h)))
        
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # 使用高质量插值
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        return resized
    
    def _standard_resize(self, image: np.ndarray, target_size: int) -> np.ndarray:
        """标准尺寸调整"""
        h, w = image.shape[:2]
        current_size = w * h
        
        if current_size <= target_size * 1000:
            return image
        
        scale = np.sqrt(target_size * 1000 / current_size)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
    
    def _smart_compress(self, image: np.ndarray, quality: int, format_type: str) -> np.ndarray:
        """智能压缩"""
        if format_type == "jpeg":
            # JPEG压缩
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            _, encoded = cv2.imencode('.jpg', image, encode_param)
            return cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        elif format_type == "webp":
            # WebP压缩
            encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), quality]
            _, encoded = cv2.imencode('.webp', image, encode_param)
            return cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        else:
            return image

class ContentAnalyzer:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def analyze(self, image: np.ndarray) -> Dict[str, Any]:
        """分析图像内容"""
        analysis = {}
        
        # 检测人脸
        analysis["has_faces"] = self._detect_faces(image)
        
        # 检测文字
        analysis["has_text"] = self._detect_text(image)
        
        # 分析颜色分布
        analysis["color_distribution"] = self._analyze_colors(image)
        
        # 分析复杂度
        analysis["complexity"] = self._analyze_complexity(image)
        
        # 分析边缘密度
        analysis["edge_density"] = self._analyze_edges(image)
        
        return analysis
    
    def _detect_faces(self, image: np.ndarray) -> bool:
        """检测人脸"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        return len(faces) > 0
    
    def _detect_text(self, image: np.ndarray) -> bool:
        """检测文字"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 使用MSER检测可能的文字区域
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)
        
        # 简单的文字检测逻辑
        return len(regions) > 10  # 如果有很多区域，可能包含文字
    
    def _analyze_colors(self, image: np.ndarray) -> Dict[str, Any]:
        """分析颜色分布"""
        # 转换为LAB色彩空间
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # 计算颜色直方图
        hist_l = cv2.calcHist([lab], [0], None, [256], [0, 256])
        hist_a = cv2.calcHist([lab], [1], None, [256], [0, 256])
        hist_b = cv2.calcHist([lab], [2], None, [256], [0, 256])
        
        return {
            "luminance_variance": np.var(hist_l),
            "color_variance": np.var(hist_a) + np.var(hist_b),
            "dominant_colors": self._get_dominant_colors(image)
        }
    
    def _get_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[List[int]]:
        """获取主要颜色"""
        # 重塑图像数据
        data = image.reshape((-1, 3))
        data = np.float32(data)
        
        # 使用K-means聚类
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # 转换为整数
        centers = np.uint8(centers)
        
        return centers.tolist()
    
    def _analyze_complexity(self, image: np.ndarray) -> float:
        """分析图像复杂度"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 计算梯度
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # 计算梯度幅值
        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # 复杂度定义为梯度的标准差
        return np.std(magnitude)
    
    def _analyze_edges(self, image: np.ndarray) -> float:
        """分析边缘密度"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # 计算边缘像素比例
        edge_pixels = np.sum(edges > 0)
        total_pixels = edges.size
        
        return edge_pixels / total_pixels

class QualityPredictor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def predict_quality(self, image: np.ndarray, content_info: Dict[str, Any], 
                        target_size: Optional[int], quality_target: Optional[float]) -> int:
        """预测最佳质量设置"""
        base_quality = 85
        
        # 基于内容调整质量
        if content_info.get("has_faces", False):
            base_quality += 5  # 有人脸，提高质量
        
        if content_info.get("has_text", False):
            base_quality += 3  # 有文字，提高质量
        
        # 基于复杂度调整
        complexity = content_info.get("complexity", 0)
        if complexity > 50:
            base_quality -= 5  # 复杂图像，降低质量以获得更好压缩
        
        # 基于目标大小调整
        if target_size:
            current_size = image.shape[0] * image.shape[1]
            if target_size < current_size * 0.5:
                base_quality -= 10  # 需要大幅压缩，降低质量
        
        # 基于质量目标调整
        if quality_target:
            if quality_target > 0.9:
                base_quality = max(base_quality, 90)
            elif quality_target < 0.7:
                base_quality = min(base_quality, 70)
        
        # 确保质量在合理范围内
        return max(30, min(100, base_quality))

class FormatSelector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def select_format(self, content_info: Dict[str, Any], target_size: Optional[int]) -> str:
        """选择最佳格式"""
        # 基于内容和使用场景选择格式
        
        # 如果需要大幅压缩，优先选择WebP
        if target_size and target_size < 500000:  # 500KB以下
            return "webp"
        
        # 如果有透明度，选择PNG
        if content_info.get("has_transparency", False):
            return "png"
        
        # 如果颜色丰富，选择JPEG
        color_variance = content_info.get("color_distribution", {}).get("color_variance", 0)
        if color_variance > 1000:
            return "jpeg"
        
        # 默认选择WebP（现代格式）
        return "webp"

# 使用示例
smart_optimizer = SmartImageOptimizer()

# 智能优化图像
result = smart_optimizer.smart_optimize(
    image_path="input.jpg",
    output_path="smart_output.webp",
    target_size=200000,  # 200KB
    quality_target=0.8
)

print(f"智能优化结果:")
print(f"原始大小: {result['original_size']} 字节")
print(f"优化大小: {result['optimized_size']} 字节")
print(f"压缩比: {result['compression_ratio']:.2f}%")
print(f"选择格式: {result['selected_format']}")
print(f"最佳质量: {result['optimal_quality']}")
print(f"内容信息: {result['content_info']}")
```

## 参考资源

### 图像处理库
- [PIL/Pillow](https://pillow.readthedocs.io/)
- [OpenCV](https://opencv.org/)
- [scikit-image](https://scikit-image.org/)
- [ImageIO](https://imageio.readthedocs.io/)

### 图像格式
- [WebP格式](https://developers.google.com/speed/webp)
- [AVIF格式](https://aomediacodec.github.io/av1-avif/)
- [HEIC格式](https://nokiatech.github.io/heif/)
- [JPEG XL格式](https://jpeg.org/jpegxl/)

### 压缩算法
- [JPEG压缩标准](https://www.jpeg.org/)
- [PNG压缩标准](https://www.w3.org/TR/PNG/)
- [WebP压缩算法](https://developers.google.com/speed/webp/docs/compression)
- [图像质量评估](https://en.wikipedia.org/wiki/Image_quality)

### 性能优化
- [并行处理](https://docs.python.org/3/library/concurrent.futures.html)
- [GPU加速](https://developer.nvidia.com/cuda-zone)
- [内存优化](https://docs.python.org/3/library/memoryview.html)
- [缓存策略](https://docs.python.org/3/library/functools.html)

### 机器学习应用
- [TensorFlow](https://www.tensorflow.org/)
- [PyTorch](https://pytorch.org/)
- [scikit-learn](https://scikit-learn.org/)
- [计算机视觉](https://opencv.org/)
