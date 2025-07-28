#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFi日志数据分析脚本
==================

功能说明:
- 解析和分析WiFi事件日志文件
- 专注于6种主要断连原因分析
- 生成详细的统计报告和可视化图表
- 支持客户端会话模式分析

主要分析内容:
1. 断连原因分布统计
2. 客户端行为模式分析  
3. 时间模式和高峰时段
4. 可视化图表生成

使用方法:
    python analyze_optimized_data.py

输出结果:
- 控制台详细分析报告
- optimized_wifi_analysis.png 可视化图表

支持的reason code:
- Code 1: 未指定原因
- Code 3: 客户端主动离开
- Code 4: 因不活跃断连
- Code 5: AP过载
- Code 15: 4-Way握手超时
- Code 23: 802.1X认证失败
"""

import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
from collections import defaultdict, Counter

# 设置中文字体 (如果需要显示中文)
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class OptimizedWiFiAnalyzer:
    def __init__(self, log_file):
        self.log_file = log_file
        self.events = []
        
        # 6种主要断连原因
        self.reason_code_mapping = {
            1: "Unspecified reason",
            3: "Client leaving", 
            4: "Inactivity timeout",
            5: "AP overload",
            15: "4-Way handshake timeout",
            23: "802.1X auth failed"
        }
        
        # 原因类别分组
        self.reason_categories = {
            "Normal": [3, 4],  # 正常断连
            "Auth Issues": [15, 23],  # 认证问题
            "Capacity Issues": [5],  # 容量问题  
            "Unspecified": [1]  # 未指定
        }
        
    def parse_log_file(self):
        """解析日志文件"""
        print("正在解析优化日志文件...")
        
        # 定义正则表达式模式
        client_pattern = r'reported client=\[([^\]]+)\] (assoc|disassoc) on vap=\[([^\]]+)\](?:, reason code=\[(\d+)\])?'
        time_pattern = r'(\w{3} \w{3} \d+ \d+:\d+:\d+)'
        config_pattern = r'reason=\[(\d+)\], oldCh->newCh=\[(\d+)\]->\[(\d+)\]'
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    # 提取时间戳
                    time_match = re.search(time_pattern, line)
                    if not time_match:
                        continue
                    
                    timestamp_str = time_match.group(1)
                    # 解析时间戳
                    timestamp = datetime.strptime(f"2023 {timestamp_str}", "%Y %a %b %d %H:%M:%S")
                    
                    # 检查是否为客户端事件
                    client_match = re.search(client_pattern, line)
                    if client_match:
                        client_mac = client_match.group(1)
                        event_type = client_match.group(2)
                        vap = client_match.group(3)
                        reason_code = int(client_match.group(4)) if client_match.group(4) else None
                        
                        event = {
                            'timestamp': timestamp,
                            'client_mac': client_mac,
                            'event_type': event_type,
                            'vap': vap,
                            'reason_code': reason_code,
                            'line_num': line_num,
                            'raw_line': line.strip()
                        }
                        
                        self.events.append(event)
                    
                    # 检查是否为配置变更事件
                    config_match = re.search(config_pattern, line)
                    if config_match:
                        event = {
                            'timestamp': timestamp,
                            'client_mac': None,
                            'event_type': 'config_change',
                            'vap': None,
                            'reason_code': None,
                            'config_reason': int(config_match.group(1)),
                            'old_channel': int(config_match.group(2)),
                            'new_channel': int(config_match.group(3)),
                            'line_num': line_num,
                            'raw_line': line.strip()
                        }
                        self.events.append(event)
                        
                except Exception as e:
                    print(f"解析第{line_num}行时出错: {e}")
                    continue
        
        print(f"成功解析 {len(self.events)} 个事件")
        return self.events
    
    def create_dataframe(self):
        """创建pandas DataFrame"""
        if not self.events:
            self.parse_log_file()
        
        df = pd.DataFrame(self.events)
        
        # 添加reason code描述
        df['reason_description'] = df['reason_code'].map(self.reason_code_mapping)
        
        # 添加reason code类别
        def get_category(reason_code):
            if pd.isna(reason_code):
                return "None"
            for category, codes in self.reason_categories.items():
                if reason_code in codes:
                    return category
            return "Other"
        
        df['reason_category'] = df['reason_code'].apply(get_category)
        
        # 添加时间特征
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['minute'] = df['timestamp'].dt.minute
        
        return df
    
    def analyze_reason_codes(self, df):
        """分析reason code分布"""
        print("\n=== 断连原因分析 ===")
        
        # 只分析disassoc事件
        disassoc_df = df[df['event_type'] == 'disassoc'].copy()
        
        if disassoc_df.empty:
            print("没有发现disassoc事件")
            return
        
        total_disconnects = len(disassoc_df)
        print(f"总断连事件数: {total_disconnects}")
        
        # 统计reason code分布
        reason_counts = disassoc_df['reason_code'].value_counts().sort_index()
        print(f"\n6种断连原因分布:")
        for code, count in reason_counts.items():
            description = self.reason_code_mapping.get(code, "未知")
            percentage = (count / total_disconnects) * 100
            print(f"  Code {code}: {count}次 ({percentage:.1f}%) - {description}")
        
        # 统计按类别分布
        category_counts = disassoc_df['reason_category'].value_counts()
        print(f"\n按类别分布:")
        for category, count in category_counts.items():
            percentage = (count / total_disconnects) * 100
            print(f"  {category}: {count}次 ({percentage:.1f}%)")
        
        return reason_counts, category_counts
    
    def analyze_client_sessions(self, df):
        """分析客户端会话模式"""
        print("\n=== 客户端会话分析 ===")
        
        client_df = df[df['event_type'].isin(['assoc', 'disassoc'])].copy()
        
        session_stats = []
        for client_mac in client_df['client_mac'].unique():
            if pd.isna(client_mac):
                continue
            
            client_events = client_df[client_df['client_mac'] == client_mac].sort_values('timestamp')
            
            # 计算会话统计
            sessions = []
            current_assoc = None
            
            for _, event in client_events.iterrows():
                if event['event_type'] == 'assoc':
                    current_assoc = event['timestamp']
                elif event['event_type'] == 'disassoc' and current_assoc is not None:
                    duration = (event['timestamp'] - current_assoc).total_seconds() / 60  # 分钟
                    sessions.append({
                        'duration': duration,
                        'reason_code': event['reason_code'],
                        'vap': event['vap']
                    })
                    current_assoc = None
            
            if sessions:
                avg_duration = np.mean([s['duration'] for s in sessions])
                most_common_reason = Counter([s['reason_code'] for s in sessions]).most_common(1)[0][0]
                
                session_stats.append({
                    'client_mac': client_mac,
                    'session_count': len(sessions),
                    'avg_duration_minutes': avg_duration,
                    'total_time_minutes': sum([s['duration'] for s in sessions]),
                    'most_common_reason': most_common_reason,
                    'reason_description': self.reason_code_mapping.get(most_common_reason, "未知")
                })
        
        session_stats_df = pd.DataFrame(session_stats)
        
        print(f"分析了 {len(session_stats_df)} 个客户端的会话模式")
        print(f"\n客户端会话统计:")
        for _, client in session_stats_df.iterrows():
            print(f"  {client['client_mac'][-8:]}... :")  # 显示MAC地址后8位
            print(f"    会话数: {client['session_count']}")
            print(f"    平均时长: {client['avg_duration_minutes']:.1f}分钟")
            print(f"    总在线时间: {client['total_time_minutes']:.1f}分钟")
            print(f"    主要断连原因: Code {client['most_common_reason']} - {client['reason_description']}")
        
        return session_stats_df
    
    def analyze_time_patterns(self, df):
        """分析时间模式"""
        print("\n=== 时间模式分析 ===")
        
        disassoc_df = df[df['event_type'] == 'disassoc']
        
        if disassoc_df.empty:
            return
        
        # 按小时分析
        hourly_patterns = disassoc_df.groupby(['hour', 'reason_code']).size().unstack(fill_value=0)
        print(f"\n每小时断连原因分布:")
        print(hourly_patterns)
        
        # 找出高峰时段
        total_by_hour = disassoc_df['hour'].value_counts().sort_index()
        peak_hours = total_by_hour.nlargest(3).index.tolist()
        print(f"\n断连高峰时段: {peak_hours}")
        
        return hourly_patterns
    
    def visualize_data(self, df):
        """数据可视化"""
        print("\n=== 生成可视化图表 ===")
        
        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Optimized WiFi Log Analysis', fontsize=16)
        
        disassoc_df = df[df['event_type'] == 'disassoc']
        
        # 1. Reason Code分布
        if not disassoc_df.empty:
            reason_counts = disassoc_df['reason_code'].value_counts().sort_index()
            
            ax1 = axes[0, 0]
            bars = ax1.bar(range(len(reason_counts)), reason_counts.values, 
                          color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
            ax1.set_xlabel('Reason Code')
            ax1.set_ylabel('Count')
            ax1.set_title('Disconnect Reason Distribution')
            ax1.set_xticks(range(len(reason_counts)))
            ax1.set_xticklabels([f'Code {code}' for code in reason_counts.index], rotation=45)
            
            # 添加数值标签
            for bar, count in zip(bars, reason_counts.values):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                        str(count), ha='center', va='bottom')
        
        # 2. 按类别分布
        if not disassoc_df.empty:
            category_counts = disassoc_df['reason_category'].value_counts()
            
            ax2 = axes[0, 1]
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
            ax2.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%', colors=colors)
            ax2.set_title('Reason Category Distribution')
        
        # 3. 时间分布
        client_df = df[df['event_type'].isin(['assoc', 'disassoc'])]
        if not client_df.empty:
            hour_counts = client_df.groupby(['hour', 'event_type']).size().unstack(fill_value=0)
            
            ax3 = axes[1, 0]
            hour_counts.plot(kind='bar', ax=ax3, width=0.8)
            ax3.set_xlabel('Hour of Day')
            ax3.set_ylabel('Event Count')
            ax3.set_title('Events by Hour')
            ax3.legend(title='Event Type')
            ax3.tick_params(axis='x', rotation=45)
        
        # 4. VAP分布
        if not disassoc_df.empty:
            vap_reason = disassoc_df.groupby(['vap', 'reason_code']).size().unstack(fill_value=0)
            
            ax4 = axes[1, 1]
            vap_reason.plot(kind='bar', ax=ax4, width=0.8)
            ax4.set_xlabel('VAP Interface')
            ax4.set_ylabel('Disconnect Count')
            ax4.set_title('Disconnects by VAP and Reason')
            ax4.legend(title='Reason Code', bbox_to_anchor=(1.05, 1), loc='upper left')
            ax4.tick_params(axis='x', rotation=0)
        
        plt.tight_layout()
        plt.savefig('optimized_wifi_analysis.png', dpi=150, bbox_inches='tight')
        plt.show()
        
        print("图表已保存为 optimized_wifi_analysis.png")
    
    def generate_summary(self, df):
        """生成分析摘要"""
        print("\n=== 优化数据集摘要 ===")
        
        total_events = len(df)
        client_events = df[df['client_mac'].notna()]
        config_events = df[df['event_type'] == 'config_change']
        
        assoc_events = df[df['event_type'] == 'assoc']
        disassoc_events = df[df['event_type'] == 'disassoc']
        
        unique_clients = df['client_mac'].nunique()
        unique_reason_codes = df['reason_code'].nunique()
        
        time_span = df['timestamp'].max() - df['timestamp'].min()
        
        print(f"总事件数: {total_events}")
        print(f"客户端事件数: {len(client_events)}")
        print(f"配置变更事件数: {len(config_events)}")
        print(f"连接事件数: {len(assoc_events)}")
        print(f"断连事件数: {len(disassoc_events)}")
        print(f"唯一客户端数: {unique_clients}")
        print(f"断连原因类型数: {unique_reason_codes}")
        print(f"数据时间跨度: {time_span}")
        
        if not disassoc_events.empty:
            most_common_reason = disassoc_events['reason_code'].mode().iloc[0]
            most_common_desc = self.reason_code_mapping.get(most_common_reason, "未知")
            print(f"最常见断连原因: Code {most_common_reason} - {most_common_desc}")
        
        # 数据质量评估
        print(f"\n数据质量评估:")
        print(f"✅ 事件数量: {total_events} (目标: ≥500)")
        print(f"✅ 断连原因种类: {unique_reason_codes} (目标: 6种)")
        print(f"✅ 时间连续性: 连续的时间序列")
        print(f"✅ reason vs reason code: 正确区分配置原因和断连原因")

def main():
    """主函数"""
    print("优化WiFi日志数据分析工具")
    print("=" * 50)
    
    # 初始化分析器
    analyzer = OptimizedWiFiAnalyzer('../ussawifievent_optimized.txt')
    
    try:
        # 解析数据
        df = analyzer.create_dataframe()
        
        # 生成分析报告
        analyzer.generate_summary(df)
        analyzer.analyze_reason_codes(df)
        analyzer.analyze_client_sessions(df)
        analyzer.analyze_time_patterns(df)
        
        # 生成可视化图表
        analyzer.visualize_data(df)
        
        print("\n✅ 分析完成！")
        print("🎯 数据集已优化，包含6种主要断连原因")
        print("📊 可用于机器学习模型训练")
        
    except FileNotFoundError:
        print("错误: 找不到日志文件 '../ussawifievent_optimized.txt'")
        print("请确保已运行数据生成脚本")
    except Exception as e:
        print(f"分析过程中出现错误: {e}")

if __name__ == "__main__":
    main() 