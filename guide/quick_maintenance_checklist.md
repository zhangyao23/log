# 快速维护检查清单

## 🚨 日志格式变更 - 必须修改的文件

### 📋 核心文件修改清单

| 变更类型 | 必须修改 | 建议修改 | 可选修改 |
|---------|---------|---------|---------|
| **时间戳格式** | `src/generate_data.py`<br>`src/analyze_optimized_data.py` | `ussawifievent_optimized.txt` | `README.md` |
| **事件格式** | `src/generate_data.py`<br>`src/analyze_optimized_data.py` | `guide/optimized_reason_codes.md` | `README.md` |
| **Reason Code** | `src/generate_data.py`<br>`src/analyze_optimized_data.py` | `guide/optimized_reason_codes.md`<br>`ussawifievent_optimized.txt` | `README.md`<br>`guide/client_session_analysis.md` |
| **VAP接口名** | `src/generate_data.py` | `ussawifievent_optimized.txt` | 无 |
| **配置事件** | `src/generate_data.py`<br>`src/analyze_optimized_data.py` | 无 | 无 |

## 🔧 标准修改流程

```bash
# 1. 备份当前版本
cp ussawifievent_optimized.txt ussawifievent_optimized.txt.backup
cp -r src/ src_backup/

# 2. 修改解析脚本
vim src/generate_data.py          # 修改数据生成逻辑
vim src/analyze_optimized_data.py # 修改解析逻辑

# 3. 重新生成数据
cd src && python3 generate_data.py

# 4. 验证数据质量
python3 analyze_optimized_data.py

# 5. 更新文档 (如果需要)
vim guide/optimized_reason_codes.md
```

## 📍 关键修改点

### 1. 正则表达式 (最重要)
```python
# 在两个脚本中找到并修改:
time_pattern = r'(\w{3} \w{3} \d+ \d+:\d+:\d+)'     # 时间戳格式
client_pattern = r'reported client=\[([^\]]+)\]...' # 客户端事件格式
config_pattern = r'reason=\[(\d+)\]...'             # 配置事件格式
```

### 2. 映射字典
```python
# src/generate_data.py
self.reason_codes = {...}  # 断连原因中文映射

# src/analyze_optimized_data.py  
self.reason_code_mapping = {...}  # 断连原因英文映射
self.reason_categories = {...}    # 原因分类
```

### 3. 数据生成函数
```python
# src/generate_data.py
def generate_client_event(...)     # 客户端事件生成
def generate_config_change(...)    # 配置变更生成
```

## ⚡ 快速测试命令

```bash
# 测试解析是否正常
python3 -c "
from src.analyze_optimized_data import OptimizedWiFiAnalyzer
analyzer = OptimizedWiFiAnalyzer('ussawifievent_optimized.txt')
df = analyzer.create_dataframe()
print(f'✅ 成功解析: {len(df)} 事件')
print(f'✅ 断连原因数: {df[\"reason_code\"].nunique()}')
"

# 查看数据样本
head -5 ussawifievent_optimized.txt
```

## 🆘 紧急恢复

```bash
# 如果修改出错，快速恢复
cp ussawifievent_optimized.txt.backup ussawifievent_optimized.txt
rm -rf src/ && mv src_backup/ src/
```

---
💡 **提示**: 详细说明请参考 `guide/maintenance_guide.md` 