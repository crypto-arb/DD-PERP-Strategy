#!/usr/bin/env python3
"""
简单的 WebSocket 原始测试脚本
直接连接到 StandX WebSocket 并打印所有接收到的消息
优化版本：减少延迟，提高性能
"""
import asyncio
import os
import sys
import yaml
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', '..'))
from adapters.standx_adapter import StandXAdapter


async def main():
    """主函数"""
    adapter = None
    config_file = os.path.join(
        os.path.dirname(__file__),
        "../../../strategys/strategy_common/config.yaml",
    )
    
    print(f"加载配置: {config_file}")
    print("等待接收消息（按 Ctrl+C 停止）...\n")
    print("=" * 80)
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        standx_config = config.get("exchanges", {}).get("standx", {})
        if not standx_config:
            print("错误: 配置文件中未找到 standx 配置")
            return
        
        adapter = StandXAdapter(standx_config)
        await adapter.connect_market_stream()
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 连接成功")
        
        symbol = "BTC-USD"
        channels = ["depth_book"]
        
        def on_message(data: dict):
            channel = data.get("channel")
            payload = data.get("data", {})
            price = None
            best_bid = None
            best_ask = None
            
            bids = payload.get("bids") or []
            asks = payload.get("asks") or []
            best_bid = bids[0][0] if bids and len(bids[0]) >= 1 else None
            best_ask = asks[0][0] if asks and len(asks[0]) >= 1 else None
            price = best_bid or best_ask
            
            print(f"bid={best_bid} ask={best_ask}")
        
        for channel in channels:
            await adapter.subscribe_market(channel, symbol, callback=on_message)
            print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 已订阅 {symbol} {channel}")
        print("")
        
        print("开始接收消息（仅打印价格）...\n")
        await asyncio.Event().wait()
                
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if adapter and adapter.market_stream:
            await adapter.market_stream.close()


if __name__ == "__main__":
    asyncio.run(main())
