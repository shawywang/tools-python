---
name: tongxunlu-shengri
description: 管理通讯录联系人工具，从 TXT 文件解析联系人信息，生成 Google Contacts CSV 导入文件和生日/纪念日 ICS 日历文件。支持从生辰.json 自动追加生卒、八字、身份证等备注信息。使用当用户需要生成通讯录CSV、导入联系人、生成生日日历文件、或管理联系人备注信息时。
---

# 通讯录、生日 — 联系人管理工具

## Overview

一个 Python 工具，将自定义格式的 `联系人.txt` 解析为 Google Contacts 兼容的 CSV 文件，同时生成生日/纪念日 ICS 日历文件。

数据源：`/Users/wangxiao/Nutstore Files/我的坚果云/我的文档/个人/联系人.txt`

## 输入格式（联系人.txt）

每行一个联系人，用中文分号 `；` 分隔各字段：

```
姓名；电话号码（逗号分隔多个）；邮箱（逗号分隔多个）；生日：农历日期；纪念日：农历日期；备注：备注内容
```

**示例：**
```
王骁；18482757919；wangxiao@example.com；生日：1998年冬月十七；备注：很久之前的电话号码是15982761423
王晶晶；15702669309,15364891243；生日：2005年六月初三；备注：好朋友张茜宁
```

### 农历日期格式

支持：
- `正月初五`（默认当年）
- `1990年四月廿三`
- `冬月十三`（冬月=11月，腊月=12月）
- 闰月：`1990年闰四月廿三`

月份映射：正=1, 二=2, ..., 十=10, 冬=11, 腊=12
日期映射：初一=1, 初二=2, ..., 三十=30

## 输出文件

| 文件 | 路径 | 用途 |
|------|------|------|
| CSV | `~/Downloads/contact.csv` | 导入 Google Contacts |
| ICS | `~/Downloads/schedule.ics` | 导入 Google Calendar（生日/纪念日提醒） |

## 生辰.json 自动追加

工具会读取 `/Users/wangxiao/Nutstore Files/我的坚果云/我的文档/个人/生辰.json`，如果联系人姓名匹配，则自动将 JSON 中的信息追加到备注。

### JSON 格式

```json
{
  "王骁": [
    {"生": "1998戊寅年冬月十七申时；1999年1月4，周一"},
    {"八字": "戊寅年，甲子月，丙辰日，丙申时，生于冬四川通江"},
    {"身份证": "51372119990212017X"},
    {"记": ""}
  ]
}
```

### 追加规则

- 只追加 value 非空的 key-value
- 用中文逗号 `，` 连接多个 key-value
- 原有备注与追加内容之间用中文句号 `。` 分隔
- 不引入中文分号 `；`（它是 TXT 字段分隔符）

**示例效果：**
```
很久之前的电话号码是15982761423。生：1998戊寅年冬月十七申时；1999年1月4，周一，八字：戊寅年，甲子月，丙辰日，丙申时，生于冬四川通江，身份证：51372119990212017X
```

## 输出 CSV 格式（Google Contacts）

生成的 CSV 包含 Google Contacts 标准表头，支持：
- **姓名**（名/姓/前缀/后缀）
- **电话**（最多 9 个，自动加 +86 前缀和空格格式化）
- **邮箱**（最多 5 个）
- **生日**（农历转公历）
- **纪念日**（Event 字段）
- **备注**（含生辰.json 追加信息）
- **地址**、**组织**、**关系**等

## 类结构

| 类 | 职责 |
|---|------|
| `GoogleCSV` | 单行 CSV 数据模型，包含所有 Google Contacts 字段 |
| `Person` | 从 TXT 解析出的联系人模型（name, nums, emails, birth, memorial, notes） |
| `Handle` | 核心处理类：解析 TXT → 生成 CSV（输出打印 + 写入文件） |
| `GoogleCalendar` | Google Calendar API 交互（OAuth 认证、创建/删除事件、导出 ICS） |
| `CulDate` | 农历日期计算：解析农历字符串、计算下次生日天数、生成提醒信息 |

## 运行方式

```bash
cd /Users/wangxiao/Documents/github/tools-python/tongxunlu-shengri
python3 "通讯录、生日.py"
```

### 输出流程

1. 读取 `联系人.txt`
2. 解析每行联系人信息
3. 加载 `生辰.json`，匹配联系人并追加备注
4. 打印 CSV 格式到终端（可复制到 Excel）
5. 写入 `~/Downloads/contact.csv`
6. 计算生日/纪念日倒计时并打印提醒
7. 生成 `~/Downloads/schedule.ics`

## 关键依赖

| 包 | 用途 |
|---|------|
| `lunardate` | 农历→公历转换 |
| `bazi_calculator` | 八字计算（用于 CulDate.get_bazi） |
| `google-api-python-client` | Google Calendar API |
| `google-auth-oauthlib` | OAuth 认证 |
| `ics` | ICS 文件生成 |
| `python-dotenv` | .env 加载（目前未使用） |

## 常见修改场景

### 添加新联系人
编辑 `联系人.txt`，按格式新增一行即可。

### 增补生辰信息
编辑 `生辰.json`，按格式添加联系人条目。

### 修改 CSV 输出列
编辑 `google_csv_title` 列表和 `Handle.show_csv()` / `write_csv()` 方法。

### 修改农历解析规则
编辑 `CulDate.parse_lunar_date()` 以及 `month_map` / `day_map` 字典。

## Common Pitfalls

1. **CSV 编码问题**：写入时必须用 `utf-8-sig`（带 BOM），否则 Excel 打开中文乱码。
2. **邮箱数量限制**：Google Contacts 导入限制最多 5 个邮箱，超过会报错退出。
3. **电话格式化**：非零号码自动加 +86 前缀，长度 ≤12 认为是大陆手机号。
4. **农历日期不合法**：如闰月不存在，程序会尝试普通月，失败则退出。
5. **生辰.json 不存在**：不报错，仅打印警告，正常生成 CSV。

## Verification Checklist

- [ ] TXT 文件中 `；` 是字段分隔符，备注内容不要用 `；`
- [ ] CSV 输出用 `；` 分列（Excel 导入时指定分列符）
- [ ] 农历生日必须正确匹配月份/日期映射
- [ ] 生辰.json 有同名联系人时，备注会追加生辰信息
- [ ] ICS 文件生成后可在 Google Calendar 导入验证
