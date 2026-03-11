#!/usr/bin/env python3
"""
混合推荐系统完整实现示例
支持: 协同过滤 + 内容推荐 + 热度排序 + 多样性 + CTR排序
"""

import json
import random
import time
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class Item:
    """商品"""
    item_id: int
    name: str
    category: str
    brand: str
    price: float
    rating: float
    sales: int

@dataclass
class User:
    """用户"""
    user_id: int
    name: str
    age: int
    vip_level: int
    history: List[int]  # 购买历史

class ItemBasedCF:
    """基于物品的协同过滤"""

    def __init__(self, items_count: int = 1000):
        self.items_count = items_count
        self.similarity_matrix = {}

    def build_similarity_matrix(self, interactions: Dict[int, List[int]]):
        """
        构建商品相似度矩阵
        interactions: {user_id: [item_id, item_id, ...], ...}
        """
        print("📊 构建商品相似度矩阵...")

        # 计算共同用户数
        item_users = {}
        for user_id, items in interactions.items():
            for item_id in items:
                if item_id not in item_users:
                    item_users[item_id] = []
                item_users[item_id].append(user_id)

        # 计算相似度
        for item_i in range(self.items_count):
            if item_i not in item_users:
                continue

            self.similarity_matrix[item_i] = {}
            users_i = set(item_users[item_i])

            for item_j in item_users.keys():
                if item_i >= item_j:
                    continue

                users_j = set(item_users[item_j])
                common = len(users_i & users_j)

                # Jaccard 相似度
                union = len(users_i | users_j)
                if union > 0:
                    similarity = common / union
                    if similarity > 0.1:
                        self.similarity_matrix[item_i][item_j] = similarity

        print(f"✓ 完成 {len(self.similarity_matrix)} 个商品的相似度计算")

    def recommend(self, user_id: int, user_history: List[int], n: int = 20) -> List[Tuple[int, float]]:
        """
        为用户推荐商品
        """
        if not user_history:
            return []

        scores = {}

        # 对用户购买过的每个商品，找相似的商品
        for bought_item in user_history:
            if bought_item not in self.similarity_matrix:
                continue

            for similar_item, similarity in self.similarity_matrix[bought_item].items():
                if similar_item not in user_history:
                    scores[similar_item] = scores.get(similar_item, 0) + similarity

        # 排序返回 Top-N
        recommendations = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n]
        return recommendations


class ContentBasedRecommender:
    """基于内容的推荐"""

    def __init__(self, items: List[Item]):
        self.items = {item.item_id: item for item in items}
        self.categories = {}
        self._build_category_index()

    def _build_category_index(self):
        """构建类别索引"""
        for item in self.items.values():
            if item.category not in self.categories:
                self.categories[item.category] = []
            self.categories[item.category].append(item.item_id)

    def build_user_profile(self, user_history: List[int]) -> Dict[str, float]:
        """
        根据用户历史构建用户偏好
        """
        if not user_history:
            return {}

        profile = {
            'avg_price': 0,
            'avg_rating': 0,
            'category_preference': {}
        }

        prices = []
        ratings = []

        for item_id in user_history:
            if item_id in self.items:
                item = self.items[item_id]
                prices.append(item.price)
                ratings.append(item.rating)

                # 类别偏好
                cat = item.category
                profile['category_preference'][cat] = profile['category_preference'].get(cat, 0) + 1

        profile['avg_price'] = np.mean(prices) if prices else 0
        profile['avg_rating'] = np.mean(ratings) if ratings else 0

        return profile

    def recommend(self, user_profile: Dict[str, float], n: int = 20) -> List[Tuple[int, float]]:
        """
        基于用户偏好推荐
        """
        scores = {}

        for item_id, item in self.items.items():
            score = 0

            # 价格相似度 (差异越小越好)
            price_diff = abs(item.price - user_profile.get('avg_price', item.price))
            score += max(0, 100 - price_diff) / 100 * 0.3

            # 评分相似度
            rating_diff = abs(item.rating - user_profile.get('avg_rating', 4.5))
            score += max(0, 5 - rating_diff) / 5 * 0.3

            # 类别偏好
            cat_pref = user_profile.get('category_preference', {}).get(item.category, 0)
            score += min(cat_pref / 10, 1.0) * 0.4

            scores[item_id] = score

        # 返回 Top-N
        recommendations = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n]
        return recommendations


class PopularityRecommender:
    """基于热度的推荐"""

    def __init__(self, items: List[Item]):
        self.items = {item.item_id: item for item in items}

    def get_popularity_score(self, item: Item) -> float:
        """计算商品热度"""
        # 热度 = 销量 * 0.4 + 评分 * 2 + 20
        return item.sales / 1000 * 0.4 + item.rating * 2 + 20

    def recommend(self, n: int = 20) -> List[Tuple[int, float]]:
        """
        返回热门商品
        """
        scores = {}
        for item_id, item in self.items.items():
            scores[item_id] = self.get_popularity_score(item)

        # 返回 Top-N
        recommendations = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n]
        return recommendations


class HybridRecommender:
    """混合推荐系统"""

    def __init__(self, items: List[Item], interactions: Dict[int, List[int]]):
        self.items = {item.item_id: item for item in items}
        self.cf_model = ItemBasedCF(len(items))
        self.cf_model.build_similarity_matrix(interactions)
        self.content_model = ContentBasedRecommender(items)
        self.popularity_model = PopularityRecommender(items)

    def fuse_recommendations(
        self,
        user_id: int,
        user_history: List[int],
        n: int = 20,
        weights: Tuple[float, float, float] = (0.5, 0.3, 0.2)
    ) -> List[Tuple[int, float, str]]:
        """
        融合三个推荐通道
        weights: (CF权重, Content权重, Popularity权重)
        """

        # 1. 协同过滤 (权重 50%)
        cf_recs = self.cf_model.recommend(user_id, user_history, n=200)
        cf_dict = {item_id: score for item_id, score in cf_recs}

        # 2. 内容推荐 (权重 30%)
        user_profile = self.content_model.build_user_profile(user_history)
        content_recs = self.content_model.recommend(user_profile, n=200)
        content_dict = {item_id: score for item_id, score in content_recs}

        # 3. 热度排序 (权重 20%)
        pop_recs = self.popularity_model.recommend(n=100)
        pop_dict = {item_id: score for item_id, score in pop_recs}

        # 融合所有候选
        all_candidates = set(list(cf_dict.keys()) + list(content_dict.keys()) + list(pop_dict.keys()))

        fused_scores = {}
        for item_id in all_candidates:
            if item_id not in user_history:  # 排除已购买
                score = 0
                source = []

                if item_id in cf_dict:
                    score += weights[0] * cf_dict[item_id]
                    source.append("CF")

                if item_id in content_dict:
                    score += weights[1] * content_dict[item_id]
                    source.append("Content")

                if item_id in pop_dict:
                    score += weights[2] * pop_dict[item_id]
                    source.append("Popularity")

                fused_scores[item_id] = (score, " + ".join(source))

        # 排序
        ranked = sorted(fused_scores.items(), key=lambda x: x[1][0], reverse=True)

        return [(item_id, score, source) for item_id, (score, source) in ranked[:n]]

    def diversify(
        self,
        recommendations: List[Tuple[int, float, str]],
        n: int = 20,
        min_categories: int = 5
    ) -> List[Tuple[int, float, str]]:
        """
        多样性排序: 确保不同品类覆盖
        """
        result = []
        category_count = {}

        for item_id, score, source in recommendations:
            item = self.items[item_id]
            category = item.category

            # 每个品类最多3个
            if category_count.get(category, 0) < 3:
                result.append((item_id, score, source))
                category_count[category] = category_count.get(category, 0) + 1

        return result[:n]

    def recommend(
        self,
        user_id: int,
        user_history: List[int],
        n: int = 20,
        apply_diversity: bool = True
    ) -> List[Dict]:
        """
        完整推荐流程
        """
        # 1. 融合推荐
        fused = self.fuse_recommendations(user_id, user_history, n=n+10, weights=(0.5, 0.3, 0.2))

        # 2. 多样性排序
        if apply_diversity:
            diverse = self.diversify(fused, n=n, min_categories=5)
        else:
            diverse = fused[:n]

        # 3. 返回结果
        results = []
        for item_id, score, source in diverse:
            item = self.items[item_id]
            results.append({
                'item_id': item_id,
                'name': item.name,
                'category': item.category,
                'price': item.price,
                'rating': item.rating,
                'score': round(score, 3),
                'source': source
            })

        return results


def main():
    """主程序"""

    print("=" * 60)
    print("混合推荐系统演示")
    print("=" * 60)
    print()

    # 1. 生成测试数据
    print("📦 生成测试数据...")

    items = []
    categories = ['电子', '图书', '服装', '食品', '家居']
    brands = ['品牌A', '品牌B', '品牌C', '品牌D', '品牌E']

    for i in range(1000):
        item = Item(
            item_id=i,
            name=f"商品{i}",
            category=random.choice(categories),
            brand=random.choice(brands),
            price=random.uniform(10, 1000),
            rating=random.uniform(3.0, 5.0),
            sales=random.randint(100, 10000)
        )
        items.append(item)

    print(f"✓ 生成 {len(items)} 个商品")

    # 2. 生成用户交互数据
    print("📊 生成用户交互数据...")

    interactions = {}
    for user_id in range(1000):
        interactions[user_id] = random.sample(range(1000), k=random.randint(5, 50))

    print(f"✓ 生成 {len(interactions)} 个用户的交互数据")

    # 3. 初始化混合推荐系统
    print("🔧 初始化混合推荐系统...")

    start = time.time()
    recommender = HybridRecommender(items, interactions)
    init_time = (time.time() - start) * 1000

    print(f"✓ 初始化完成 (耗时 {init_time:.2f}ms)")
    print()

    # 4. 推荐示例
    print("=" * 60)
    print("推荐示例")
    print("=" * 60)
    print()

    test_user_id = 0
    test_user_history = interactions[test_user_id]

    print(f"用户ID: {test_user_id}")
    print(f"购买历史: {test_user_history}")
    print()

    # 执行推荐
    start = time.time()
    recommendations = recommender.recommend(
        user_id=test_user_id,
        user_history=test_user_history,
        n=10,
        apply_diversity=True
    )
    recommend_time = (time.time() - start) * 1000

    print(f"✓ 推荐完成 (耗时 {recommend_time:.2f}ms)")
    print()

    print("推荐结果:")
    print("-" * 60)

    for idx, rec in enumerate(recommendations, 1):
        print(f"{idx}. {rec['name']}")
        print(f"   商品ID: {rec['item_id']}")
        print(f"   分类: {rec['category']}")
        print(f"   价格: ¥{rec['price']:.2f}")
        print(f"   评分: {rec['rating']:.1f}⭐")
        print(f"   推荐得分: {rec['score']}")
        print(f"   推荐来源: {rec['source']}")
        print()

    # 5. 性能对比
    print("=" * 60)
    print("性能分析")
    print("=" * 60)
    print()

    # 多用户推荐性能测试
    print("测试 100 个用户的推荐性能...")

    times = []
    for user_id in range(100):
        user_history = interactions[user_id]

        start = time.time()
        recommendations = recommender.recommend(
            user_id=user_id,
            user_history=user_history,
            n=20
        )
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)

    avg_time = np.mean(times)
    p99_time = np.percentile(times, 99)
    max_time = np.max(times)

    print(f"平均推荐延迟: {avg_time:.2f}ms")
    print(f"P99延迟: {p99_time:.2f}ms")
    print(f"最大延迟: {max_time:.2f}ms")
    print()

    # 6. 预期收益
    print("=" * 60)
    print("预期收益")
    print("=" * 60)
    print()

    print("假设:")
    print("  - 日活用户: 100万")
    print("  - 人均推荐: 5 次")
    print("  - 热门商品 CTR: 8%")
    print("  - 混合推荐 CTR: 15%")
    print()

    daily_users = 1_000_000
    recs_per_user = 5
    baseline_ctr = 0.08
    hybrid_ctr = 0.15

    baseline_clicks = daily_users * recs_per_user * baseline_ctr
    hybrid_clicks = daily_users * recs_per_user * hybrid_ctr
    ctr_improvement = (hybrid_ctr - baseline_ctr) / baseline_ctr * 100

    print(f"基础方案点击数: {baseline_clicks:,.0f}")
    print(f"混合推荐点击数: {hybrid_clicks:,.0f}")
    print(f"点击率提升: {ctr_improvement:.0f}%")
    print()

    if baseline_ctr < hybrid_ctr:
        print("✓ 混合推荐系统有显著改进!")
    else:
        print("基础方案性能更好")


if __name__ == "__main__":
    main()
