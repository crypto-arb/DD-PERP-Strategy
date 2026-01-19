#!/usr/bin/env python3
"""
StandX WebSocket 私有数据测试脚本
订阅用户持仓、余额、未成交订单
"""
import asyncio
import os
import sys
import yaml
from datetime import datetime
from typing import Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", ".."))
from adapters.standx_adapter import StandXAdapter


def _load_config() -> Dict[str, Any]:
    config_file = os.path.join(
        os.path.dirname(__file__),
        "../../../strategys/strategy_common/config.yaml",
    )
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    standx_config = config.get("exchanges", {}).get("standx", {})
    if not standx_config:
        raise ValueError("配置文件中未找到 standx 配置")
    return standx_config


async def main():
    adapter = None
    try:
        standx_config = _load_config()
        adapter = StandXAdapter(standx_config)

        # 先获取 token（API Token 方式直接可用；钱包方式会登录）
        adapter.connect()

        # 连接市场流并认证
        await adapter.connect_market_stream()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] WSS 连接成功")

        streams = [{"channel": "order"}, {"channel": "position"}, {"channel": "balance"}]
        await adapter.market_stream.authenticate(adapter.token, streams=streams)
        print("✓ 已发送认证请求")

        def on_message(message: Dict[str, Any]) -> None:
            channel = message.get("channel")
            data = message.get("data")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {channel}: {data}")

        # 为回调注册订阅
        await adapter.market_stream.subscribe("order", callback=on_message)
        await adapter.market_stream.subscribe("position", callback=on_message)
        await adapter.market_stream.subscribe("balance", callback=on_message)
        print("✓ 已订阅 order / position / balance\n")

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
