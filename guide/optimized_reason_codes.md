# 优化数据集：6种主要WiFi断连原因参考

## 数据集概览

`ussawifievent_optimized.txt` 包含501条WiFi事件日志，专注于6种最常见和最有代表性的断连原因。这些数据经过优化，适合机器学习模型训练和实际网络故障分析。

## 重要区分

### ⚠️ reason vs reason code
- **reason=[数字]**: 配置变更的转换原因（如信道切换、功率调整等），**不是断连原因**
- **reason code=[数字]**: 客户端断连的具体原因，**这是我们要分析和预测的目标**

### 示例
```
# 配置变更 (不考虑)
reason=[2], oldCh->newCh=[4]->[1], oldBw->newBw=[80MHz]->[80MHz]

# 客户端断连 (我们的重点)
reported client=[2e:55:b9:42:06:aa] disassoc on vap=[rai4], reason code=[15]
```

## 6种主要断连原因详解

### 1. Code 1: 未指定原因 (Unspecified reason)
- **含义**: 最通用的断连代码，原因不明确或多种可能
- **占比**: 64次 (26.1%)
- **特征**: 
  - 各种会话长度都可能出现
  - 网络正常运行时的常见断连
  - 可能是软件重启、驱动更新等原因
- **预测线索**: 通常没有明显的前置事件模式

### 2. Code 4: 因不活跃断连 (Disassociated due to inactivity)
- **含义**: 客户端长时间无数据传输，被AP主动断开
- **占比**: 52次 (21.2%)
- **特征**:
  - 通常发生在较长的会话后（30分钟以上）
  - 用户可能已离开或设备进入休眠
  - 是一种正常的网络管理行为
- **预测线索**: 长时间连接 + 无活动迹象

### 3. Code 3: 客户端主动离开 (Deauthenticated because sending station is leaving)
- **含义**: 客户端主动发起断连，正常离开网络
- **占比**: 54次 (22.0%)
- **特征**:
  - 用户主动操作（关闭WiFi、切换网络等）
  - 设备关机或移出覆盖范围
  - 通常是计划内的断连
- **预测线索**: 用户行为模式、时间规律

### 4. Code 15: 4-Way握手超时 (4-Way Handshake timeout)
- **含义**: WPA/WPA2安全认证过程中的四次握手超时失败
- **占比**: 24次 (9.8%)
- **特征**:
  - 安全认证问题
  - 可能是密码错误、网络配置问题
  - 通常发生在连接初期
- **预测线索**: 短会话 + 频繁重连尝试

### 5. Code 23: 802.1X认证失败 (IEEE 802.1X authentication failed)
- **含义**: 企业级网络的802.1X认证失败
- **占比**: 20次 (8.1%)
- **特征**:
  - 企业网络环境常见
  - 证书问题、用户名密码错误
  - RADIUS服务器连接问题
- **预测线索**: 企业网络环境 + 认证服务器状态

### 6. Code 5: AP过载 (AP unable to handle all associated stations)
- **含义**: 接入点无法处理当前所有关联的客户端，拒绝新连接或断开现有连接
- **占比**: 32次 (13.1%)
- **特征**:
  - 网络高负载时期
  - 同时在线用户过多
  - AP性能瓶颈
- **预测线索**: 高并发连接时段 + 系统负载指标

## 数据特征分析

### 时间分布
- **数据跨度**: 2023年7月7日 08:00 - 多日连续
- **事件密度**: 平均每小时20-30个事件
- **配置变更**: 约占总事件的5%，不影响断连分析

### 客户端分布
数据包含8个不同的客户端设备：
- `2e:55:b9:42:06:aa` (较活跃)
- `4c:79:6e:de:4d:1f` (中等活跃)
- `d6:99:0f:58:6c:79` (中等活跃)
- `a2:c4:7f:38:21:9b` (较不活跃)
- `f8:e6:1a:57:02:45` (较不活跃)
- `bc:d1:77:e4:58:a3` (较不活跃)
- `1a:2b:3c:4d:5e:6f` (较不活跃)
- `7g:8h:9i:0j:1k:2l` (较不活跃)

### VAP接口分布
- `rai0`: 主要接口
- `rai4`: 辅助接口

## 机器学习建议

### 1. 特征工程
```python
# 时间特征
- hour_of_day: 小时 (0-23)
- day_of_week: 星期几 (0-6)
- session_duration: 会话持续时间(分钟)

# 行为特征  
- recent_disconnects: 最近断连次数
- reconnect_interval: 重连间隔时间
- client_stability: 客户端稳定性评分

# 网络特征
- concurrent_clients: 同时在线客户端数
- config_changes_nearby: 附近配置变更
- vap_load: VAP负载情况
```

### 2. 目标变量
```python
# 6分类问题
target_classes = {
    1: "未指定原因",
    3: "客户端主动离开", 
    4: "因不活跃断连",
    5: "AP过载",
    15: "4-Way握手超时",
    23: "802.1X认证失败"
}
```

### 3. 模型选择建议

**阶段1: 基线模型**
- **随机森林**: 快速实现，特征重要性分析
- **XGBoost**: 高准确率，处理不平衡数据

**阶段2: 深度学习**
- **LSTM**: 学习客户端行为序列模式
- **CNN-LSTM**: 结合局部和时序特征

**阶段3: 集成方法**
- **投票分类器**: 结合多种模型的预测
- **Stacking**: 元学习器优化最终预测

### 4. 评估指标
- **整体准确率**: >85%
- **每类别精确率/召回率**: >80%
- **混淆矩阵**: 分析错分类模式
- **特征重要性**: 识别关键预测因子

## 实际应用价值

### 1. 网络运维
- **预防性维护**: 预测何时可能出现特定类型的断连
- **资源优化**: 根据断连模式调整AP配置
- **故障诊断**: 快速定位问题根因

### 2. 用户体验
- **连接稳定性**: 识别并解决连接质量问题
- **个性化服务**: 根据用户行为模式优化网络参数
- **智能重连**: 预测最佳重连时机和方式

### 3. 容量规划
- **负载预测**: 基于历史断连模式预测网络负载
- **扩容决策**: 识别需要增加AP的区域和时间
- **配置优化**: 自动调整网络参数以减少断连

## 下一步行动

1. **数据探索**: 使用优化后的数据集进行深入的探索性数据分析
2. **模型训练**: 实现上述建议的机器学习模型
3. **性能验证**: 在真实网络环境中验证模型效果
4. **持续优化**: 根据实际使用反馈不断改进模型

这个优化的数据集为WiFi网络异常检测和故障预测提供了坚实的基础，能够支持从简单统计分析到复杂深度学习模型的各种应用需求。 