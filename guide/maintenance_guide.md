# 项目维护指南：日志格式变更处理

当WiFi日志的内容或格式发生变化时，需要按照以下指南更新相关文件，确保项目的正常运行。

## 🎯 核心原则

**日志格式变更影响范围**：
- 🔴 **高影响**：解析逻辑、数据生成、分析脚本
- 🟡 **中影响**：文档说明、示例代码
- 🟢 **低影响**：配置文件、README概述

## 📋 变更类型与对应文件

### 1. 日志时间戳格式变更

#### 影响文件
- ✅ `src/generate_data.py` - 数据生成脚本
- ✅ `src/analyze_optimized_data.py` - 分析脚本
- ✅ `src/data_analysis.py` (如果存在) - 旧版分析脚本

#### 修改要点
```python
# 在解析脚本中找到时间戳解析部分
time_pattern = r'(\w{3} \w{3} \d+ \d+:\d+:\d+)'  # 需要修改此正则表达式
timestamp = datetime.strptime(f"2023 {timestamp_str}", "%Y %a %b %d %H:%M:%S")  # 修改解析格式
```

#### 示例修改
```python
# 原格式: Wed Jul  9 09:25:16
time_pattern = r'(\w{3} \w{3} \d+ \d+:\d+:\d+)'

# 新格式: 2023-07-09 09:25:16 (假设)
time_pattern = r'(\d{4}-\d{2}-\d{2} \d+:\d+:\d+)'
timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
```

### 2. 客户端事件格式变更

#### 影响文件
- ✅ `src/generate_data.py`
- ✅ `src/analyze_optimized_data.py`
- ✅ `guide/optimized_reason_codes.md`

#### 修改要点
```python
# 客户端事件正则表达式
client_pattern = r'reported client=\[([^\]]+)\] (assoc|disassoc) on vap=\[([^\]]+)\](?:, reason code=\[(\d+)\])?'

# 如果格式变为: client:[MAC] event:assoc interface:rai0
# 需要修改为:
client_pattern = r'client:\[([^\]]+)\] event:(assoc|disassoc) interface:\[([^\]]+)\](?:, reason:\[(\d+)\])?'
```

#### 数据生成函数
```python
def generate_client_event(self, timestamp, mac, event_type, vap, reason_code=None):
    # 需要根据新格式修改输出字符串
    if event_type == "assoc":
        return f"USSA > {timestamp} | NOTICE  | reported client=[{mac}] assoc on vap=[{vap}]"
    else:
        return f"USSA > {timestamp} | NOTICE  | reported client=[{mac}] disassoc on vap=[{vap}], reason code=[{reason_code}]"
```

### 3. Reason Code变更

#### 影响文件
- ✅ `src/generate_data.py` - reason_codes字典
- ✅ `src/analyze_optimized_data.py` - reason_code_mapping字典  
- ✅ `guide/optimized_reason_codes.md` - 完整文档重写
- ✅ `README.md` - 支持的异常类型部分

#### 修改步骤

**步骤1**: 更新数据生成脚本
```python
# src/generate_data.py
self.reason_codes = {
    1: "未指定原因",
    3: "客户端主动离开",
    4: "因不活跃断连",
    5: "AP过载", 
    15: "4-Way握手超时",
    23: "802.1X认证失败",
    # 新增reason code
    8: "客户端离开BSS",  # 示例新增
}
```

**步骤2**: 更新分析脚本
```python
# src/analyze_optimized_data.py
self.reason_code_mapping = {
    1: "Unspecified reason",
    3: "Client leaving",
    4: "Inactivity timeout", 
    5: "AP overload",
    15: "4-Way handshake timeout",
    23: "802.1X auth failed",
    8: "Client leaving BSS",  # 新增
}

# 更新类别分组
self.reason_categories = {
    "Normal": [3, 4, 8],  # 添加新的正常断连类型
    "Auth Issues": [15, 23],
    "Capacity Issues": [5],
    "Unspecified": [1]
}
```

**步骤3**: 更新文档
```markdown
# guide/optimized_reason_codes.md
### 新增：Code 8: 客户端离开BSS
- **含义**: 客户端离开基础服务集
- **特征**: 主动离开行为的一种具体形式
```

### 4. 配置变更事件格式变更

#### 影响文件
- ✅ `src/generate_data.py`
- ✅ `src/analyze_optimized_data.py`

#### 修改要点
```python
# 原格式: reason=[1], oldCh->newCh=[1]->[6]
config_pattern = r'reason=\[(\d+)\], oldCh->newCh=\[(\d+)\]->\[(\d+)\]'

# 新格式: config_reason=1, channel_change=1->6 (假设)
config_pattern = r'config_reason=(\d+), channel_change=(\d+)->(\d+)'
```

### 5. VAP接口名称变更

#### 影响文件
- ✅ `src/generate_data.py` - vaps列表
- ✅ 数据文件 - 重新生成数据

#### 修改示例
```python
# src/generate_data.py
# 原接口名称
self.vaps = ["rai0", "rai4"]

# 新接口名称
self.vaps = ["wlan0", "wlan1", "eth0"]  # 示例
```

## 🔄 标准维护流程

### 第一步：分析变更
1. **确定变更类型**：时间戳、事件格式、reason code等
2. **评估影响范围**：哪些文件需要修改
3. **备份当前版本**：防止修改出错

### 第二步：更新解析逻辑
1. **修改正则表达式**：适配新的日志格式
2. **测试解析功能**：确保能正确提取信息
3. **更新字段映射**：reason code描述等

### 第三步：重新生成数据
```bash
cd src
python3 generate_data.py  # 生成新的优化数据集
```

### 第四步：验证数据质量
```bash
python3 analyze_optimized_data.py  # 验证数据解析正确性
```

### 第五步：更新文档
1. **更新技术文档**：reason code说明等
2. **更新README**：反映新的特性
3. **更新示例代码**：确保示例可运行

### 第六步：测试完整流程
1. **端到端测试**：从数据生成到分析完整流程
2. **回归测试**：确保原有功能正常
3. **性能测试**：验证处理效率

## 📁 文件修改优先级

### 🔴 必须修改 (Critical)
1. `src/generate_data.py` - 数据生成核心
2. `src/analyze_optimized_data.py` - 数据分析核心

### 🟡 建议修改 (Important)  
3. `guide/optimized_reason_codes.md` - 技术文档
4. `ussawifievent_optimized.txt` - 重新生成数据

### 🟢 可选修改 (Optional)
5. `README.md` - 项目概述
6. `guide/client_session_analysis.md` - 分析方案文档

## ⚠️ 常见问题与解决

### 问题1：正则表达式不匹配
**症状**: 解析脚本无法提取数据
**解决**: 
1. 检查日志样本，确认格式变化
2. 使用在线正则测试工具验证新表达式
3. 逐步调试，先匹配简单部分

### 问题2：时间戳解析失败
**症状**: datetime.strptime() 报错
**解决**:
1. 确认新的时间格式
2. 查阅Python datetime文档，找到对应格式符
3. 考虑时区问题

### 问题3：Reason Code含义变化
**症状**: 分析结果与预期不符
**解决**:
1. 重新审查reason code官方文档
2. 更新所有映射字典和分类
3. 重新生成和验证数据

### 问题4：数据分布不平衡
**症状**: 某些reason code过多或过少
**解决**:
1. 调整generate_data.py中的权重参数
2. 修改choose_reason_code()逻辑
3. 重新平衡各类别比例

## 🔧 维护工具

### 快速检查脚本
```bash
# 检查日志格式是否改变
head -10 ussawifievent_optimized.txt

# 验证解析是否正常
python3 -c "
from src.analyze_optimized_data import OptimizedWiFiAnalyzer
analyzer = OptimizedWiFiAnalyzer('ussawifievent_optimized.txt')
df = analyzer.create_dataframe()
print(f'成功解析: {len(df)} 事件')
"
```

### 备份恢复
```bash
# 备份当前版本
cp ussawifievent_optimized.txt ussawifievent_optimized.txt.backup
cp -r src/ src_backup/

# 恢复备份版本
cp ussawifievent_optimized.txt.backup ussawifievent_optimized.txt
rm -rf src/ && mv src_backup/ src/
```

## 📞 技术支持

如果在维护过程中遇到问题：
1. **检查日志样本**：确保格式理解正确
2. **分步骤测试**：逐个验证修改是否正确
3. **查看错误信息**：Python错误通常很明确
4. **参考原始文档**：IEEE 802.11标准等

遵循此指南，可以有效应对日志格式变更，确保项目持续稳定运行。 