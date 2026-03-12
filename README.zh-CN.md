# cocoindex-code

[English](README.md) | [中文](README.zh-CN.md)

基于 [CocoIndex](https://github.com/cocoindex-io/cocoindex) 的轻量代码语义检索 MCP 服务。这个 fork 只保留远程 API embedding 路径，并依赖 `CoderDoubleflower/litellm` 的补丁版本。

## 安装

使用 `uv` 安装或更新：

```bash
uv tool install --force "git+https://github.com/CoderDoubleflower/cocoindex-code.git@main"
```

使用 `pipx` 安装或更新：

```bash
pipx install --force "git+https://github.com/CoderDoubleflower/cocoindex-code.git@main"
```

从本地源码安装：

```bash
pipx install --force /path/to/cocoindex-code
```

## 用法

索引当前仓库：

```bash
COCOINDEX_CODE_ROOT_PATH="$(pwd)" cocoindex-code index
```

只索引 C/C++ 文件，并使用远程 embedding 服务：

```bash
COCOINDEX_CODE_ROOT_PATH="$(pwd)" \
COCOINDEX_CODE_INCLUDE_PATTERNS="**/*.cpp,**/*.h,**/*.c" \
COCOINDEX_CODE_EMBEDDING_MODEL="openai/Qwen3-VL-Embedding-8B" \
COCOINDEX_CODE_API_BASE="https://your-openai-compatible-endpoint/v1" \
COCOINDEX_CODE_ENCODING_FORMAT="float" \
OPENAI_API_KEY="your-api-key" \
cocoindex-code index
```

把 MCP 服务加到 Claude Code：

```bash
claude mcp add cocoindex-code \
  --scope user \
  --transport stdio \
  -e COCOINDEX_CODE_EMBEDDING_MODEL=openai/Qwen3-VL-Embedding-8B \
  -e COCOINDEX_CODE_API_BASE=https://your-openai-compatible-endpoint/v1 \
  -e COCOINDEX_CODE_ENCODING_FORMAT=float \
  -e OPENAI_API_KEY=your-api-key \
  -- cocoindex-code
```

把 MCP 服务加到 Codex：

```bash
codex mcp add cocoindex-code \
  -e COCOINDEX_CODE_EMBEDDING_MODEL=openai/Qwen3-VL-Embedding-8B \
  -e COCOINDEX_CODE_API_BASE=https://your-openai-compatible-endpoint/v1 \
  -e COCOINDEX_CODE_ENCODING_FORMAT=float \
  -e OPENAI_API_KEY=your-api-key \
  -- cocoindex-code
```

## 参数说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `COCOINDEX_CODE_ROOT_PATH` | 代码根目录。未设置时，会从当前目录向上查找 `.cocoindex_code`、`.git` 或其他项目标记。 | 自动发现 |
| `COCOINDEX_CODE_EMBEDDING_MODEL` | LiteLLM 模型 id，使用 `provider/model` 形式，例如 `openai/text-embedding-3-small` 或 `openrouter/qwen/qwen3-embedding-8b`。 | `text-embedding-3-small` |
| `COCOINDEX_CODE_API_BASE` | 可选，自定义 API Base URL，会作为 `api_base` 传给 LiteLLM。适合 OpenAI-compatible 网关或自建 endpoint。 | provider 默认值 |
| `COCOINDEX_CODE_ENCODING_FORMAT` | embedding 返回格式。这个项目最推荐 `float`。支持：`float`、`base64`、`bytes`、`bytes_only`。 | `float` |
| `COCOINDEX_CODE_INCLUDE_PATTERNS` | 逗号分隔的 glob 模式。设置后会直接覆盖内置文件类型列表。 | 内置语言列表 |
| `COCOINDEX_CODE_EXTRA_EXTENSIONS` | 在内置文件类型基础上额外添加的扩展名。格式：`ext` 或 `ext:language`。 | 无 |

Provider 的鉴权和专用 endpoint 变量仍然沿用 LiteLLM 约定，比如 `OPENAI_API_KEY`、`OPENROUTER_API_KEY`、`VOYAGE_API_KEY`、`AZURE_API_KEY`、`AZURE_API_BASE`、`OLLAMA_API_BASE`。

## MCP 工具

### `search`

对代码库做语义检索。

```text
search(
    query: str,
    limit: int = 10,
    offset: int = 0,
    refresh_index: bool = True
)
```

`refresh_index=True` 时，查询前会先做一次增量更新。

返回内容包括：

- 文件路径
- 语言
- 代码内容
- 起止行号
- 相似度分数

## 支持语言

默认支持 Python、JavaScript/TypeScript、Rust、Go、Java、C/C++、C#、SQL、Shell，以及常见文本文档格式。

## 故障排查

### `sqlite3.Connection object has no attribute enable_load_extension`

某些 Python 发行版的 SQLite 没开启扩展支持。macOS 上通常建议改用 Homebrew 安装的 Python，再重新安装这个 fork：

```bash
uv tool install --force "git+https://github.com/CoderDoubleflower/cocoindex-code.git@main"
```
