# WiFi日志断连原因分析项目

## 项目简介

本项目专注于WiFi网络日志的断连原因分析和预测。通过分析6种主要的WiFi断连原因（reason code），帮助网络运维人员快速定位问题根因，提升网络稳定性。

## 🎯 核心功能

- **6种断连原因分析**: 专注于最常见的WiFi断连场景
- **自动数据生成**: 生成符合IEEE 802.11标准的模拟日志数据
- **智能数据分析**: 深入分析客户端行为模式和时间规律
- **可视化报告**: 自动生成直观的分析图表

## 📊 支持的断连原因

| Code | 描述 | 常见场景 |
|------|------|----------|
| **1** | 未指定原因 | 通用断连，软件重启等 |
| **3** | 客户端主动离开 | 用户关闭WiFi，离开覆盖区域 |
| **4** | 因不活跃断连 | 长时间无数据传输，AP主动断开 |
| **5** | AP过载 | 网络负载过高，AP无法处理更多连接 |
| **15** | 4-Way握手超时 | WPA/WPA2认证失败 |
| **23** | 802.1X认证失败 | 企业网络认证问题 |

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Linux/MacOS/Windows

### 安装依赖
```bash
# 克隆项目
git clone <repository-url>
cd 处理模型

# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 基本使用

#### 1. 数据生成
```bash
cd src
python generate_data.py
```
输出: `ussawifievent_optimized.txt` (501条WiFi事件，包含6种断连原因)

#### 2. 数据分析
```bash
python analyze_optimized_data.py
```
输出: 详细的统计分析报告 + 可视化图表

### 使用示例
```python
from src.analyze_optimized_data import OptimizedWiFiAnalyzer

# 初始化分析器
analyzer = OptimizedWiFiAnalyzer('ussawifievent_optimized.txt')

# 创建数据框架
df = analyzer.create_dataframe()

# 分析断连原因
reason_counts, category_counts = analyzer.analyze_reason_codes(df)

# 分析客户端会话
session_stats = analyzer.analyze_client_sessions(df)

# 生成可视化图表
analyzer.visualize_data(df)
```

## 📁 项目结构

```
处理模型/
├── src/                                    # 源代码
│   ├── generate_data.py                    # 数据生成脚本
│   └── analyze_optimized_data.py           # 数据分析脚本
├── guide/                                  # 项目文档
│   ├── optimized_reason_codes.md           # 断连原因详解
│   ├── maintenance_guide.md                # 维护指南
│   └── quick_maintenance_checklist.md      # 快速检查清单
├── ussawifievent_optimized.txt             # 优化的WiFi日志数据 (501条)
├── requirements.txt                        # 依赖包列表
└── README.md                               # 项目说明
```

## 📈 数据特征

### 数据质量
- ✅ **501条事件** (超过目标500条)
- ✅ **6种断连原因** 分布均衡
- ✅ **8个客户端设备** 行为多样
- ✅ **5天时间跨度** 连续数据

### 分布统计
- **正常断连** (43.1%): 不活跃超时 + 主动离开
- **未指定原因** (26.0%): 通用断连
- **认证问题** (17.9%): 握手超时 + 802.1X失败  
- **容量问题** (13.0%): AP过载

### 时间特征
- **高峰时段**: 5时、17时、18时
- **会话时长**: 平均17-36分钟
- **重连模式**: 各客户端有不同的断连偏好

## 🎯 实际应用

### 网络运维
- **故障诊断**: 快速识别断连根因
- **预防性维护**: 预测潜在网络问题
- **容量规划**: 基于断连模式优化网络配置

### 数据分析
- **客户端行为分析**: 了解用户连接习惯
- **时间模式挖掘**: 发现网络使用规律
- **异常检测**: 识别不正常的断连模式

### 机器学习应用
- **分类预测**: 预测断连原因类型
- **时序分析**: 学习客户端连接模式
- **特征工程**: 基于会话时长、重连间隔等特征建模

## 🔧 维护和扩展

### 日志格式变更
如果WiFi日志格式发生变化，请参考:
- **[完整维护指南](guide/maintenance_guide.md)**: 详细的处理流程
- **[快速检查清单](guide/quick_maintenance_checklist.md)**: 要修改的文件列表

### 核心修改文件
1. `src/generate_data.py` - 更新数据生成逻辑
2. `src/analyze_optimized_data.py` - 更新解析逻辑

### 快速验证
```bash
# 测试数据解析是否正常
python -c "
from src.analyze_optimized_data import OptimizedWiFiAnalyzer
analyzer = OptimizedWiFiAnalyzer('ussawifievent_optimized.txt')
df = analyzer.create_dataframe()
print(f'✅ 成功解析: {len(df)} 事件')
print(f'✅ 断连原因数: {df[\"reason_code\"].nunique()}')
"
```

## 📚 技术文档

- **[优化数据集说明](guide/optimized_reason_codes.md)**: 6种断连原因的详细技术说明
- **[项目维护指南](guide/maintenance_guide.md)**: 完整的维护和更新流程
- **[快速维护检查清单](guide/quick_maintenance_checklist.md)**: 日志变更时的修改清单

## 💡 设计理念

### 简单实用
- 专注于6种最重要的断连原因
- 避免过度复杂的深度学习方案
- 优先可解释性和实用性

### 易于维护
- 清晰的代码结构
- 详细的维护文档
- 标准化的数据格式

### 可扩展性
- 模块化设计，易于添加新功能
- 标准的IEEE 802.11格式
- 支持自定义reason code

## ⚠️ 重要说明

### reason vs reason code
- **reason=[数字]**: 配置变更原因 (如信道切换) - **不分析**
- **reason code=[数字]**: 客户端断连原因 - **分析重点**

### 数据特点
- 数据基于真实WiFi日志格式生成
- 符合IEEE 802.11标准
- 适合机器学习训练和网络分析

## 🔮 未来规划

- [ ] Web界面展示分析结果
- [ ] 实时日志流处理
- [ ] 机器学习模型预训练
- [ ] 更多reason code支持
- [ ] 网络拓扑关联分析

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/新功能`)
3. 提交更改 (`git commit -m '添加新功能'`)
4. 推送到分支 (`git push origin feature/新功能`)
5. 创建 Pull Request

## 📧 联系方式

如有问题或建议，请通过 Issue 反馈。

---

**🎯 项目目标**: 让WiFi网络故障诊断变得简单高效！ 