[uv常用命令与注意事项](https://chatgpt.com/c/6aaa5c61-8a74-83ee-a871-3e754fa47504)

可以。按 **uv 目前官方文档**来看，我会把它分成两套思路：

- **日常项目开发：优先用 `uv init / add / remove / sync / run / lock`**
- **临时环境、兼容传统 pip 工作流、特殊安装操作：用 `uv pip ...`**

也就是说，别把 `uv` 简单理解成“快很多的 pip”。它真正舒服的地方是把 **Python 版本 + `.venv` + `pyproject.toml` + `uv.lock` + 工具管理**揉成了一套。Python 包管理这些年终于快从考古学进化成工程学了。([Astral Docs](https://docs.astral.sh/uv/getting-started/features/?utm_source=chatgpt.com))

# uv 常用命令速查

## 1. uv 自身

如果使用 Astral 官方安装器安装：

```bash
uv self update
```

查看版本：

```bash
uv --version
```

清缓存：

```bash
uv cache clean
```

只清某个包：

```bash
uv cache clean torch
```

清理无用缓存：

```bash
uv cache prune
```

如果遇到“明明服务器上的 wheel 更新了，但 uv 还是拿旧东西”这类缓存玄学：

```bash
uv sync --refresh
```

或者：

```bash
uv sync --refresh-package torch
```

官方建议一般周期性使用 `uv cache prune` 即可，不必没事把整个缓存扬了。([Astral Docs](https://docs.astral.sh/uv/getting-started/installation/?utm_source=chatgpt.com))

------

# 2. Python 版本管理

查看可用 Python：

```bash
uv python list
```

只看已经安装的：

```bash
uv python list --only-installed
```

安装 Python：

```bash
uv python install 3.12
```

安装指定 patch：

```bash
uv python install 3.12.11
```

同时安装多个：

```bash
uv python install 3.10 3.11 3.12
```

给当前项目固定 Python：

```bash
uv python pin 3.12
```

会生成：

```text
.python-version
```

升级 uv 管理的 Python 3.12 到最新 patch：

```bash
uv python upgrade 3.12
```

升级所有 uv 管理的 CPython：

```bash
uv python upgrade
```

注意，`uv` 如果发现项目需要的 Python 不存在，**默认可以自动下载**对应 Python。所以很多情况下甚至不需要先 `uv python install`。([Astral Docs](https://docs.astral.sh/uv/concepts/python-versions/?utm_source=chatgpt.com))

------

# 3. 创建项目

最简单：

```bash
uv init
```

指定 Python：

```bash
uv init --python 3.12
```

典型项目随后会有：

```text
project/
├── .python-version
├── pyproject.toml
├── uv.lock
└── .venv/
```

其中：

- `pyproject.toml`：你**声明想要什么**
- `uv.lock`：uv **实际解析到了什么版本**
- `.venv`：实际运行环境

这三个概念非常重要。

------

# 4. 创建虚拟环境

通常项目模式下你甚至不用手动创建，`uv sync` 会自动建立 `.venv`。

需要手动创建时：

```bash
uv venv
```

指定 Python：

```bash
uv venv --python 3.12
```

指定目录：

```bash
uv venv .venv
```

激活方式仍然和传统 venv 一样。

Linux：

```bash
source .venv/bin/activate
```

PowerShell：

```powershell
.venv\Scripts\Activate.ps1
```

但使用 uv 项目时，我建议**不用养成必须 activate 的习惯**：

```bash
uv run python main.py
uv run pytest
uv run ruff check .
```

这样环境是谁、Python 是谁、依赖是谁，都由 uv 决定，少一点 shell 状态魔法。([Astral Docs](https://docs.astral.sh/uv/pip/environments/?utm_source=chatgpt.com))

------

# 5. 安装普通依赖

安装：

```bash
uv add requests
```

安装多个：

```bash
uv add numpy pandas scipy
```

指定版本：

```bash
uv add "numpy==2.3.3"
```

指定范围：

```bash
uv add "numpy>=2.0,<3"
```

`uv add` 会同时修改：

```text
pyproject.toml
uv.lock
.venv
```

所以通常**不要**这样：

```bash
uv pip install requests
```

如果这是一个正式 uv 项目，更推荐：

```bash
uv add requests
```

因为 `uv pip install` 只操作环境，不会帮你维护项目声明。([Astral Docs](https://docs.astral.sh/uv/concepts/projects/dependencies/?utm_source=chatgpt.com))

------

# 6. 删除依赖

```bash
uv remove requests
```

删除后同样会更新：

```text
pyproject.toml
uv.lock
.venv
```

([Astral Docs](https://docs.astral.sh/uv/concepts/projects/dependencies/?utm_source=chatgpt.com))

------

# 7. 开发依赖

比如你的 Python 项目规范中经常用的：

```bash
uv add --dev pytest ruff ty
```

会放进：

```toml
[dependency-groups]
dev = [
    "pytest",
    "ruff",
    "ty",
]
```

现在 uv 推荐的是标准化的 **dependency groups**，而不是以前的 `tool.uv.dev-dependencies`。([Astral Docs](https://docs.astral.sh/uv/concepts/projects/dependencies/?utm_source=chatgpt.com))

还可以划分：

```bash
uv add --group test pytest
uv add --group lint ruff
uv add --group type ty
```

例如：

```toml
[dependency-groups]
test = ["pytest"]
lint = ["ruff"]
type = ["ty"]
```

执行某个 group：

```bash
uv sync --group test
```

所有 group：

```bash
uv sync --all-groups
```

`dev` 比较特殊，**默认会参与同步**。([Astral Docs](https://docs.astral.sh/uv/concepts/projects/dependencies/?utm_source=chatgpt.com))

------

# 8. 更新某一个包

这是非常值得记住的一组。

例如：

```bash
uv lock --upgrade-package numpy
```

缩写：

```bash
uv lock -P numpy
```

它的含义是：

> 把 numpy 更新到 **当前 `pyproject.toml` 约束范围内的最新兼容版本**，其他依赖尽量保持不动。

然后同步环境：

```bash
uv sync
```

例如：

```toml
dependencies = [
    "numpy>=2.0,<3",
]
```

运行：

```bash
uv lock --upgrade-package numpy
uv sync
```

可能：

```text
2.2.6 → 2.3.3
```

但不会跳到 `3.x`。

官方项目指南明确推荐这种方式更新单个依赖。([Astral Docs](https://docs.astral.sh/uv/guides/projects/?utm_source=chatgpt.com))

------

# 9. 修改版本约束并升级

例如原来：

```toml
httpx>=0.27
```

现在想改要求：

```bash
uv add "httpx>=0.28"
```

注意一个容易踩的坑：

**修改依赖约束并不意味着一定主动升级到最新版本。**

如果你希望：

> 修改约束 + 马上升级到最新兼容版本

使用：

```bash
uv add "httpx>=0.28" --upgrade-package httpx
```

这是官方文档特别提醒的行为。([Astral Docs](https://docs.astral.sh/uv/concepts/projects/dependencies/?utm_source=chatgpt.com))

------

# 10. 更新全部依赖

```bash
uv lock --upgrade
```

然后：

```bash
uv sync
```

这相当于：

> 在 `pyproject.toml` 约束允许的范围内重新寻找最新版本。

所以正常维护项目时，我更推荐：

```bash
uv lock --upgrade
uv sync
uv run pytest
```

而不是删除 `uv.lock` 重新生成。

**不要为了升级就删 lock 文件。**

lock 文件的存在就是为了让升级是一个明确的、有控制的动作。

------

# 11. 同步环境

最普通：

```bash
uv sync
```

它让：

```text
.venv ← uv.lock
```

默认是 **exact sync**，所以 `.venv` 里那些不属于项目的包可能被删除。([Astral Docs](https://docs.astral.sh/uv/reference/cli/?utm_source=chatgpt.com))

如果想保留额外包：

```bash
uv sync --inexact
```

CI 中很有用：

```bash
uv sync --locked
```

它表示：

> `pyproject.toml` 与 `uv.lock` 不一致就报错，不偷偷更新 lock。

更严格地完全相信已有 lock：

```bash
uv sync --frozen
```

大概可以理解：

```text
正常开发：
uv sync

CI：
uv sync --locked

完全不解析、不检查：
uv sync --frozen
```

([Astral Docs](https://docs.astral.sh/uv/concepts/projects/sync/?utm_source=chatgpt.com))

------

# 12. 运行程序

Python：

```bash
uv run python main.py
```

pytest：

```bash
uv run pytest
```

ruff：

```bash
uv run ruff check .
uv run ruff format .
```

ty：

```bash
uv run ty check
```

一个很舒服的特性是：

```bash
uv run ...
```

执行前会自动检查：

```text
pyproject.toml
       ↓
    uv.lock
       ↓
     .venv
```

必要时自动 lock + sync。([Astral Docs](https://docs.astral.sh/uv/guides/projects/?utm_source=chatgpt.com))

所以正常情况下：

```bash
uv add pytest
uv run pytest
```

就够了。

------

# 13. 临时使用某个依赖

例如我只想临时执行 Python，并使用 `rich`：

```bash
uv run --with rich python script.py
```

不会把 `rich` 正式加进项目。

这很适合：

```bash
uv run --with ipython ipython
```

或者临时测试某个库。

------

# 14. 查看依赖树

```bash
uv tree
```

非常适合查：

```text
为什么装了这个包？
谁依赖它？
为什么版本升不上去？
```

例如：

```bash
uv tree | less
```

或者直接搜索：

```bash
uv tree | grep torch
```

`uv tree` 同样会自动检查 lock 是否最新。([Astral Docs](https://docs.astral.sh/uv/concepts/projects/sync/?utm_source=chatgpt.com))

------

# 15. requirements.txt 迁移

老项目：

```text
requirements.txt
```

可以直接：

```bash
uv add -r requirements.txt
```

例如：

```bash
uv init
uv add -r requirements.txt
```

然后以后改用：

```text
pyproject.toml
uv.lock
```

([Astral Docs](https://docs.astral.sh/uv/concepts/projects/dependencies/?utm_source=chatgpt.com))

------

# 16. 导出 requirements.txt

如果某些部署环境还活在 pip 世界：

```bash
uv export --format requirements.txt --output-file requirements.txt
```

也可以导出 PEP 751：

```bash
uv export --format pylock.toml --output-file pylock.toml
```

甚至 SBOM：

```bash
uv export --format cyclonedx1.5 --output-file sbom.json
```

官方明确提醒，一般**不推荐同时把 `uv.lock` 和 `requirements.txt` 当两套锁文件维护**。如果必须兼容 pip，就让 `requirements.txt` 从 `uv.lock` 导出。([Astral Docs](https://docs.astral.sh/uv/reference/cli/?utm_source=chatgpt.com))

------

# 17. 安装 PyTorch：这里要特别注意

PyTorch 是 Python 包管理界著名的“不按正常规则出牌选手”，原因主要有：

- CPU / CUDA / ROCm / XPU 有不同 wheel
- 很多 wheel 不在标准 PyPI
- 不同 CUDA variant 在不同 index
- CUDA/PyTorch/Python/平台之间存在兼容组合

uv 官方因此单独写了一整页 PyTorch 指南。([Astral Docs](https://docs.astral.sh/uv/guides/integration/pytorch/?utm_source=chatgpt.com))

## 最简单

```bash
uv add torch torchvision
```

但这意味着：

> 使用默认 PyPI 上的 PyTorch 包。

当前 PyTorch 的 PyPI 行为还会因 Windows/Linux/macOS 不同，因此 **GPU 项目我不建议仅靠这一条命令然后祈祷显卡之神降临**。([Astral Docs](https://docs.astral.sh/uv/guides/integration/pytorch/?utm_source=chatgpt.com))

------

# 18. 指定 CUDA PyTorch

例如 CUDA 13.0：

```bash
uv add torch torchvision \
    --index pytorch=https://download.pytorch.org/whl/cu130
```

uv 会生成类似：

```toml
[project]
dependencies = [
    "torch",
    "torchvision",
]

[tool.uv.sources]
torch = { index = "pytorch" }
torchvision = { index = "pytorch" }

[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cu130"
```

([Astral Docs](https://docs.astral.sh/uv/concepts/projects/dependencies/?utm_source=chatgpt.com))

对于正式项目，官方还推荐：

```toml
[[tool.uv.index]]
name = "pytorch-cu130"
url = "https://download.pytorch.org/whl/cu130"
explicit = true
```

再指定：

```toml
[tool.uv.sources]
torch = { index = "pytorch-cu130" }
torchvision = { index = "pytorch-cu130" }
```

这里：

```toml
explicit = true
```

很重要。

它相当于告诉 uv：

> **只有我明确指定的 PyTorch 包才能从这个源下载。**

否则理论上某些普通依赖也可能从 PyTorch index 解析，人类辛辛苦苦防供应链攻击，总不能自己主动把依赖解析搞得更混乱。([Astral Docs](https://docs.astral.sh/uv/guides/integration/pytorch/?utm_source=chatgpt.com))

------

# 19. PyTorch 自动检测 CUDA

uv 现在还有一个很好玩的功能：

```bash
uv pip install torch torchvision --torch-backend=auto
```

它会检测：

- NVIDIA CUDA driver
- AMD GPU
- Intel GPU

自动选择适合的 PyTorch index。

也可以指定：

```bash
uv pip install torch torchvision --torch-backend=cu130
```

例如目前 CLI 支持：

```text
cpu
cu118
cu126
cu128
cu129
cu130
cu132
rocm...
xpu
auto
```

但有两个重要注意事项：

> **`--torch-backend` 目前仍属于 preview 功能。**

而且目前：

> **仅支持 `uv pip` interface。**

因此我会把它当成**临时装环境 / 实验很好用**的功能，而正式项目仍然更倾向于把 index 明确写进 `pyproject.toml`。([Astral Docs](https://docs.astral.sh/uv/reference/cli/?utm_source=chatgpt.com))

------

# 20. PyTorch 扩展包，例如 flash-attn

这类东西更麻烦，因为通常绑定：

```text
Python
× CUDA
× PyTorch
× 平台
```

uv/Astral 现在提供了一些 GPU wheel index。

例如官方文档给出的 CUDA 12.8：

```bash
uv add flash-attn \
    --index astral-cu128=https://wheels.astral.sh/simple/cu128/
```

会产生：

```toml
[tool.uv.sources]
flash-attn = { index = "astral-cu128" }

[[tool.uv.index]]
name = "astral-cu128"
url = "https://wheels.astral.sh/simple/cu128/"
explicit = true
```

官方当前提到预编译 wheel 涉及：

```text
flash-attn
deepspeed
deep-gemm
torch-scatter
vllm
```

等项目。([Astral Docs](https://docs.astral.sh/uv/guides/integration/pytorch/?utm_source=chatgpt.com))

这对你这种经常折腾 vLLM / CUDA / PyTorch 环境的人尤其有价值，因为能避免：

```text
pip install flash-attn
↓
开始编译
↓
CUDA 不对
↓
torch ABI 不对
↓
ninja 开始烤 CPU
↓
半小时以后报错
```

这种 Python AI 环境的传统宗教仪式。

------

# 21. `uv pip` 模式

如果你只是想把 uv 当超级快的 pip：

```bash
uv venv
uv pip install numpy
```

升级：

```bash
uv pip install --upgrade numpy
```

卸载：

```bash
uv pip uninstall numpy
```

列出：

```bash
uv pip list
```

查看：

```bash
uv pip show torch
```

安装 requirements：

```bash
uv pip install -r requirements.txt
```

同步：

```bash
uv pip sync requirements.txt
```

但要记住：

```text
uv add
```

和：

```text
uv pip install
```

**不是同一个层级。**

官方的描述非常明确：`uv pip` 是直接管理环境的低层接口，而项目 interface 则由 uv 自动管理虚拟环境、依赖和 lockfile。([Astral Docs](https://docs.astral.sh/uv/pip/?utm_source=chatgpt.com))

因此：

| 场景                   | 推荐                     |
| ---------------------- | ------------------------ |
| 正式项目依赖           | `uv add`                 |
| 删除项目依赖           | `uv remove`              |
| 项目升级               | `uv lock --upgrade...`   |
| 根据项目运行           | `uv run`                 |
| 临时 venv              | `uv pip`                 |
| 老项目 requirements    | `uv pip`                 |
| 手工测试 PyTorch wheel | `uv pip`                 |
| 自动 CUDA backend      | `uv pip --torch-backend` |

------

# 22. CLI 工具不要装进项目

比如 `ruff` 如果只是个人全局工具：

```bash
uv tool install ruff
```

查看：

```bash
uv tool list
```

升级：

```bash
uv tool upgrade ruff
```

升级所有：

```bash
uv tool upgrade --all
```

删除：

```bash
uv tool uninstall ruff
```

([Astral Docs](https://docs.astral.sh/uv/concepts/tools/?utm_source=chatgpt.com))

不过如果：

```text
这个项目明确依赖 ruff 0.x
```

还是：

```bash
uv add --dev ruff
```

更可复现。

------

# 23. `uvx`：一次性运行工具

例如：

```bash
uvx ruff check .
```

等价于：

```bash
uv tool run ruff check .
```

无需事先安装。

比如：

```bash
uvx black .
```

特别适合偶尔使用的小工具。([Astral Docs](https://docs.astral.sh/uv/getting-started/features/?utm_source=chatgpt.com))

------

# 我最推荐你记住的工作流

对于你平时新建 Python AI / CV 项目，可以基本固定成：

```bash
# 创建
uv init --python 3.12

# 普通依赖
uv add numpy opencv-python pillow

# 开发依赖
uv add --dev pytest ruff ty

# 运行
uv run python main.py

# lint
uv run ruff check .

# format
uv run ruff format .

# type check
uv run ty check

# test
uv run pytest
```

更新单个包：

```bash
uv lock --upgrade-package numpy
uv sync
uv run pytest
```

整体升级：

```bash
uv lock --upgrade
uv sync
uv run pytest
```

如果更新版本要求：

```bash
uv add "numpy>=2.3" --upgrade-package numpy
```

PyTorch GPU 项目则额外明确指定源，例如：

```bash
uv add torch torchvision \
    --index pytorch=https://download.pytorch.org/whl/cu130
```

然后把这个 index 配置保存在 `pyproject.toml`，正式项目尽量不要靠一次性的 shell 参数维持环境。

------

## 几个最容易搞混的点

**`uv add` ≠ `uv pip install`。** 前者修改项目，后者主要修改环境。正式项目优先 `uv add`。

**`uv lock --upgrade-package foo` 不会突破 `pyproject.toml` 的版本约束。** 如果约束本身需要变，用：

```bash
uv add "foo>=新版本" --upgrade-package foo
```

**`uv lock` 主要修改 lock，不负责把 `.venv` 完全同步过去。** 升级后执行：

```bash
uv sync
```

或者下一次：

```bash
uv run ...
```

让 uv 自动同步。([Astral Docs](https://docs.astral.sh/uv/concepts/projects/sync/?utm_source=chatgpt.com))

**`uv sync` 默认是 exact sync。** 手动往 `.venv` 塞的奇怪东西可能被它清掉。这其实是好事，只是第一次看到时容易以为 uv 对你的包发动了清洗。

**PyTorch 不要把普通 PyPI 包思维直接套过去。** CUDA/ROCm wheel 应明确考虑 index、Python、PyTorch 和 CUDA 组合。([Astral Docs](https://docs.astral.sh/uv/guides/integration/pytorch/?utm_source=chatgpt.com))

**推荐提交到 Git 的是：**

```text
pyproject.toml
uv.lock
.python-version
```

而不是：

```text
.venv/
```

------

### 一张真正够日常使用的速查表

```bash
# ===== 项目 =====
uv init --python 3.12
uv sync
uv run python main.py

# ===== Python =====
uv python list
uv python install 3.12
uv python pin 3.12
uv python upgrade 3.12

# ===== 依赖 =====
uv add requests
uv add "numpy>=2,<3"
uv add --dev pytest
uv add --group lint ruff
uv remove requests

# ===== 更新 =====
uv lock --upgrade-package numpy
uv lock --upgrade
uv sync

# 修改约束并更新
uv add "numpy>=2.3" --upgrade-package numpy

# ===== 查看 =====
uv tree

# ===== requirements =====
uv add -r requirements.txt
uv export --format requirements.txt --output-file requirements.txt

# ===== PyTorch =====
uv add torch torchvision \
  --index pytorch=https://download.pytorch.org/whl/cu130

# 临时/低层 PyTorch 安装
uv pip install torch torchvision --torch-backend=auto
uv pip install torch torchvision --torch-backend=cu130

# ===== 工具 =====
uvx ruff check .
uv tool install ruff
uv tool upgrade ruff
uv tool upgrade --all

# ===== 缓存 =====
uv cache prune
uv cache clean torch
uv sync --refresh-package torch

# ===== uv =====
uv self update
```

这套基本已经覆盖 **90% 以上正常 Python 开发，以及相当一部分 AI/CUDA 环境管理**。对于你的项目规范，我也会更倾向于把以前那句“使用 `uv` 管理 Python、虚拟环境和依赖”进一步明确成：**默认使用 uv Project Interface，只有临时环境、遗留 pip 工作流或 PyTorch 特殊安装场景才使用 `uv pip`**。这样 agent 不容易一看到安装包就条件反射地 `uv pip install`，然后偷偷绕开 `pyproject.toml` 和 `uv.lock`。([Astral Docs](https://docs.astral.sh/uv/pip/?utm_source=chatgpt.com))

