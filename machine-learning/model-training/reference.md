# 机器学习模型训练参考文档

## 机器学习概述

### 机器学习定义
机器学习是人工智能的一个分支，通过算法使计算机系统能够从数据中学习和改进，而无需明确编程。

### 机器学习类型
- **监督学习**: 从标记数据中学习映射函数
- **无监督学习**: 从未标记数据中发现模式
- **半监督学习**: 结合标记和未标记数据
- **强化学习**: 通过与环境交互学习最优策略
- **深度学习**: 使用神经网络进行复杂模式学习

### 机器学习工作流
1. **问题定义**: 明确业务目标和成功指标
2. **数据收集**: 获取相关数据
3. **数据预处理**: 清洗和准备数据
4. **特征工程**: 创建和选择特征
5. **模型选择**: 选择合适的算法
6. **模型训练**: 训练模型
7. **模型评估**: 评估模型性能
8. **模型部署**: 部署到生产环境
9. **监控维护**: 持续监控和更新

## 数据预处理

### 数据清洗

#### 缺失值处理
```python
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

class MissingValueHandler:
    def __init__(self, df):
        self.df = df.copy()
    
    def analyze_missing_values(self):
        """分析缺失值"""
        missing_info = pd.DataFrame({
            'count': self.df.isnull().sum(),
            'percentage': (self.df.isnull().sum() / len(self.df)) * 100
        })
        return missing_info[missing_info['count'] > 0]
    
    def drop_missing(self, axis=0, threshold=0.5):
        """删除缺失值"""
        if axis == 0:  # 删除行
            min_count = int(threshold * len(self.df.columns))
            self.df = self.df.dropna(thresh=min_count)
        else:  # 删除列
            min_count = int(threshold * len(self.df))
            self.df = self.df.dropna(axis=1, thresh=min_count)
        
        return self.df
    
    def fill_missing_mean(self, columns=None):
        """均值填充"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        imputer = SimpleImputer(strategy='mean')
        self.df[columns] = imputer.fit_transform(self.df[columns])
        return self.df
    
    def fill_missing_median(self, columns=None):
        """中位数填充"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        imputer = SimpleImputer(strategy='median')
        self.df[columns] = imputer.fit_transform(self.df[columns])
        return self.df
    
    def fill_missing_mode(self, columns=None):
        """众数填充"""
        if columns is None:
            columns = self.df.select_dtypes(include=['object']).columns
        
        imputer = SimpleImputer(strategy='most_frequent')
        self.df[columns] = imputer.fit_transform(self.df[columns])
        return self.df
    
    def fill_missing_knn(self, columns=None, n_neighbors=5):
        """KNN填充"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        imputer = KNNImputer(n_neighbors=n_neighbors)
        self.df[columns] = imputer.fit_transform(self.df[columns])
        return self.df
    
    def fill_missing_iterative(self, columns=None):
        """迭代填充"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        imputer = IterativeImputer(random_state=42)
        self.df[columns] = imputer.fit_transform(self.df[columns])
        return self.df

# 使用示例
# 创建示例数据
data = {
    'age': [25, 30, np.nan, 35, 28, np.nan, 40],
    'salary': [50000, 60000, 55000, np.nan, 52000, 58000, np.nan],
    'gender': ['M', 'F', 'M', np.nan, 'F', 'M', 'F'],
    'experience': [2, 5, 3, 8, 4, 6, np.nan]
}

df = pd.DataFrame(data)

# 处理缺失值
handler = MissingValueHandler(df)

# 分析缺失值
missing_analysis = handler.analyze_missing_values()
print("缺失值分析:")
print(missing_analysis)

# 均值填充数值列
handler.fill_missing_mean(['age', 'salary'])

# 众数填充分类列
handler.fill_missing_mode(['gender'])

# KNN填充剩余数值列
handler.fill_missing_knn(['experience'])

print("处理后的数据:")
print(handler.df)
```

#### 异常值检测
```python
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
import matplotlib.pyplot as plt
import seaborn as sns

class OutlierDetector:
    def __init__(self, df):
        self.df = df.copy()
        self.outliers_info = {}
    
    def detect_outliers_iqr(self, columns=None, factor=1.5):
        """IQR方法检测异常值"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        outliers = {}
        
        for col in columns:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - factor * IQR
            upper_bound = Q3 + factor * IQR
            
            outlier_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
            outliers[col] = {
                'indices': self.df[outlier_mask].index.tolist(),
                'values': self.df.loc[outlier_mask, col].tolist(),
                'count': outlier_mask.sum(),
                'percentage': (outlier_mask.sum() / len(self.df)) * 100
            }
        
        self.outliers_info['IQR'] = outliers
        return outliers
    
    def detect_outliers_zscore(self, columns=None, threshold=3):
        """Z-score方法检测异常值"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        outliers = {}
        
        for col in columns:
            z_scores = np.abs(stats.zscore(self.df[col]))
            outlier_mask = z_scores > threshold
            
            outliers[col] = {
                'indices': self.df[outlier_mask].index.tolist(),
                'values': self.df.loc[outlier_mask, col].tolist(),
                'count': outlier_mask.sum(),
                'percentage': (outlier_mask.sum() / len(self.df)) * 100
            }
        
        self.outliers_info['ZScore'] = outliers
        return outliers
    
    def detect_outliers_isolation_forest(self, columns=None, contamination=0.1):
        """孤立森林检测异常值"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        outlier_labels = iso_forest.fit_predict(self.df[columns])
        
        outlier_mask = outlier_labels == -1
        outliers = {
            'indices': self.df[outlier_mask].index.tolist(),
            'count': outlier_mask.sum(),
            'percentage': (outlier_mask.sum() / len(self.df)) * 100
        }
        
        self.outliers_info['IsolationForest'] = outliers
        return outliers
    
    def detect_outliers_one_class_svm(self, columns=None, nu=0.1):
        """单类SVM检测异常值"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        svm = OneClassSVM(nu=nu, kernel='rbf')
        outlier_labels = svm.fit_predict(self.df[columns])
        
        outlier_mask = outlier_labels == -1
        outliers = {
            'indices': self.df[outlier_mask].index.tolist(),
            'count': outlier_mask.sum(),
            'percentage': (outlier_mask.sum() / len(self.df)) * 100
        }
        
        self.outliers_info['OneClassSVM'] = outliers
        return outliers
    
    def remove_outliers(self, method='IQR', columns=None, **kwargs):
        """移除异常值"""
        if method == 'IQR':
            self.detect_outliers_iqr(columns, **kwargs)
            outlier_indices = set()
            for col, info in self.outliers_info['IQR'].items():
                outlier_indices.update(info['indices'])
        
        elif method == 'ZScore':
            self.detect_outliers_zscore(columns, **kwargs)
            outlier_indices = set()
            for col, info in self.outliers_info['ZScore'].items():
                outlier_indices.update(info['indices'])
        
        elif method == 'IsolationForest':
            self.detect_outliers_isolation_forest(columns, **kwargs)
            outlier_indices = set(self.outliers_info['IsolationForest']['indices'])
        
        elif method == 'OneClassSVM':
            self.detect_outliers_one_class_svm(columns, **kwargs)
            outlier_indices = set(self.outliers_info['OneClassSVM']['indices'])
        
        # 移除异常值
        self.df = self.df.drop(outlier_indices)
        print(f"移除了 {len(outlier_indices)} 个异常值")
        
        return self.df
    
    def visualize_outliers(self, column, method='IQR'):
        """可视化异常值"""
        plt.figure(figsize=(12, 4))
        
        # 箱线图
        plt.subplot(1, 2, 1)
        sns.boxplot(x=self.df[column])
        plt.title(f'Boxplot of {column}')
        
        # 直方图
        plt.subplot(1, 2, 2)
        sns.histplot(self.df[column], kde=True)
        plt.title(f'Distribution of {column}')
        
        plt.tight_layout()
        plt.show()
    
    def get_outlier_summary(self):
        """获取异常值摘要"""
        summary = {}
        for method, outliers in self.outliers_info.items():
            if method in ['IQR', 'ZScore']:
                summary[method] = {
                    'total_outliers': sum(info['count'] for info in outliers.values()),
                    'columns_affected': list(outliers.keys()),
                    'details': outliers
                }
            else:
                summary[method] = outliers
        
        return summary

# 使用示例
# 创建包含异常值的数据
np.random.seed(42)
data = {
    'feature1': np.concatenate([np.random.normal(0, 1, 100), np.array([10, -10, 15, -15])]),
    'feature2': np.concatenate([np.random.normal(5, 2, 100), np.array([30, -20, 35, -25])]),
    'feature3': np.random.normal(10, 3, 104)
}

df = pd.DataFrame(data)

# 检测异常值
detector = OutlierDetector(df)

# IQR方法
iqr_outliers = detector.detect_outliers_iqr()
print("IQR异常值检测结果:")
for col, info in iqr_outliers.items():
    print(f"{col}: {info['count']} 个异常值 ({info['percentage']:.2f}%)")

# Z-score方法
zscore_outliers = detector.detect_outliers_zscore()
print("\nZ-score异常值检测结果:")
for col, info in zscore_outliers.items():
    print(f"{col}: {info['count']} 个异常值 ({info['percentage']:.2f}%)")

# 孤立森林
iso_outliers = detector.detect_outliers_isolation_forest()
print(f"\n孤立森林异常值检测结果: {iso_outliers['count']} 个异常值")

# 可视化异常值
detector.visualize_outliers('feature1', 'IQR')

# 移除异常值
df_clean = detector.remove_outliers('IQR')
print(f"\n原始数据形状: {df.shape}")
print(f"清理后数据形状: {df_clean.shape}")
```

### 特征工程

#### 特征选择
```python
import pandas as pd
import numpy as np
from sklearn.feature_selection import (
    SelectKBest, SelectPercentile, RFE, RFECV,
    f_classif, f_regression, chi2, mutual_info_classif, mutual_info_regression
)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt

class FeatureSelector:
    def __init__(self, X, y, task_type='classification'):
        self.X = X
        self.y = y
        self.task_type = task_type
        self.selected_features = {}
        self.feature_scores = {}
    
    def select_univariate(self, method='k_best', k=10, percentile=50):
        """单变量特征选择"""
        if self.task_type == 'classification':
            score_func = f_classif
        else:
            score_func = f_regression
        
        if method == 'k_best':
            selector = SelectKBest(score_func=score_func, k=k)
        elif method == 'percentile':
            selector = SelectPercentile(score_func=score_func, percentile=percentile)
        
        X_selected = selector.fit_transform(self.X, self.y)
        selected_mask = selector.get_support()
        
        selected_features = self.X.columns[selected_mask].tolist()
        feature_scores = dict(zip(self.X.columns, selector.scores_))
        
        self.selected_features['univariate'] = selected_features
        self.feature_scores['univariate'] = feature_scores
        
        return selected_features, feature_scores
    
    def select_rfe(self, estimator=None, n_features_to_select=10, step=1):
        """递归特征消除"""
        if estimator is None:
            if self.task_type == 'classification':
                estimator = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                estimator = RandomForestRegressor(n_estimators=100, random_state=42)
        
        selector = RFE(estimator=estimator, n_features_to_select=n_features_to_select, step=step)
        X_selected = selector.fit_transform(self.X, self.y)
        
        selected_mask = selector.get_support()
        selected_features = self.X.columns[selected_mask].tolist()
        feature_ranking = dict(zip(self.X.columns, selector.ranking_))
        
        self.selected_features['RFE'] = selected_features
        self.feature_scores['RFE'] = feature_ranking
        
        return selected_features, feature_ranking
    
    def select_rfecv(self, estimator=None, cv=5, scoring='accuracy'):
        """交叉验证递归特征消除"""
        if estimator is None:
            if self.task_type == 'classification':
                estimator = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                estimator = RandomForestRegressor(n_estimators=100, random_state=42)
        
        selector = RFECV(estimator=estimator, cv=cv, scoring=scoring)
        X_selected = selector.fit_transform(self.X, self.y)
        
        selected_mask = selector.get_support()
        selected_features = self.X.columns[selected_mask].tolist()
        feature_ranking = dict(zip(self.X.columns, selector.ranking_))
        
        self.selected_features['RFECV'] = selected_features
        self.feature_scores['RFECV'] = feature_ranking
        
        return selected_features, feature_ranking
    
    def select_mutual_info(self, k=10):
        """互信息特征选择"""
        if self.task_type == 'classification':
            score_func = mutual_info_classif
        else:
            score_func = mutual_info_regression
        
        selector = SelectKBest(score_func=score_func, k=k)
        X_selected = selector.fit_transform(self.X, self.y)
        
        selected_mask = selector.get_support()
        selected_features = self.X.columns[selected_mask].tolist()
        feature_scores = dict(zip(self.X.columns, selector.scores_))
        
        self.selected_features['mutual_info'] = selected_features
        self.feature_scores['mutual_info'] = feature_scores
        
        return selected_features, feature_scores
    
    def select_correlation(self, threshold=0.8):
        """相关性特征选择"""
        # 计算特征相关性矩阵
        corr_matrix = self.X.corr().abs()
        
        # 找到高相关性的特征对
        upper_triangle = corr_matrix.where(
            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
        )
        
        # 找到相关性高于阈值的特征
        high_corr_features = [
            column for column in upper_triangle.columns 
            if any(upper_triangle[column] > threshold)
        ]
        
        # 移除高相关性的特征
        selected_features = [
            feature for feature in self.X.columns 
            if feature not in high_corr_features
        ]
        
        self.selected_features['correlation'] = selected_features
        
        return selected_features
    
    def evaluate_feature_importance(self, estimator=None):
        """评估特征重要性"""
        if estimator is None:
            if self.task_type == 'classification':
                estimator = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                estimator = RandomForestRegressor(n_estimators=100, random_state=42)
        
        estimator.fit(self.X, self.y)
        
        if hasattr(estimator, 'feature_importances_'):
            feature_importance = dict(zip(self.X.columns, estimator.feature_importances_))
        elif hasattr(estimator, 'coef_'):
            feature_importance = dict(zip(self.X.columns, np.abs(estimator.coef_).flatten()))
        else:
            feature_importance = {}
        
        self.feature_scores['importance'] = feature_importance
        
        return feature_importance
    
    def plot_feature_scores(self, method='univariate', top_k=20):
        """绘制特征分数"""
        if method not in self.feature_scores:
            print(f"方法 {method} 尚未执行")
            return
        
        scores = self.feature_scores[method]
        
        # 排序并选择前k个特征
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        features, values = zip(*sorted_scores)
        
        plt.figure(figsize=(12, 6))
        plt.barh(range(len(features)), values)
        plt.yticks(range(len(features)), features)
        plt.xlabel('Score')
        plt.title(f'Top {top_k} Features by {method}')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.show()
    
    def get_consensus_features(self, methods=None, min_votes=2):
        """获取共识特征"""
        if methods is None:
            methods = list(self.selected_features.keys())
        
        feature_votes = {}
        
        for method in methods:
            if method in self.selected_features:
                for feature in self.selected_features[method]:
                    feature_votes[feature] = feature_votes.get(feature, 0) + 1
        
        consensus_features = [
            feature for feature, votes in feature_votes.items() 
            if votes >= min_votes
        ]
        
        return consensus_features, feature_votes

# 使用示例
from sklearn.datasets import make_classification, make_regression

# 分类任务示例
X_clf, y_clf = make_classification(
    n_samples=1000, n_features=50, n_informative=20, 
    n_redundant=10, n_repeated=5, random_state=42
)

X_clf_df = pd.DataFrame(X_clf, columns=[f'feature_{i}' for i in range(50)])

# 特征选择
selector = FeatureSelector(X_clf_df, y_clf, task_type='classification')

# 单变量特征选择
univariate_features, univariate_scores = selector.select_univariate(k=20)
print(f"单变量选择的特征: {len(univariate_features)}")

# 递归特征消除
rfe_features, rfe_scores = selector.select_rfe(n_features_to_select=15)
print(f"RFE选择的特征: {len(rfe_features)}")

# 互信息特征选择
mi_features, mi_scores = selector.select_mutual_info(k=20)
print(f"互信息选择的特征: {len(mi_features)}")

# 特征重要性
importance_scores = selector.evaluate_feature_importance()

# 绘制特征分数
selector.plot_feature_scores('univariate', top_k=15)

# 获取共识特征
consensus_features, votes = selector.get_consensus_features(min_votes=2)
print(f"共识特征: {len(consensus_features)}")
```

#### 特征变换
```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler,
    PowerTransformer, QuantileTransformer, Normalizer
)
from sklearn.decomposition import PCA, FastICA, TruncatedSVD
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns

class FeatureTransformer:
    def __init__(self, df):
        self.df = df.copy()
        self.transformed_data = {}
        self.scalers = {}
    
    def scale_standard(self, columns=None):
        """标准化变换"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        scaler = StandardScaler()
        self.df[columns] = scaler.fit_transform(self.df[columns])
        self.scalers['standard'] = scaler
        
        self.transformed_data['standard'] = self.df[columns].copy()
        return self.df
    
    def scale_minmax(self, columns=None, feature_range=(0, 1)):
        """最小-最大归一化"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        scaler = MinMaxScaler(feature_range=feature_range)
        self.df[columns] = scaler.fit_transform(self.df[columns])
        self.scalers['minmax'] = scaler
        
        self.transformed_data['minmax'] = self.df[columns].copy()
        return self.df
    
    def scale_robust(self, columns=None):
        """鲁棒缩放"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        scaler = RobustScaler()
        self.df[columns] = scaler.fit_transform(self.df[columns])
        self.scalers['robust'] = scaler
        
        self.transformed_data['robust'] = self.df[columns].copy()
        return self.df
    
    def scale_maxabs(self, columns=None):
        """最大绝对值缩放"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        scaler = MaxAbsScaler()
        self.df[columns] = scaler.fit_transform(self.df[columns])
        self.scalers['maxabs'] = scaler
        
        self.transformed_data['maxabs'] = self.df[columns].copy()
        return self.df
    
    def transform_power(self, columns=None, method='yeo-johnson'):
        """幂变换"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        transformer = PowerTransformer(method=method)
        self.df[columns] = transformer.fit_transform(self.df[columns])
        self.scalers['power'] = transformer
        
        self.transformed_data['power'] = self.df[columns].copy()
        return self.df
    
    def transform_quantile(self, columns=None, n_quantiles=1000, output_distribution='normal'):
        """分位数变换"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        transformer = QuantileTransformer(
            n_quantiles=n_quantiles, 
            output_distribution=output_distribution
        )
        self.df[columns] = transformer.fit_transform(self.df[columns])
        self.scalers['quantile'] = transformer
        
        self.transformed_data['quantile'] = self.df[columns].copy()
        return self.df
    
    def apply_pca(self, columns=None, n_components=2):
        """主成分分析"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        pca = PCA(n_components=n_components)
        pca_result = pca.fit_transform(self.df[columns])
        
        # 创建PCA特征列名
        pca_columns = [f'PCA_{i+1}' for i in range(n_components)]
        pca_df = pd.DataFrame(pca_result, columns=pca_columns, index=self.df.index)
        
        self.df[pca_columns] = pca_df
        self.scalers['pca'] = pca
        
        self.transformed_data['pca'] = pca_df
        
        print(f"PCA解释方差比例: {pca.explained_variance_ratio_}")
        print(f"总解释方差比例: {pca.explained_variance_ratio_.sum():.3f}")
        
        return self.df, pca
    
    def apply_ica(self, columns=None, n_components=2):
        """独立成分分析"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        ica = FastICA(n_components=n_components, random_state=42)
        ica_result = ica.fit_transform(self.df[columns])
        
        # 创建ICA特征列名
        ica_columns = [f'ICA_{i+1}' for i in range(n_components)]
        ica_df = pd.DataFrame(ica_result, columns=ica_columns, index=self.df.index)
        
        self.df[ica_columns] = ica_df
        self.scalers['ica'] = ica
        
        self.transformed_data['ica'] = ica_df
        
        return self.df, ica
    
    def apply_tsne(self, columns=None, n_components=2, perplexity=30):
        """t-SNE降维"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        tsne = TSNE(n_components=n_components, perplexity=perplexity, random_state=42)
        tsne_result = tsne.fit_transform(self.df[columns])
        
        # 创建t-SNE特征列名
        tsne_columns = [f'tSNE_{i+1}' for i in range(n_components)]
        tsne_df = pd.DataFrame(tsne_result, columns=tsne_columns, index=self.df.index)
        
        self.df[tsne_columns] = tsne_df
        self.scalers['tsne'] = tsne
        
        self.transformed_data['tsne'] = tsne_df
        
        return self.df, tsne
    
    def create_polynomial_features(self, columns=None, degree=2):
        """创建多项式特征"""
        from sklearn.preprocessing import PolynomialFeatures
        
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        poly = PolynomialFeatures(degree=degree, include_bias=False)
        poly_features = poly.fit_transform(self.df[columns])
        
        # 创建多项式特征列名
        feature_names = poly.get_feature_names_out(columns)
        poly_df = pd.DataFrame(poly_features, columns=feature_names, index=self.df.index)
        
        # 只添加新的特征（不包括原始特征）
        new_features = [name for name in feature_names if name not in columns]
        self.df[new_features] = poly_df[new_features]
        
        self.scalers['polynomial'] = poly
        self.transformed_data['polynomial'] = poly_df[new_features]
        
        return self.df
    
    def create_interaction_features(self, columns=None):
        """创建交互特征"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        # 创建两两交互特征
        for i, col1 in enumerate(columns):
            for col2 in columns[i+1:]:
                interaction_name = f'{col1}_x_{col2}'
                self.df[interaction_name] = self.df[col1] * self.df[col2]
        
        return self.df
    
    def visualize_distribution(self, column, before_after=True):
        """可视化分布变换"""
        if before_after and 'original' not in self.transformed_data:
            # 保存原始数据
            self.transformed_data['original'] = self.df[[column]].copy()
        
        plt.figure(figsize=(15, 5))
        
        if before_after and 'original' in self.transformed_data:
            # 原始分布
            plt.subplot(1, 3, 1)
            sns.histplot(self.transformed_data['original'][column], kde=True)
            plt.title(f'Original {column}')
            
            # 变换后分布
            plt.subplot(1, 3, 2)
            sns.histplot(self.df[column], kde=True)
            plt.title(f'Transformed {column}')
            
            # Q-Q图
            plt.subplot(1, 3, 3)
            stats.probplot(self.df[column], dist="norm", plot=plt)
            plt.title(f'Q-Q Plot {column}')
        else:
            # 只显示当前分布
            plt.subplot(1, 2, 1)
            sns.histplot(self.df[column], kde=True)
            plt.title(f'Distribution of {column}')
            
            # Q-Q图
            plt.subplot(1, 2, 2)
            stats.probplot(self.df[column], dist="norm", plot=plt)
            plt.title(f'Q-Q Plot {column}')
        
        plt.tight_layout()
        plt.show()
    
    def compare_transformations(self, column, methods=None):
        """比较不同变换方法"""
        if methods is None:
            methods = ['standard', 'minmax', 'robust', 'power', 'quantile']
        
        # 保存原始数据
        original_data = self.df[column].copy()
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        axes = axes.flatten()
        
        # 原始分布
        sns.histplot(original_data, kde=True, ax=axes[0])
        axes[0].set_title('Original')
        
        # 各种变换
        for i, method in enumerate(methods[:5]):
            if method == 'standard':
                transformed = StandardScaler().fit_transform(original_data.values.reshape(-1, 1)).flatten()
            elif method == 'minmax':
                transformed = MinMaxScaler().fit_transform(original_data.values.reshape(-1, 1)).flatten()
            elif method == 'robust':
                transformed = RobustScaler().fit_transform(original_data.values.reshape(-1, 1)).flatten()
            elif method == 'power':
                transformed = PowerTransformer().fit_transform(original_data.values.reshape(-1, 1)).flatten()
            elif method == 'quantile':
                transformed = QuantileTransformer().fit_transform(original_data.values.reshape(-1, 1)).flatten()
            
            sns.histplot(transformed, kde=True, ax=axes[i+1])
            axes[i+1].set_title(method)
        
        plt.tight_layout()
        plt.show()

# 使用示例
# 创建示例数据
np.random.seed(42)
data = {
    'normal_feature': np.random.normal(0, 1, 1000),
    'skewed_feature': np.random.exponential(2, 1000),
    'uniform_feature': np.random.uniform(0, 10, 1000),
    'categorical_feature': np.random.choice(['A', 'B', 'C'], 1000)
}

df = pd.DataFrame(data)

# 特征变换
transformer = FeatureTransformer(df)

# 标准化
transformer.scale_standard(['normal_feature', 'skewed_feature', 'uniform_feature'])

# 幂变换（处理偏态数据）
transformer.transform_power(['skewed_feature'])

# PCA降维
transformer.apply_pca(['normal_feature', 'skewed_feature', 'uniform_feature'], n_components=2)

# 创建多项式特征
transformer.create_polynomial_features(['normal_feature', 'uniform_feature'], degree=2)

# 可视化变换效果
transformer.visualize_distribution('skewed_feature')

# 比较不同变换方法
transformer.compare_transformations('skewed_feature')

print("变换后的数据形状:", transformer.df.shape)
print("新增的列:", [col for col in transformer.df.columns if col not in df.columns])
```

## 模型训练

### 传统机器学习模型

#### 分类模型训练
```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
import xgboost as xgb
import lightgbm as lgb
import matplotlib.pyplot as plt
import seaborn as sns

class ClassificationTrainer:
    def __init__(self, X, y, test_size=0.2, random_state=42):
        self.X = X
        self.y = y
        self.test_size = test_size
        self.random_state = random_state
        self.models = {}
        self.best_models = {}
        self.evaluation_results = {}
        
        # 分割数据
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # 特征缩放
        self.scaler = StandardScaler()
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)
    
    def train_logistic_regression(self, **params):
        """训练逻辑回归"""
        default_params = {
            'random_state': self.random_state,
            'max_iter': 1000
        }
        default_params.update(params)
        
        model = LogisticRegression(**default_params)
        model.fit(self.X_train_scaled, self.y_train)
        
        self.models['logistic_regression'] = model
        return model
    
    def train_decision_tree(self, **params):
        """训练决策树"""
        default_params = {'random_state': self.random_state}
        default_params.update(params)
        
        model = DecisionTreeClassifier(**default_params)
        model.fit(self.X_train, self.y_train)
        
        self.models['decision_tree'] = model
        return model
    
    def train_random_forest(self, **params):
        """训练随机森林"""
        default_params = {
            'n_estimators': 100,
            'random_state': self.random_state
        }
        default_params.update(params)
        
        model = RandomForestClassifier(**default_params)
        model.fit(self.X_train, self.y_train)
        
        self.models['random_forest'] = model
        return model
    
    def train_gradient_boosting(self, **params):
        """训练梯度提升"""
        default_params = {
            'n_estimators': 100,
            'random_state': self.random_state
        }
        default_params.update(params)
        
        model = GradientBoostingClassifier(**default_params)
        model.fit(self.X_train, self.y_train)
        
        self.models['gradient_boosting'] = model
        return model
    
    def train_xgboost(self, **params):
        """训练XGBoost"""
        default_params = {
            'n_estimators': 100,
            'random_state': self.random_state,
            'eval_metric': 'logloss'
        }
        default_params.update(params)
        
        model = xgb.XGBClassifier(**default_params)
        model.fit(self.X_train, self.y_train)
        
        self.models['xgboost'] = model
        return model
    
    def train_lightgbm(self, **params):
        """训练LightGBM"""
        default_params = {
            'n_estimators': 100,
            'random_state': self.random_state,
            'verbosity': -1
        }
        default_params.update(params)
        
        model = lgb.LGBMClassifier(**default_params)
        model.fit(self.X_train, self.y_train)
        
        self.models['lightgbm'] = model
        return model
    
    def train_svm(self, **params):
        """训练支持向量机"""
        default_params = {
            'random_state': self.random_state,
            'probability': True
        }
        default_params.update(params)
        
        model = SVC(**default_params)
        model.fit(self.X_train_scaled, self.y_train)
        
        self.models['svm'] = model
        return model
    
    def train_knn(self, **params):
        """训练K近邻"""
        default_params = {'n_neighbors': 5}
        default_params.update(params)
        
        model = KNeighborsClassifier(**default_params)
        model.fit(self.X_train_scaled, self.y_train)
        
        self.models['knn'] = model
        return model
    
    def train_naive_bayes(self, **params):
        """训练朴素贝叶斯"""
        model = GaussianNB(**params)
        model.fit(self.X_train, self.y_train)
        
        self.models['naive_bayes'] = model
        return model
    
    def evaluate_model(self, model_name, model=None):
        """评估模型"""
        if model is None:
            if model_name not in self.models:
                raise ValueError(f"模型 {model_name} 尚未训练")
            model = self.models[model_name]
        
        # 选择适当的数据（是否需要缩放）
        if model_name in ['logistic_regression', 'svm', 'knn']:
            X_train_eval = self.X_train_scaled
            X_test_eval = self.X_test_scaled
        else:
            X_train_eval = self.X_train
            X_test_eval = self.X_test
        
        # 预测
        y_train_pred = model.predict(X_train_eval)
        y_test_pred = model.predict(X_test_eval)
        
        # 预测概率
        if hasattr(model, 'predict_proba'):
            y_train_proba = model.predict_proba(X_train_eval)
            y_test_proba = model.predict_proba(X_test_eval)
        else:
            y_train_proba = None
            y_test_proba = None
        
        # 计算指标
        metrics = {
            'train_accuracy': accuracy_score(self.y_train, y_train_pred),
            'test_accuracy': accuracy_score(self.y_test, y_test_pred),
            'train_precision': precision_score(self.y_train, y_train_pred, average='weighted'),
            'test_precision': precision_score(self.y_test, y_test_pred, average='weighted'),
            'train_recall': recall_score(self.y_train, y_train_pred, average='weighted'),
            'test_recall': recall_score(self.y_test, y_test_pred, average='weighted'),
            'train_f1': f1_score(self.y_train, y_train_pred, average='weighted'),
            'test_f1': f1_score(self.y_test, y_test_pred, average='weighted')
        }
        
        # AUC-ROC（二分类）
        if len(np.unique(self.y)) == 2 and y_test_proba is not None:
            metrics['train_auc'] = roc_auc_score(self.y_train, y_train_proba[:, 1])
            metrics['test_auc'] = roc_auc_score(self.y_test, y_test_proba[:, 1])
        
        self.evaluation_results[model_name] = metrics
        
        return metrics
    
    def compare_models(self):
        """比较所有模型"""
        results = []
        
        for model_name in self.models.keys():
            metrics = self.evaluate_model(model_name)
            metrics['model'] = model_name
            results.append(metrics)
        
        results_df = pd.DataFrame(results)
        results_df = results_df.set_index('model')
        
        return results_df
    
    def hyperparameter_tuning(self, model_name, param_grid, search_type='grid', cv=5, scoring='accuracy'):
        """超参数调优"""
        # 选择模型
        if model_name == 'logistic_regression':
            model = LogisticRegression(random_state=self.random_state, max_iter=1000)
            X_train = self.X_train_scaled
        elif model_name == 'decision_tree':
            model = DecisionTreeClassifier(random_state=self.random_state)
            X_train = self.X_train
        elif model_name == 'random_forest':
            model = RandomForestClassifier(random_state=self.random_state)
            X_train = self.X_train
        elif model_name == 'gradient_boosting':
            model = GradientBoostingClassifier(random_state=self.random_state)
            X_train = self.X_train
        elif model_name == 'xgboost':
            model = xgb.XGBClassifier(random_state=self.random_state)
            X_train = self.X_train
        elif model_name == 'lightgbm':
            model = lgb.LGBMClassifier(random_state=self.random_state, verbosity=-1)
            X_train = self.X_train
        elif model_name == 'svm':
            model = SVC(random_state=self.random_state, probability=True)
            X_train = self.X_train_scaled
        elif model_name == 'knn':
            model = KNeighborsClassifier()
            X_train = self.X_train_scaled
        else:
            raise ValueError(f"不支持的模型: {model_name}")
        
        # 超参数搜索
        if search_type == 'grid':
            search = GridSearchCV(model, param_grid, cv=cv, scoring=scoring, n_jobs=-1)
        elif search_type == 'random':
            search = RandomizedSearchCV(model, param_grid, cv=cv, scoring=scoring, n_jobs=-1, n_iter=50)
        else:
            raise ValueError("search_type 必须是 'grid' 或 'random'")
        
        search.fit(X_train, self.y_train)
        
        # 保存最佳模型
        self.best_models[model_name] = search.best_estimator_
        
        print(f"最佳参数: {search.best_params_}")
        print(f"最佳分数: {search.best_score_:.4f}")
        
        return search.best_estimator_, search.best_params_, search.best_score_
    
    def plot_confusion_matrix(self, model_name, model=None):
        """绘制混淆矩阵"""
        if model is None:
            if model_name not in self.models:
                raise ValueError(f"模型 {model_name} 尚未训练")
            model = self.models[model_name]
        
        # 选择适当的数据
        if model_name in ['logistic_regression', 'svm', 'knn']:
            X_test_eval = self.X_test_scaled
        else:
            X_test_eval = self.X_test
        
        y_pred = model.predict(X_test_eval)
        cm = confusion_matrix(self.y_test, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f'Confusion Matrix - {model_name}')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.show()
    
    def plot_feature_importance(self, model_name, top_features=20):
        """绘制特征重要性"""
        if model_name not in self.models:
            raise ValueError(f"模型 {model_name} 尚未训练")
        
        model = self.models[model_name]
        
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_names = self.X.columns
            
            # 排序
            indices = np.argsort(importances)[::-1][:top_features]
            
            plt.figure(figsize=(10, 6))
            plt.title(f'Feature Importance - {model_name}')
            plt.bar(range(top_features), importances[indices])
            plt.xticks(range(top_features), feature_names[indices], rotation=45, ha='right')
            plt.tight_layout()
            plt.show()
        else:
            print(f"模型 {model_name} 不支持特征重要性")

# 使用示例
from sklearn.datasets import make_classification

# 创建分类数据集
X, y = make_classification(
    n_samples=1000, n_features=20, n_informative=15,
    n_redundant=5, n_classes=2, random_state=42
)

X_df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(20)])

# 训练分类器
trainer = ClassificationTrainer(X_df, y)

# 训练多个模型
trainer.train_logistic_regression()
trainer.train_random_forest()
trainer.train_xgboost()
trainer.train_lightgbm()

# 比较模型性能
results = trainer.compare_models()
print("模型比较结果:")
print(results)

# 超参数调优示例
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [3, 5, 7, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

best_rf, best_params, best_score = trainer.hyperparameter_tuning(
    'random_forest', param_grid, search_type='random'
)

# 绘制混淆矩阵
trainer.plot_confusion_matrix('random_forest')

# 绘制特征重要性
trainer.plot_feature_importance('random_forest', top_features=10)
```

#### 回归模型训练
```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    mean_absolute_percentage_error
)
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
import xgboost as xgb
import lightgbm as lgb
import matplotlib.pyplot as plt
import seaborn as sns

class RegressionTrainer:
    def __init__(self, X, y, test_size=0.2, random_state=42):
        self.X = X
        self.y = y
        self.test_size = test_size
        self.random_state = random_state
        self.models = {}
        self.best_models = {}
        self.evaluation_results = {}
        
        # 分割数据
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # 特征缩放
        self.scaler = StandardScaler()
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)
    
    def train_linear_regression(self):
        """训练线性回归"""
        model = LinearRegression()
        model.fit(self.X_train, self.y_train)
        
        self.models['linear_regression'] = model
        return model
    
    def train_ridge(self, **params):
        """训练岭回归"""
        default_params = {'random_state': self.random_state}
        default_params.update(params)
        
        model = Ridge(**default_params)
        model.fit(self.X_train, self.y_train)
        
        self.models['ridge'] = model
        return model
    
    def train_lasso(self, **params):
        """训练Lasso回归"""
        default_params = {'random_state': self.random_state}
        default_params.update(params)
        
        model = Lasso(**default_params)
        model.fit(self.X_train, self.y_train)
        
        self.models['lasso'] = model
        return model
    
    def train_elastic_net(self, **params):
        """训练弹性网络"""
        default_params = {'random_state': self.random_state}
        default_params.update(params)
        
        model = ElasticNet(**default_params)
        model.fit(self.X_train, self.y_train)
        
        self.models['elastic_net'] = model
        return model
    
    def train_decision_tree(self, **params):
        """训练决策树回归"""
        default_params = {'random_state': self.random_state}
        default_params.update(params)
        
        model = DecisionTreeRegressor(**default_params)
        model.fit(self.X_train, self.y_train)
        
        self.models['decision_tree'] = model
        return model
    
    def train_random_forest(self, **params):
        """训练随机森林回归"""
        default_params = {
            'n_estimators': 100,
            'random_state': self.random_state
        }
        default_params.update(params)
        
        model = RandomForestRegressor(**default_params)
        model.fit(self.X_train, self.y_train)
        
        self.models['random_forest'] = model
        return model
    
    def train_gradient_boosting(self, **params):
        """训练梯度提升回归"""
        default_params = {
            'n_estimators': 100,
            'random_state': self.random_state
        }
        default_params.update(params)
        
        model = GradientBoostingRegressor(**default_params)
        model.fit(self.X_train, self.y_train)
        
        self.models['gradient_boosting'] = model
        return model
    
    def train_xgboost(self, **params):
        """训练XGBoost回归"""
        default_params = {
            'n_estimators': 100,
            'random_state': self.random_state
        }
        default_params.update(params)
        
        model = xgb.XGBRegressor(**default_params)
        model.fit(self.X_train, self.y_train)
        
        self.models['xgboost'] = model
        return model
    
    def train_lightgbm(self, **params):
        """训练LightGBM回归"""
        default_params = {
            'n_estimators': 100,
            'random_state': self.random_state,
            'verbosity': -1
        }
        default_params.update(params)
        
        model = lgb.LGBMRegressor(**default_params)
        model.fit(self.X_train, self.y_train)
        
        self.models['lightgbm'] = model
        return model
    
    def train_svr(self, **params):
        """训练支持向量回归"""
        default_params = {}
        default_params.update(params)
        
        model = SVR(**default_params)
        model.fit(self.X_train_scaled, self.y_train)
        
        self.models['svr'] = model
        return model
    
    def train_knn(self, **params):
        """训练K近邻回归"""
        default_params = {'n_neighbors': 5}
        default_params.update(params)
        
        model = KNeighborsRegressor(**default_params)
        model.fit(self.X_train_scaled, self.y_train)
        
        self.models['knn'] = model
        return model
    
    def evaluate_model(self, model_name, model=None):
        """评估回归模型"""
        if model is None:
            if model_name not in self.models:
                raise ValueError(f"模型 {model_name} 尚未训练")
            model = self.models[model_name]
        
        # 选择适当的数据（是否需要缩放）
        if model_name in ['svr', 'knn']:
            X_train_eval = self.X_train_scaled
            X_test_eval = self.X_test_scaled
        else:
            X_train_eval = self.X_train
            X_test_eval = self.X_test
        
        # 预测
        y_train_pred = model.predict(X_train_eval)
        y_test_pred = model.predict(X_test_eval)
        
        # 计算指标
        metrics = {
            'train_mse': mean_squared_error(self.y_train, y_train_pred),
            'test_mse': mean_squared_error(self.y_test, y_test_pred),
            'train_rmse': np.sqrt(mean_squared_error(self.y_train, y_train_pred)),
            'test_rmse': np.sqrt(mean_squared_error(self.y_test, y_test_pred)),
            'train_mae': mean_absolute_error(self.y_train, y_train_pred),
            'test_mae': mean_absolute_error(self.y_test, y_test_pred),
            'train_r2': r2_score(self.y_train, y_train_pred),
            'test_r2': r2_score(self.y_test, y_test_pred),
            'train_mape': mean_absolute_percentage_error(self.y_train, y_train_pred),
            'test_mape': mean_absolute_percentage_error(self.y_test, y_test_pred)
        }
        
        self.evaluation_results[model_name] = metrics
        
        return metrics
    
    def compare_models(self):
        """比较所有回归模型"""
        results = []
        
        for model_name in self.models.keys():
            metrics = self.evaluate_model(model_name)
            metrics['model'] = model_name
            results.append(metrics)
        
        results_df = pd.DataFrame(results)
        results_df = results_df.set_index('model')
        
        return results_df
    
    def plot_predictions(self, model_name, model=None):
        """绘制预测结果"""
        if model is None:
            if model_name not in self.models:
                raise ValueError(f"模型 {model_name} 尚未训练")
            model = self.models[model_name]
        
        # 选择适当的数据
        if model_name in ['svr', 'knn']:
            X_test_eval = self.X_test_scaled
        else:
            X_test_eval = self.X_test
        
        y_pred = model.predict(X_test_eval)
        
        plt.figure(figsize=(12, 5))
        
        # 真实值 vs 预测值
        plt.subplot(1, 2, 1)
        plt.scatter(self.y_test, y_pred, alpha=0.6)
        plt.plot([self.y_test.min(), self.y_test.max()], 
                [self.y_test.min(), self.y_test.max()], 'r--', lw=2)
        plt.xlabel('Actual')
        plt.ylabel('Predicted')
        plt.title(f'Actual vs Predicted - {model_name}')
        
        # 残差图
        plt.subplot(1, 2, 2)
        residuals = self.y_test - y_pred
        plt.scatter(y_pred, residuals, alpha=0.6)
        plt.axhline(y=0, color='r', linestyle='--')
        plt.xlabel('Predicted')
        plt.ylabel('Residuals')
        plt.title(f'Residuals Plot - {model_name}')
        
        plt.tight_layout()
        plt.show()
    
    def plot_residuals_distribution(self, model_name, model=None):
        """绘制残差分布"""
        if model is None:
            if model_name not in self.models:
                raise ValueError(f"模型 {model_name} 尚未训练")
            model = self.models[model_name]
        
        # 选择适当的数据
        if model_name in ['svr', 'knn']:
            X_test_eval = self.X_test_scaled
        else:
            X_test_eval = self.X_test
        
        y_pred = model.predict(X_test_eval)
        residuals = self.y_test - y_pred
        
        plt.figure(figsize=(12, 4))
        
        # 残差直方图
        plt.subplot(1, 2, 1)
        sns.histplot(residuals, kde=True)
        plt.title(f'Residuals Distribution - {model_name}')
        plt.xlabel('Residuals')
        
        # Q-Q图
        plt.subplot(1, 2, 2)
        from scipy import stats
        stats.probplot(residuals, dist="norm", plot=plt)
        plt.title(f'Q-Q Plot - {model_name}')
        
        plt.tight_layout()
        plt.show()

# 使用示例
from sklearn.datasets import make_regression

# 创建回归数据集
X, y = make_regression(
    n_samples=1000, n_features=15, n_informative=10,
    noise=0.1, random_state=42
)

X_df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(15)])

# 训练回归模型
trainer = RegressionTrainer(X_df, y)

# 训练多个模型
trainer.train_linear_regression()
trainer.train_ridge()
trainer.train_random_forest()
trainer.train_xgboost()
trainer.train_lightgbm()

# 比较模型性能
results = trainer.compare_models()
print("回归模型比较结果:")
print(results)

# 绘制预测结果
trainer.plot_predictions('random_forest')

# 绘制残差分布
trainer.plot_residuals_distribution('random_forest')
```

## 深度学习

### PyTorch深度学习

#### 基础神经网络
```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, TensorDataset
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

class SimpleNN(nn.Module):
    """简单神经网络"""
    def __init__(self, input_size, hidden_sizes, output_size, dropout_rate=0.2):
        super(SimpleNN, self).__init__()
        
        layers = []
        
        # 输入层到第一个隐藏层
        layers.append(nn.Linear(input_size, hidden_sizes[0]))
        layers.append(nn.ReLU())
        layers.append(nn.Dropout(dropout_rate))
        
        # 隐藏层
        for i in range(len(hidden_sizes) - 1):
            layers.append(nn.Linear(hidden_sizes[i], hidden_sizes[i + 1]))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout_rate))
        
        # 输出层
        layers.append(nn.Linear(hidden_sizes[-1], output_size))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)

class DeepLearningTrainer:
    def __init__(self, X, y, task_type='classification', test_size=0.2, random_state=42):
        self.task_type = task_type
        self.random_state = random_state
        
        # 数据分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # 特征缩放
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 转换为PyTorch张量
        self.X_train = torch.FloatTensor(X_train_scaled)
        self.X_test = torch.FloatTensor(X_test_scaled)
        
        if task_type == 'classification':
            self.y_train = torch.LongTensor(y_train.values if hasattr(y_train, 'values') else y_train)
            self.y_test = torch.LongTensor(y_test.values if hasattr(y_test, 'values') else y_test)
        else:
            self.y_train = torch.FloatTensor(y_train.values if hasattr(y_train, 'values') else y_train)
            self.y_test = torch.FloatTensor(y_test.values if hasattr(y_test, 'values') else y_test)
        
        # 创建数据加载器
        train_dataset = TensorDataset(self.X_train, self.y_train)
        test_dataset = TensorDataset(self.X_test, self.y_test)
        
        self.train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
        self.test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
        
        self.model = None
        self.optimizer = None
        self.criterion = None
        self.train_losses = []
        self.val_losses = []
    
    def create_model(self, hidden_sizes=[64, 32], dropout_rate=0.2):
        """创建模型"""
        input_size = self.X_train.shape[1]
        
        if self.task_type == 'classification':
            output_size = len(torch.unique(self.y_train))
        else:
            output_size = 1
        
        self.model = SimpleNN(input_size, hidden_sizes, output_size, dropout_rate)
        
        # 选择损失函数
        if self.task_type == 'classification':
            self.criterion = nn.CrossEntropyLoss()
        else:
            self.criterion = nn.MSELoss()
        
        # 选择优化器
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001, weight_decay=1e-5)
        
        return self.model
    
    def train_epoch(self):
        """训练一个epoch"""
        self.model.train()
        total_loss = 0
        
        for batch_X, batch_y in self.train_loader:
            self.optimizer.zero_grad()
            
            outputs = self.model(batch_X)
            loss = self.criterion(outputs, batch_y)
            
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(self.train_loader)
    
    def validate_epoch(self):
        """验证一个epoch"""
        self.model.eval()
        total_loss = 0
        
        with torch.no_grad():
            for batch_X, batch_y in self.test_loader:
                outputs = self.model(batch_X)
                loss = self.criterion(outputs, batch_y)
                total_loss += loss.item()
        
        return total_loss / len(self.test_loader)
    
    def train(self, epochs=100, patience=10, verbose=True):
        """训练模型"""
        best_val_loss = float('inf')
        patience_counter = 0
        best_model_state = None
        
        for epoch in range(epochs):
            train_loss = self.train_epoch()
            val_loss = self.validate_epoch()
            
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            
            if verbose and epoch % 10 == 0:
                print(f'Epoch {epoch}: Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}')
            
            # 早停
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                best_model_state = self.model.state_dict()
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    if verbose:
                        print(f'Early stopping at epoch {epoch}')
                    break
        
        # 加载最佳模型
        if best_model_state is not None:
            self.model.load_state_dict(best_model_state)
    
    def predict(self, X=None):
        """预测"""
        self.model.eval()
        
        if X is None:
            X = self.X_test
        else:
            X = torch.FloatTensor(self.scaler.transform(X))
        
        with torch.no_grad():
            outputs = self.model(X)
            
            if self.task_type == 'classification':
                predictions = torch.argmax(outputs, dim=1).numpy()
                probabilities = torch.softmax(outputs, dim=1).numpy()
                return predictions, probabilities
            else:
                return outputs.numpy()
    
    def evaluate(self):
        """评估模型"""
        if self.task_type == 'classification':
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            
            predictions, _ = self.predict()
            
            accuracy = accuracy_score(self.y_test.numpy(), predictions)
            precision = precision_score(self.y_test.numpy(), predictions, average='weighted')
            recall = recall_score(self.y_test.numpy(), predictions, average='weighted')
            f1 = f1_score(self.y_test.numpy(), predictions, average='weighted')
            
            return {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1
            }
        else:
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            
            predictions = self.predict()
            
            mse = mean_squared_error(self.y_test.numpy(), predictions)
            mae = mean_absolute_error(self.y_test.numpy(), predictions)
            r2 = r2_score(self.y_test.numpy(), predictions)
            
            return {
                'mse': mse,
                'mae': mae,
                'r2': r2
            }
    
    def plot_training_history(self):
        """绘制训练历史"""
        plt.figure(figsize=(10, 5))
        plt.plot(self.train_losses, label='Train Loss')
        plt.plot(self.val_losses, label='Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Training History')
        plt.legend()
        plt.grid(True)
        plt.show()

# 使用示例
from sklearn.datasets import make_classification, make_regression

# 分类任务示例
X_clf, y_clf = make_classification(
    n_samples=1000, n_features=20, n_classes=3, random_state=42
)

# 训练深度学习分类器
dl_trainer = DeepLearningTrainer(
    pd.DataFrame(X_clf), pd.Series(y_clf), 
    task_type='classification'
)

# 创建并训练模型
dl_trainer.create_model(hidden_sizes=[64, 32, 16], dropout_rate=0.3)
dl_trainer.train(epochs=100, patience=15)

# 评估模型
results = dl_trainer.evaluate()
print("深度学习分类结果:", results)

# 绘制训练历史
dl_trainer.plot_training_history()

# 回归任务示例
X_reg, y_reg = make_regression(
    n_samples=1000, n_features=15, noise=0.1, random_state=42
)

# 训练深度学习回归器
dl_trainer_reg = DeepLearningTrainer(
    pd.DataFrame(X_reg), pd.Series(y_reg), 
    task_type='regression'
)

# 创建并训练模型
dl_trainer_reg.create_model(hidden_sizes=[32, 16], dropout_rate=0.2)
dl_trainer_reg.train(epochs=100, patience=10)

# 评估模型
results_reg = dl_trainer_reg.evaluate()
print("深度学习回归结果:", results_reg)

# 绘制训练历史
dl_trainer_reg.plot_training_history()
```

## 参考资源

### 机器学习框架
- [Scikit-learn Documentation](https://scikit-learn.org/stable/)
- [TensorFlow Documentation](https://www.tensorflow.org/docs)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [LightGBM Documentation](https://lightgbm.readthedocs.io/)

### 深度学习资源
- [Deep Learning Book](https://www.deeplearningbook.org/)
- [Neural Networks and Deep Learning](http://neuralnetworksanddeeplearning.com/)
- [Fast.ai](https://www.fast.ai/)
- [Stanford CS231n](http://cs231n.stanford.edu/)

### 数据科学工具
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [NumPy Documentation](https://numpy.org/doc/)
- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)
- [Seaborn Documentation](https://seaborn.pydata.org/)

### 实验管理
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Weights & Biases Documentation](https://docs.wandb.ai/)
- [TensorBoard Documentation](https://www.tensorflow.org/tensorboard)
- [Neptune Documentation](https://docs.neptune.ai/)

### 模型部署
- [TensorFlow Serving](https://www.tensorflow.org/tfx/guide/serving)
- [TorchServe](https://pytorch.org/serve/)
- [ONNX Runtime](https://onnxruntime.ai/)
- [BentoML](https://docs.bentoml.org/)

### 社区资源
- [Kaggle](https://www.kaggle.com/)
- [Papers With Code](https://paperswithcode.com/)
- [Reddit r/MachineLearning](https://www.reddit.com/r/MachineLearning/)
- [Awesome Machine Learning](https://github.com/josephmisiti/awesome-machine-learning)
