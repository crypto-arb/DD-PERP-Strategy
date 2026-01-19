#!/usr/bin/env python3
"""
GRVT WebSocket 私有数据测试脚本
订阅用户持仓 / 订单 / 账户状态
"""
import asyncio
import os
import sys
import yaml
from datetime import datetime
from typing import Any, Dict

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", ".."))
from adapters.grvt_adapter import GrvtAdapter
from exchange.exchange_grvt.src.pysdk.grvt_ccxt_env import GrvtWSEndpointType

SYMBOL = "BTC_USDT_Perp"
STREAMS = ["position", "order", "state"]


def _load_config() -> Dict[str, Any]:
    config_file = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    auth = config.get("auth", {})
    env = os.getenv("GRVT_ENV", config.get("env", "prod"))

    trading_account_id = os.getenv(
        "GRVT_TRADING_ACCOUNT_ID", auth.get("trading_account_id", "")
    )
    sub_account_id = os.getenv("GRVT_SUB_ACCOUNT_ID", "")
    if sub_account_id:
        trading_account_id = sub_account_id

    return {
        "exchange_name": "grvt",
        "env": env,
        "api_key": os.getenv("GRVT_API_KEY", auth.get("api_key", "")),
        "trading_account_id": trading_account_id,
        "private_key": os.getenv("GRVT_PRIVATE_KEY", auth.get("private_key", "")),
        "api_ws_version": os.getenv("GRVT_WS_STREAM_VERSION", "v1"),
    }


async def main():
    adapter = None
    try:
        config = _load_config()
        adapter = GrvtAdapter(config)
        await adapter.connect_ws()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] WSS 已连接")

        def on_message(message: Dict[str, Any]) -> None:
            print(message)
            stream = message.get("stream")
            selector = message.get("selector")
            feed = message.get("feed")
            if feed is None and isinstance(message.get("params"), dict):
                feed = message["params"].get("feed")
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] stream={stream} "
                f"selector={selector} feed={feed}"
            )

        ws_client = adapter.ws_client
        stream_params = {
            "position": {},
            "state": {},
            "order": {"instrument": SYMBOL},
        }
        for stream in STREAMS:
            params = stream_params.get(stream, {})
            await adapter.subscribe_ws(
                stream=stream,
                params=params,
                callback=on_message,
                ws_end_point_type=GrvtWSEndpointType.TRADE_DATA_RPC_FULL,
            )
            if ws_client:
                try:
                    selector = ws_client._construct_selector(stream, params)
                    print(f"已订阅 {stream} selector={selector}")
                except Exception:
                    print(f"已订阅 {stream} params={params}")
            else:
                print(f"已订阅 {stream} params={params}")

        print("\n开始接收私有数据（按 Ctrl+C 停止）...\n")
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # GrvtCcxtWS 内部有重连循环，这里不强制关闭
        pass


if __name__ == "__main__":
    asyncio.run(main())
