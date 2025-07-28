# 双流时序异常检测与分类框架

## 项目简介

本项目实现了一个先进的双流时序异常检测与分类框架，专门用于网络设备日志的异常检测和智能诊断。该框架通过将异常检测问题分解为两个并行的检测流，分别处理语义/逻辑异常和数据/指标异常，最终通过智能分类器进行统一诊断。

## 核心特性

### 🚀 双流并行检测
- **语义异常流**: 使用LSTM自编码器检测事件序列中的逻辑异常
- **数据异常流**: 使用孤立森林算法检测数值指标的统计异常

### 🎯 智能分类诊断
- 基于XGBoost的多分类器，提供具体的异常类型诊断
- 支持可解释性分析，明确异常原因和关键指标

### 📊 完整的处理流程
- 自动日志解析和结构化处理
- 时间序列重采样和特征工程
- 端到端的异常检测和分类流程

## 技术架构

```
原始日志 → 数据预处理 → 双流检测引擎 → 智能诊断分类 → 异常分类结果
           ↓              ↓                ↓
         结构化数据    语义异常 + 数据异常    可解释性分析
```

## 目录结构

```
processing-model/
├── guide/                          # 项目文档
│   └── dual_stream_framework.md    # 详细设计方案
├── test/                           # 测试脚本目录
├── src/                            # 源代码目录（待开发）
├── data/                           # 数据目录（待创建）
├── models/                         # 模型存储目录（待创建）
├── ussawifievent.txt              # 示例日志文件
├── README.md                       # 项目说明文档
└── requirements.txt               # 依赖包列表（待创建）
```

## 快速开始

### 环境要求
- Python 3.8+
- 支持CUDA的GPU（可选，用于深度学习加速）

### 安装依赖
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖包（待requirements.txt创建后）
pip install -r requirements.txt
```

### 基本使用
```python
# 示例代码（待实现）
from src.dual_stream_framework import DualStreamDetector

# 初始化检测器
detector = DualStreamDetector()

# 加载和预处理日志数据
detector.load_data('ussawifievent.txt')

# 训练模型
detector.train()

# 进行异常检测
anomalies = detector.detect()

# 获取异常分类结果
classifications = detector.classify_anomalies(anomalies)
```

## 主要组件

### 1. 数据预处理层
- **日志解析器**: 解析各种格式的网络设备日志
- **时序重采样器**: 将离散事件转换为固定时间间隔的时间序列
- **特征标准化器**: 确保不同特征的可比性

### 2. 双流检测引擎
- **语义异常检测流**: 基于LSTM自编码器的事件序列异常检测
- **数据异常检测流**: 基于孤立森林的数值指标异常检测

### 3. 智能诊断分类层
- **特征融合器**: 整合多源特征信息
- **XGBoost分类器**: 进行精确的异常类型分类
- **可解释性分析器**: 提供异常原因分析

## 支持的异常类型

### 网络连接异常
- 频繁断连
- 认证失败
- 关联超时

### 性能异常
- 信号质量差
- 传输速率低
- 延迟过高

### 硬件异常
- 功率异常
- 温度过高
- 内存不足

### 配置异常
- 参数错误
- 策略冲突
- 版本不匹配

## 性能指标

### 预期检测性能
- 异常检测准确率: >95%
- 误报率: <5%
- 漏报率: <3%

### 预期分类性能
- 异常分类准确率: >90%
- 平均诊断时间: 从小时级降到分钟级
- 人工干预需求: 减少70%

## 开发计划

- [x] ~~框架设计和文档编写~~
- [ ] 数据预处理模块实现 (1-2周)
- [ ] 双流检测引擎开发 (2-3周)
- [ ] 分类诊断模块集成 (1-2周)
- [ ] 系统集成与测试 (1周)

## 文档

### 技术文档
- **[双流框架设计方案](guide/dual_stream_framework.md)**: 完整的技术架构和实现计划
- **[客户端会话分析方案](guide/client_session_analysis.md)**: 客户端行为模式分析的具体方法
- **[优化数据集说明](guide/optimized_reason_codes.md)**: 6种主要断连原因详解和使用指南

### 维护文档
- **[项目维护指南](guide/maintenance_guide.md)**: 日志格式变更时的完整维护流程
- **[快速维护检查清单](guide/quick_maintenance_checklist.md)**: 日志变更时需要修改的文件清单

### 文档内容包含
- 完整的技术架构设计
- 详细的算法原理说明
- 实现计划和时间表
- 技术挑战和解决方案
- 性能评估指标
- 数据分析方法和工具使用
- 项目维护和更新指南

## 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件至项目维护者

## 致谢

感谢所有为这个项目做出贡献的开发者和研究人员。

---

**注意**: 本项目目前处于设计阶段，代码实现正在进行中。详细的使用说明将在代码完成后更新。 