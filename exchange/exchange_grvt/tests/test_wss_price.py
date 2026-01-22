#!/usr/bin/env python3
"""
GRVT WebSocket 价格测试脚本
使用 GrvtAdapter 连接 WSS 并订阅 BTC 价格
"""
import asyncio
import os
import sys
import yaml
from datetime import datetime
from typing import Any, Dict, Optional

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", ".."))
from adapters.grvt_adapter import GrvtAdapter

SYMBOL = "BTC_USDT_Perp"
STREAM = "ticker.s"


def _load_config() -> Dict[str, Any]:
    config_file = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    auth = config.get("auth", {})
    env = os.getenv("GRVT_ENV", config.get("env", "prod"))

    return {
        "exchange_name": "grvt",
        "env": env,
        "api_key": os.getenv("GRVT_API_KEY", auth.get("api_key", "")),
        "trading_account_id": os.getenv(
            "GRVT_TRADING_ACCOUNT_ID", auth.get("trading_account_id", "")
        ),
        "private_key": os.getenv("GRVT_PRIVATE_KEY", auth.get("private_key", "")),
        "api_ws_version": os.getenv("GRVT_WS_STREAM_VERSION", "v1"),
    }


def _extract_feed(message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if isinstance(message.get("feed"), dict):
        return message["feed"]
    if isinstance(message.get("data"), dict) and isinstance(message["data"].get("feed"), dict):
        return message["data"]["feed"]
    if isinstance(message.get("params"), dict):
        params = message["params"]
        if isinstance(params.get("feed"), dict):
            return params["feed"]
        if isinstance(params.get("data"), dict) and isinstance(params["data"].get("feed"), dict):
            return params["data"]["feed"]
    if isinstance(message.get("result"), dict) and isinstance(message["result"].get("feed"), dict):
        return message["result"]["feed"]
    return None


async def main():
    config = _load_config()
    adapter = GrvtAdapter(config)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 连接 GRVT WSS...")
    await adapter.connect_ws()
    print("✓ 连接成功")

    def on_message(message: Dict[str, Any]) -> None:
        feed = _extract_feed(message) or {}
        best_bid = feed.get("best_bid_price") or feed.get("best_bid")
        best_ask = feed.get("best_ask_price") or feed.get("best_ask")
        last_price = feed.get("last_price") or feed.get("price")

        if best_bid is not None or best_ask is not None:
            print(f"bid={best_bid} ask={best_ask}")
        elif last_price is not None:
            print(last_price)

    await adapter.subscribe_ws(
        stream=STREAM,
        params={"instrument": SYMBOL},
        callback=on_message,
    )
    print(f"已订阅 {SYMBOL} ({STREAM})")
    print("开始接收消息（仅打印价格）...\n")

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
