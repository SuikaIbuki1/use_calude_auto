# AI Auto Operator

<div align="center">

**智能化鼠标键盘自动化操作系统**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](#english) | [中文文档](#中文文档)

</div>

---

<a name="中文文档"></a>

## 📖 项目简介

AI Auto Operator 是一个基于 Python 的智能自动化操作系统,结合 AI 视觉识别和决策能力,实现复杂的桌面操作自动化。

### ✨ 核心特性

- 🖱️ **鼠标控制**: 移动、点击、拖拽、滚动等完整操作支持
- ⌨️ **键盘控制**: 文本输入、快捷键、组合键等
- 👁️ **屏幕识别**: 图像匹配、OCR 文字识别
- 🤖 **AI 决策**: 基于 GPT-4/Claude 的智能决策引擎
- 📋 **任务编排**: 支持 YAML/JSON 定义任务流程
- 🔧 **灵活配置**: 三种执行模式适配不同场景

### 🎯 执行模式

1. **预定义模式 (Predefined)**: 按照预定义的步骤序列执行
2. **AI 辅助模式 (AI-Assisted)**: AI 实时分析屏幕并决策
3. **混合模式 (Hybrid)**: 结合预定义步骤和 AI 决策

---

## 🚀 快速开始

### 安装依赖

```bash
# 克隆项目
git clone https://github.com/yourusername/ai-auto-operator.git
cd ai-auto-operator

# 安装依赖
pip install -r requirements.txt

# 安装 Tesseract OCR (可选)
# Windows: 下载安装包 https://github.com/tesseract-ocr/tesseract
# Ubuntu: sudo apt-get install tesseract-ocr
# Mac: brew install tesseract
```

### 配置 API 密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件,填入你的 API 密钥
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here
```

### 基础使用

```bash
# 进入 src 目录
cd src

# 测试控制器
python main.py test

# 截屏
python main.py screen

# 执行预定义任务
python main.py run ../config/task_templates/example_predefined.yaml

# AI 辅助执行
python main.py ask "打开浏览器并搜索 Python 教程"

# 查找图像
python main.py find path/to/image.png
```

---

## 📚 使用指南

### 1. 预定义任务

创建 YAML 任务文件:

```yaml
name: "打开记事本并输入文本"
description: "自动化文本输入示例"
mode: "predefined"

steps:
  - action: hotkey
    keys: ["win", "r"]
    description: "打开运行对话框"
    delay: 1.0
  
  - action: type_text
    text: "notepad"
    description: "输入 notepad"
  
  - action: press_key
    key: "enter"
    description: "确认打开"
    delay: 2.0
  
  - action: type_text
    text: "Hello from AI Auto Operator!"
    description: "输入文本"
```

执行任务:

```bash
python main.py run my_task.yaml
```

### 2. AI 辅助任务

使用自然语言描述任务:

```bash
python main.py ask "打开 Outlook 发送一封测试邮件"
```

AI 将:
1. 分析当前屏幕
2. 识别相关元素
3. 决策下一步操作
4. 自动执行直到完成

### 3. 图像识别

查找屏幕上的图像:

```bash
python main.py find button.png
```

系统会自动定位并将鼠标移动到匹配位置。

---

## 🛠️ 开发指南

### 项目结构

```
ai-auto-operator/
├── src/
│   ├── controllers/        # 鼠标键盘控制器
│   ├── recognizers/        # 屏幕识别模块
│   ├── ai_engine/          # AI 决策引擎
│   ├── task_engine/        # 任务执行引擎
│   ├── config/             # 配置管理
│   ├── utils/              # 工具函数
│   └── main.py             # 主程序入口
├── config/                 # 配置文件
│   ├── config.yaml         # 主配置
│   └── task_templates/     # 任务模板
├── tests/                  # 单元测试
├── requirements.txt        # 依赖列表
└── README.md
```

### API 使用示例

```python
from controllers import MouseController, KeyboardController
from recognizers import ScreenCapture, ImageMatcher
from ai_engine import AIClient, DecisionEngine
from task_engine import TaskExecutor

# 初始化控制器
mouse = MouseController()
keyboard = KeyboardController()

# 鼠标操作
mouse.click(100, 200)
mouse.move_to(500, 300, duration=0.5)

# 键盘操作
keyboard.type_text("Hello World", enter=True)
keyboard.hotkey("ctrl", "c")

# 屏幕识别
capture = ScreenCapture()
screen = capture.capture_full_screen()

matcher = ImageMatcher()
position = matcher.find_image_center(screen, template_image)

# AI 决策
ai_client = AIClient(provider="openai")
decision_engine = DecisionEngine(ai_client, capture)
executor = TaskExecutor(mouse, keyboard, decision_engine)

executor.execute_simple("打开浏览器搜索天气")
```

---

## ⚙️ 配置说明

### 主配置文件 (config.yaml)

```yaml
# 鼠标设置
mouse:
  safety_delay: 0.1      # 操作间隔
  move_duration: 0.5     # 移动速度
  fail_safe: true        # 紧急停止(移至角落)

# 键盘设置
keyboard:
  typing_speed: 0.05     # 打字速度

# AI 设置
ai:
  provider: "openai"     # openai 或 anthropic
  model: "gpt-4-vision-preview"
  temperature: 0.7
  confidence_threshold: 0.7

# 识别设置
recognition:
  confidence_threshold: 0.8
  ocr_backend: "tesseract"
  ocr_language: "chi_sim+eng"
```

---

## 🔒 安全特性

- **紧急停止**: 鼠标快速移动到屏幕角落即可中止操作
- **操作延迟**: 每步操作间加入安全延迟,避免误操作
- **重试机制**: 支持失败重试和错误处理
- **权限控制**: API 密钥通过环境变量管理

---

## 📋 支持的操作

### 鼠标操作

| 操作 | 描述 | 参数 |
|------|------|------|
| `click` | 单击 | x, y, button, clicks |
| `double_click` | 双击 | x, y |
| `right_click` | 右键 | x, y |
| `move_to` | 移动 | x, y, duration |
| `drag` | 拖拽 | start_x, start_y, end_x, end_y |
| `scroll` | 滚动 | amount |

### 键盘操作

| 操作 | 描述 | 参数 |
|------|------|------|
| `type_text` | 输入文本 | text, interval |
| `press_key` | 按键 | key, presses |
| `hotkey` | 组合键 | keys[] |
| `copy` | 复制 | - |
| `paste` | 粘贴 | - |

### 工具操作

| 操作 | 描述 | 参数 |
|------|------|------|
| `wait` | 等待 | duration |
| `screenshot` | 截屏 | save_path |

---

## 🧪 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 测试特定模块
pytest tests/test_controllers.py -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

---

## 🤝 贡献指南

欢迎贡献代码!请遵循以下步骤:

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🙏 致谢

- [pyautogui](https://github.com/asweigart/pyautogui) - 鼠标键盘自动化
- [OpenCV](https://opencv.org/) - 图像识别
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - 文字识别
- [OpenAI](https://openai.com/) / [Anthropic](https://www.anthropic.com/) - AI API

---

<div align="center">

**如果这个项目对你有帮助,请给一个 ⭐️ Star!**

Made with ❤️ by Your Name

</div>

---

<a name="english"></a>

## 📖 Introduction

AI Auto Operator is a Python-based intelligent automation system that combines AI visual recognition and decision-making capabilities to achieve complex desktop operation automation.

### ✨ Core Features

- 🖱️ **Mouse Control**: Complete operation support for moving, clicking, dragging, scrolling, etc.
- ⌨️ **Keyboard Control**: Text input, shortcuts, combination keys, etc.
- 👁️ **Screen Recognition**: Image matching, OCR text recognition
- 🤖 **AI Decision**: Intelligent decision engine based on GPT-4/Claude
- 📋 **Task Orchestration**: Support for YAML/JSON task flow definitions
- 🔧 **Flexible Configuration**: Three execution modes for different scenarios

For detailed documentation, please refer to the Chinese documentation above.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.