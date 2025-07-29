#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from datetime import datetime
from collections import defaultdict
import argparse

class WiFiLogProcessor:
    def __init__(self, include_system_events=True):
        self.client_sessions = defaultdict(list)
        self.reason_lines = []
        self.skip_lines = []
        self.other_lines = []
        self.include_system_events = include_system_events
        
    def parse_line(self, line):
        """解析单行日志"""
        line = line.strip()
        if not line:
            return None
            
        # 匹配时间戳
        time_match = re.search(r'(\w+ \w+ \d+ \d+:\d+:\d+)', line)
        if not time_match:
            return None
            
        timestamp = time_match.group(1)
        
        # 匹配客户端相关事件
        client_match = re.search(r'reported client=\[([^\]]+)\] (assoc|disassoc)', line)
        if client_match:
            client_mac = client_match.group(1)
            event_type = client_match.group(2)
            
            # 获取vap信息
            vap_match = re.search(r'on vap=\[([^\]]+)\]', line)
            vap = vap_match.group(1) if vap_match else ""
            
            # 获取断连原因
            reason_code = ""
            if event_type == "disassoc":
                reason_match = re.search(r'reason code=\[(\d+)\]', line)
                reason_code = reason_match.group(1) if reason_match else ""
            
            return {
                'type': 'client_event',
                'timestamp': timestamp,
                'client': client_mac,
                'event': event_type,
                'vap': vap,
                'reason_code': reason_code,
                'original_line': line
            }
        
        # 匹配reason行（系统参数变化）
        elif self.include_system_events and 'reason=' in line and 'oldCh->newCh' in line:
            return {
                'type': 'system_reason',
                'timestamp': timestamp,
                'original_line': line
            }
        
        # 匹配skip行
        elif self.include_system_events and 'skip' in line.lower():
            return {
                'type': 'skip',
                'timestamp': timestamp,
                'original_line': line
            }
        
        # 其他类型的行（可选记录）
        elif self.include_system_events and not ('reason=' in line and 'oldCh->newCh' in line) and 'skip' not in line.lower():
            return {
                'type': 'other',
                'timestamp': timestamp,
                'original_line': line
            }
            
        return None
    
    def process_file(self, input_file):
        """处理输入文件"""
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                parsed = self.parse_line(line)
                if parsed:
                    if parsed['type'] == 'client_event':
                        self.client_sessions[parsed['client']].append(parsed)
                    elif parsed['type'] == 'system_reason':
                        self.reason_lines.append(parsed)
                    elif parsed['type'] == 'skip':
                        self.skip_lines.append(parsed)
                    elif parsed['type'] == 'other':
                        self.other_lines.append(parsed)
    
    def pair_sessions(self):
        """配对每个客户端的assoc和disassoc事件"""
        paired_sessions = []
        
        for client, events in self.client_sessions.items():
            # 按时间排序
            events.sort(key=lambda x: datetime.strptime(x['timestamp'], '%a %b %d %H:%M:%S'))
            
            i = 0
            while i < len(events):
                current_event = events[i]
                
                if current_event['event'] == 'assoc':
                    # 寻找对应的disassoc事件
                    j = i + 1
                    while j < len(events) and events[j]['event'] != 'disassoc':
                        j += 1
                    
                    if j < len(events):
                        # 找到配对的disassoc
                        disassoc_event = events[j]
                        paired_sessions.append({
                            'client': client,
                            'assoc_time': current_event['timestamp'],
                            'assoc_vap': current_event['vap'],
                            'disassoc_time': disassoc_event['timestamp'],
                            'disassoc_vap': disassoc_event['vap'],
                            'reason_code': disassoc_event['reason_code'],
                            'assoc_line': current_event['original_line'],
                            'disassoc_line': disassoc_event['original_line']
                        })
                        i = j + 1
                    else:
                        # 没有找到配对的disassoc，可能是未完成的连接
                        paired_sessions.append({
                            'client': client,
                            'assoc_time': current_event['timestamp'],
                            'assoc_vap': current_event['vap'],
                            'disassoc_time': '',
                            'disassoc_vap': '',
                            'reason_code': '',
                            'assoc_line': current_event['original_line'],
                            'disassoc_line': ''
                        })
                        i += 1
                else:
                    # 如果是单独的disassoc（没有对应的assoc），也记录
                    paired_sessions.append({
                        'client': client,
                        'assoc_time': '',
                        'assoc_vap': '',
                        'disassoc_time': current_event['timestamp'],
                        'disassoc_vap': current_event['vap'],
                        'reason_code': current_event['reason_code'],
                        'assoc_line': '',
                        'disassoc_line': current_event['original_line']
                    })
                    i += 1
        
        return paired_sessions
    
    def sort_sessions(self, sessions):
        """排序：优先按客户端，然后按时间"""
        return sorted(sessions, key=lambda x: (
            x['client'],
            datetime.strptime(x['assoc_time'], '%a %b %d %H:%M:%S') if x['assoc_time'] else datetime.min
        ))
    
    def write_output(self, sessions, output_file):
        """写入输出文件"""
        with open(output_file, 'w', encoding='ascii', errors='ignore') as f:
            # 写入表头
            f.write("=" * 120 + "\n")
            f.write("WiFi Client Session Analysis Report\n")
            f.write("=" * 120 + "\n")
            f.write(f"Total Sessions: {len(sessions)}\n")
            f.write(f"Unique Clients: {len(set(s['client'] for s in sessions))}\n")
            f.write("=" * 120 + "\n\n")
            
            current_client = ""
            for session in sessions:
                # 如果是新的客户端，添加分隔符
                if session['client'] != current_client:
                    if current_client:
                        f.write("\n" + "-" * 100 + "\n\n")
                    current_client = session['client']
                    f.write(f"CLIENT: {current_client}\n")
                    f.write("-" * 100 + "\n")
                
                # 写入会话信息
                if session['assoc_time'] and session['disassoc_time']:
                    # 完整的连接-断开会话
                    duration = self.calculate_duration(session['assoc_time'], session['disassoc_time'])
                    f.write(f"ASSOC:    {session['assoc_time']} on {session['assoc_vap']}\n")
                    f.write(f"DISASSOC: {session['disassoc_time']} on {session['disassoc_vap']} (reason: {session['reason_code']})\n")
                    f.write(f"DURATION: {duration}\n")
                elif session['assoc_time']:
                    # 只有连接，没有断开
                    f.write(f"ASSOC:    {session['assoc_time']} on {session['assoc_vap']} (No disconnection recorded)\n")
                else:
                    # 只有断开，没有连接
                    f.write(f"DISASSOC: {session['disassoc_time']} on {session['disassoc_vap']} (reason: {session['reason_code']}) (No prior association recorded)\n")
                
                f.write("\n")
            
            # 写入系统reason行
            if self.reason_lines:
                f.write("\n" + "=" * 120 + "\n")
                f.write("System Parameter Changes\n")
                f.write("=" * 120 + "\n")
                for reason in self.reason_lines:
                    f.write(f"{reason['timestamp']}: {reason['original_line']}\n")
            
            # 写入skip行
            if self.skip_lines:
                f.write("\n" + "=" * 120 + "\n")
                f.write("Skip Events\n")
                f.write("=" * 120 + "\n")
                for skip in self.skip_lines:
                    f.write(f"{skip['timestamp']}: {skip['original_line']}\n")
            
            # 写入其他类型的行
            if self.other_lines:
                f.write("\n" + "=" * 120 + "\n")
                f.write("Other Events\n")
                f.write("=" * 120 + "\n")
                for other in self.other_lines:
                    f.write(f"{other['timestamp']}: {other['original_line']}\n")
    
    def calculate_duration(self, start_time, end_time):
        """计算连接持续时间"""
        try:
            start = datetime.strptime(start_time, '%a %b %d %H:%M:%S')
            end = datetime.strptime(end_time, '%a %b %d %H:%M:%S')
            duration = end - start
            
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        except:
            return "Unknown"

def main():
    parser = argparse.ArgumentParser(description='WiFi日志数据处理工具')
    parser.add_argument('input_file', help='输入日志文件路径')
    parser.add_argument('-o', '--output', default='processed_wifi_log.txt', help='输出文件路径（默认：processed_wifi_log.txt）')
    parser.add_argument('--no-system-events', action='store_true', help='不包含系统事件（reason、skip等行）')
    
    args = parser.parse_args()
    
    processor = WiFiLogProcessor(include_system_events=not args.no_system_events)
    
    print("正在处理日志文件...")
    processor.process_file(args.input_file)
    
    print("正在配对连接会话...")
    sessions = processor.pair_sessions()
    
    print("正在排序...")
    sorted_sessions = processor.sort_sessions(sessions)
    
    print(f"正在写入输出文件: {args.output}")
    processor.write_output(sorted_sessions, args.output)
    
    print(f"处理完成！")
    print(f"总共处理了 {len(sorted_sessions)} 个会话")
    print(f"涉及 {len(set(s['client'] for s in sorted_sessions))} 个客户端")
    print(f"系统参数变更: {len(processor.reason_lines)} 条")
    print(f"Skip事件: {len(processor.skip_lines)} 条")
    print(f"其他事件: {len(processor.other_lines)} 条")
    print(f"结果已保存到: {args.output}")

if __name__ == "__main__":
    main() 