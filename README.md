# Nado & Variational 跨平台套利交易工具

一个自动化交易工具，用于在 Nado 和 Variational 两个交易平台之间执行套利策略。通过浏览器自动化技术，实现跨平台的自动下单和订单管理。

## 功能特性

- 🔄 **跨平台套利**：支持在 Nado 和 Variational 之间执行套利交易
- 📊 **实时价格获取**：通过 API 实时获取交易对价格，确保订单价格准确
- 🔁 **自动重试机制**：订单未成交时自动重新获取价格并重新下单
- ⏱️ **灵活的执行策略**：支持单次、多次和无限循环执行
- 📝 **配置文件管理**：支持多个配置文件，可灵活切换不同交易对
- 🛡️ **安全中断**：执行过程中可按 Ctrl+C 安全返回菜单

## 环境要求

- Python 3.9+
- MoreLogin 浏览器环境管理工具（需要运行在 localhost:40000）
- 已配置的 Nado 和 Variational 浏览器环境 ID

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd DD-strategy-bot
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 确保 MoreLogin 服务运行

确保 MoreLogin 的 API 服务运行在 `http://localhost:40000`，并且已经创建了浏览器环境。

## 配置说明

### 配置文件格式

配置文件为 CSV 格式，包含以下字段：

| 字段 | 说明 | 示例 |
|------|------|------|
| `nado_env_id` | Nado 平台的浏览器环境 ID | 2008001765488267264 |
| `variational_env_id` | Variational 平台的浏览器环境 ID | 2008001765131751424 |
| `symbol` | 交易对符号（大写） | BTC, ETH, AAVE |
| `size` | 订单大小 | 0.05 |
| `price_offset` | 价格偏移量（正数表示高于市价，负数表示低于市价） | 5 或 -5 |
| `repeat_count` | 重复执行次数（用于方法3和4） | 5 |
| `sleep_range` | 休眠时间范围（秒），格式：min-max | 5-20 |

### 配置文件示例

创建 `config_btc.csv`：

```csv
nado_env_id,variational_env_id,symbol,size,price_offset,repeat_count,sleep_range
2008001765488267264,2008001765131751424,BTC,0.05,5,5,5-20
```

创建 `config_aave.csv`：

```csv
nado_env_id,variational_env_id,symbol,size,price_offset,repeat_count,sleep_range
2008001765488267264,2008001765131751424,AAVE,3,0,5,10-50
```

### 价格偏移说明

- **做多订单**：使用 `bid` 价格，减去偏移量（更低价买入）
- **做空订单**：使用 `ask` 价格，加上偏移量（更高价卖出）

例如：
- `price_offset = 5`：做多时，订单价格 = bid - 5；做空时，订单价格 = ask + 5
- `price_offset = -5`：做多时，订单价格 = bid - (-5) = bid + 5；做空时，订单价格 = ask + 5

## 使用方法

### 基本用法

```bash
# 使用默认配置文件 config.csv
python nado_var.py

# 指定配置文件
python nado_var.py --config config_btc.csv
python nado_var.py --config config_aave.csv
```

### 命令行参数

```bash
python nado_var.py -h
# 或
python nado_var.py --help
```

参数说明：
- `-c, --config`: 指定配置文件路径（默认: config.csv）

### 菜单选项

运行程序后，会显示菜单：

```
==================================================
菜单
==================================================
1. 单次做多Nado做空Variational
2. 单次做空Nado做多Variational
3. 多次做多Nado做空Variational
4. 多次做空Nado做多Variational
5. 循环执行：做多Nado做空Variational -> 休眠 -> 做空Nado做多Variational

提示: 执行方法时按 Ctrl+C 可返回菜单，菜单界面按 Ctrl+C 退出程序
==================================================
```

### 功能说明

#### 方法1：单次做多Nado做空Variational
- 在 Nado 平台做多
- 订单成交后，在 Variational 平台做空
- 适合单次套利操作

#### 方法2：单次做空Nado做多Variational
- 在 Nado 平台做空
- 订单成交后，在 Variational 平台做多
- 适合单次套利操作

#### 方法3：多次做多Nado做空Variational
- 循环执行方法1的操作
- 执行次数由配置文件中的 `repeat_count` 决定
- 每次执行后随机休眠（由 `sleep_range` 配置）

#### 方法4：多次做空Nado做多Variational
- 循环执行方法2的操作
- 执行次数由配置文件中的 `repeat_count` 决定
- 每次执行后随机休眠（由 `sleep_range` 配置）

#### 方法5：循环执行策略
- 无限循环执行以下步骤：
  1. 做多Nado做空Variational
  2. 休眠随机秒数
  3. 做空Nado做多Variational
  4. 休眠随机秒数
- 按 Ctrl+C 可停止循环并返回菜单

## 工作流程

### 下单流程

1. **获取价格**：通过 API 获取交易对的实时价格（bid/ask）
2. **计算订单价格**：根据价格偏移量计算订单价格
3. **提交订单**：在 Nado 平台提交限价单
4. **监控订单**：监控订单是否成交（通过持仓变化判断）
5. **自动重试**：如果30秒内未成交，自动取消订单并重新获取价格下单
6. **执行反向操作**：订单成交后，在 Variational 平台执行反向操作

### 价格获取机制

- 每次下单前都会重新获取最新价格
- 使用 Nado API 获取实时价格
- `product_id` 会缓存到本地，避免重复查询
- 价格数据不缓存，确保每次都是最新价格

## 注意事项

### ⚠️ 重要提示

1. **风险提示**：本工具仅用于自动化交易，使用前请充分了解交易风险
2. **环境配置**：确保 MoreLogin 服务正常运行，浏览器环境已正确配置
3. **网络连接**：需要稳定的网络连接，确保能够访问 Nado API
4. **资金管理**：请合理设置订单大小，避免过度交易
5. **价格偏移**：合理设置价格偏移量，确保订单能够成交

### 使用建议

1. **测试环境**：建议先在测试环境或小额资金下测试
2. **监控运行**：运行过程中注意监控程序状态和订单情况
3. **配置文件**：修改配置文件后无需重启程序，下次执行时会自动加载新配置
4. **中断操作**：执行过程中可按 Ctrl+C 安全返回菜单，不会丢失已成交订单

## 故障排除

### 常见问题

#### 1. 页面打开失败

**问题**：显示"页面打开失败"或超时

**解决方案**：
- 检查 MoreLogin 服务是否运行在 `localhost:40000`
- 确认环境 ID 是否正确
- 检查网络连接
- 程序已自动增加超时时间到120秒

#### 2. 价格获取失败

**问题**：显示"未能通过API获取价格"

**解决方案**：
- 检查网络连接
- 确认交易对符号正确（大写，如 BTC、ETH）
- 检查 Nado API 是否可访问
- 程序会自动重试10次

#### 3. 订单未成交

**问题**：订单一直未成交

**解决方案**：
- 调整价格偏移量，使其更接近市价
- 检查订单大小是否合理
- 程序会自动重试（最多999次），每次都会重新获取价格

#### 4. Ctrl+C 无法中断

**问题**：按 Ctrl+C 后程序没有响应

**解决方案**：
- 程序已优化，所有等待操作都可以响应 Ctrl+C
- 如果仍然卡住，可能需要强制退出（Ctrl+Z 或关闭终端）

## 文件说明

- `nado_var.py`: 主程序文件
- `config_*.csv`: 配置文件（可创建多个，如 config_btc.csv, config_aave.csv）
- `product_id_cache.json`: product_id 缓存文件（自动生成）

## 技术栈

- **Python 3.9+**: 编程语言
- **Playwright**: 浏览器自动化框架
- **Requests**: HTTP 请求库
- **MoreLogin API**: 浏览器环境管理

## 更新日志

### 最新功能

- ✅ 支持命令行参数指定配置文件
- ✅ 配置文件修改后无需重启程序
- ✅ 执行过程中可按 Ctrl+C 安全返回菜单
- ✅ 优化了所有等待操作，确保能够响应中断
- ✅ 每次重新下单都会重新获取最新价格
- ✅ 详细的日志输出，方便监控执行过程


**免责声明**：本工具仅供学习和研究使用，使用者需自行承担交易风险。作者不对使用本工具造成的任何损失负责。
