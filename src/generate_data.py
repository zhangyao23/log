#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFi日志数据生成脚本
生成至少500条包含6种主要断连原因的WiFi事件日志
"""

import random
from datetime import datetime, timedelta
import math

class WiFiLogGenerator:
    def __init__(self):
        # 6种主要断连原因
        self.reason_codes = {
            1: "未指定原因",
            3: "客户端主动离开", 
            4: "因不活跃断连",
            5: "AP过载",
            15: "4-Way握手超时",
            23: "802.1X认证失败"
        }
        
        # 客户端MAC地址池
        self.client_macs = [
            "2e:55:b9:42:06:aa",
            "4c:79:6e:de:4d:1f", 
            "d6:99:0f:58:6c:79",
            "a2:c4:7f:38:21:9b",
            "f8:e6:1a:57:02:45",
            "bc:d1:77:e4:58:a3",
            "1a:2b:3c:4d:5e:6f",
            "7g:8h:9i:0j:1k:2l"
        ]
        
        # VAP接口
        self.vaps = ["rai0", "rai4"]
        
        # 配置变更的reason (这个不是断连原因)
        self.config_reasons = [1, 2, 3]
        
        # 基础时间
        self.start_time = datetime(2023, 7, 7, 8, 0, 0)
        
    def generate_timestamp(self, base_time):
        """生成时间戳字符串"""
        return base_time.strftime("%a %b %d %H:%M:%S")
    
    def generate_config_change(self, timestamp):
        """生成配置变更事件"""
        reason = random.choice(self.config_reasons)
        old_ch = random.randint(1, 11)
        new_ch = random.randint(1, 11)
        while new_ch == old_ch:
            new_ch = random.randint(1, 11)
        
        old_bw = random.choice(["20MHz", "40MHz", "80MHz"])
        new_bw = random.choice(["20MHz", "40MHz", "80MHz"])
        
        old_power = round(random.uniform(12.0, 20.0), 6)
        new_power = round(random.uniform(12.0, 20.0), 6)
        
        return f"USSA > {timestamp} | NOTICE  | reason=[{reason}], oldCh->newCh=[{old_ch}]->[{new_ch}], oldBw->newBw=[{old_bw}]->[{new_bw}], oldTxPower->newTxPower=[{old_power:.6f}]->[{new_power:.6f}]"
    
    def generate_client_event(self, timestamp, mac, event_type, vap, reason_code=None):
        """生成客户端事件"""
        if event_type == "assoc":
            return f"USSA > {timestamp} | NOTICE  | reported client=[{mac}] assoc on vap=[{vap}]"
        else:  # disassoc
            return f"USSA > {timestamp} | NOTICE  | reported client=[{mac}] disassoc on vap=[{vap}], reason code=[{reason_code}]"
    
    def generate_session(self, start_time, client_mac, vap):
        """生成一个完整的客户端会话 (assoc -> disassoc)"""
        events = []
        
        # 关联事件
        assoc_time = start_time
        assoc_event = self.generate_client_event(
            self.generate_timestamp(assoc_time),
            client_mac,
            "assoc", 
            vap
        )
        events.append((assoc_time, assoc_event))
        
        # 会话持续时间 (3-60分钟，不同reason code有不同的倾向)
        if random.random() < 0.3:  # 30%的短会话
            duration_minutes = random.randint(3, 10)
        elif random.random() < 0.7:  # 40%的中等会话
            duration_minutes = random.randint(10, 30)
        else:  # 30%的长会话
            duration_minutes = random.randint(30, 120)
        
        # 断连事件
        disassoc_time = assoc_time + timedelta(minutes=duration_minutes)
        reason_code = self.choose_reason_code(duration_minutes)
        
        disassoc_event = self.generate_client_event(
            self.generate_timestamp(disassoc_time),
            client_mac,
            "disassoc",
            vap,
            reason_code
        )
        events.append((disassoc_time, disassoc_event))
        
        return events, disassoc_time
    
    def choose_reason_code(self, duration_minutes):
        """根据会话持续时间选择合适的断连原因"""
        # 不同持续时间倾向于不同的断连原因
        if duration_minutes < 5:
            # 短会话：更可能是认证问题或AP过载
            return random.choices([15, 23, 5, 1], weights=[30, 25, 25, 20])[0]
        elif duration_minutes < 20:
            # 中等会话：各种原因都可能
            return random.choices([1, 4, 15, 23, 5, 3], weights=[25, 20, 15, 15, 15, 10])[0]
        else:
            # 长会话：更可能是不活跃或主动离开
            return random.choices([4, 3, 1, 5], weights=[40, 30, 20, 10])[0]
    
    def generate_data(self, target_events=500):
        """生成至少target_events条事件的数据"""
        all_events = []
        current_time = self.start_time
        event_count = 0
        
        # 客户端状态跟踪 (是否已连接)
        client_states = {mac: False for mac in self.client_macs}
        
        while event_count < target_events:
            # 每10-30分钟可能有配置变更
            if random.random() < 0.05:  # 5%概率
                config_event = self.generate_config_change(self.generate_timestamp(current_time))
                all_events.append((current_time, config_event))
                event_count += 1
                current_time += timedelta(minutes=random.randint(1, 3))
            
            # 选择一个客户端
            client_mac = random.choice(self.client_macs)
            vap = random.choice(self.vaps)
            
            # 如果客户端未连接，生成新会话
            if not client_states[client_mac]:
                session_events, end_time = self.generate_session(current_time, client_mac, vap)
                all_events.extend(session_events)
                event_count += len(session_events)
                client_states[client_mac] = False  # 会话结束后状态为未连接
                
                # 更新时间到会话结束
                current_time = end_time + timedelta(minutes=random.randint(1, 5))
            else:
                # 如果客户端已连接，跳过或生成断连
                current_time += timedelta(minutes=random.randint(1, 3))
        
        # 按时间排序
        all_events.sort(key=lambda x: x[0])
        
        return [event[1] for event in all_events]
    
    def save_to_file(self, events, filename):
        """保存事件到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            for event in events:
                f.write(event + '\n')
        
        print(f"已生成 {len(events)} 条事件，保存到 {filename}")
        
        # 统计断连原因分布
        reason_counts = {}
        for event in events:
            if "disassoc" in event and "reason code=" in event:
                reason_code = int(event.split("reason code=[")[1].split("]")[0])
                reason_counts[reason_code] = reason_counts.get(reason_code, 0) + 1
        
        print("\n断连原因分布:")
        for code, count in sorted(reason_counts.items()):
            description = self.reason_codes.get(code, "未知")
            print(f"  Code {code}: {count}次 - {description}")
        
        return len(events), reason_counts

def main():
    print("WiFi日志数据生成器")
    print("=" * 50)
    
    generator = WiFiLogGenerator()
    
    # 生成至少500条事件
    events = generator.generate_data(target_events=500)
    
    # 保存到文件
    event_count, reason_counts = generator.save_to_file(events, "../ussawifievent_optimized.txt")
    
    print(f"\n✅ 成功生成 {event_count} 条事件")
    print(f"✅ 包含 {len(reason_counts)} 种不同的断连原因")
    print(f"✅ 数据已保存到 ussawifievent_optimized.txt")

if __name__ == "__main__":
    main() 