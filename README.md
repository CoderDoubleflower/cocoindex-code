<p align="center">
<img width="2428" alt="cocoindex code" src="https://github.com/user-attachments/assets/d05961b4-0b7b-42ea-834a-59c3c01717ca" />
</p>


<h1 align="center">light weight MCP for code that just works </h1>

![effect](https://github.com/user-attachments/assets/cb3a4cae-0e1f-49c4-890b-7bb93317ab60)




A super light-weight, effective embedded MCP **(AST-based)** that understand and searches your codebase that just works! Using [CocoIndex](https://github.com/cocoindex-io/cocoindex) - an Rust-based ultra performant data transformation engine. No blackbox. Works for Claude, Codex, Cursor - any coding agent.

- Instant token saving by 70%.
- **1 min setup** - Just claude/codex mcp add works!

<div align="center">

[![Discord](https://img.shields.io/discord/1314801574169673738?logo=discord&color=5B5BD6&logoColor=white)](https://discord.com/invite/zpA9S2DR7s)
[![GitHub](https://img.shields.io/github/stars/cocoindex-io/cocoindex?color=5B5BD6)](https://github.com/cocoindex-io/cocoindex)
[![Documentation](https://img.shields.io/badge/Documentation-394e79?logo=readthedocs&logoColor=00B9FF)](https://cocoindex.io/docs/getting_started/quickstart)
[![License](https://img.shields.io/badge/license-Apache%202.0-5B5BD6?logoColor=white)](https://opensource.org/licenses/Apache-2.0)
<!--[![PyPI - Downloads](https://img.shields.io/pypi/dm/cocoindex)](https://pypistats.org/packages/cocoindex) -->
[![PyPI Downloads](https://static.pepy.tech/badge/cocoindex/month)](https://pepy.tech/projects/cocoindex)
[![CI](https://github.com/cocoindex-io/cocoindex/actions/workflows/CI.yml/badge.svg?event=push&color=5B5BD6)](https://github.com/cocoindex-io/cocoindex/actions/workflows/CI.yml)
[![release](https://github.com/cocoindex-io/cocoindex/actions/workflows/release.yml/badge.svg?event=push&color=5B5BD6)](https://github.com/cocoindex-io/cocoindex/actions/workflows/release.yml)


🌟 Please help star [CocoIndex](https://github.com/cocoindex-io/cocoindex) if you like this project!

[English](README.md) | [中文](README.zh-CN.md)

</div>


## Install

This fork installs a patched `litellm` dependency from `CoderDoubleflower/litellm`.

Install or update with `uv`:

```bash
uv tool install --force "git+https://github.com/CoderDoubleflower/cocoindex-code.git@main"
```

Install or update with `pipx`:

```bash
pipx install --force "git+https://github.com/CoderDoubleflower/cocoindex-code.git@main"
```

Install from a local checkout:

```bash
pipx install --force /path/to/cocoindex-code
```

## Use

Index the current repository:

```bash
COCOINDEX_CODE_ROOT_PATH="$(pwd)" cocoindex-code index
```

Index only C/C++ files with a remote embedding model:

```bash
COCOINDEX_CODE_ROOT_PATH="$(pwd)" \
COCOINDEX_CODE_INCLUDE_PATTERNS="**/*.cpp,**/*.h,**/*.c" \
COCOINDEX_CODE_EMBEDDING_MODEL="openai/Qwen3-VL-Embedding-8B" \
COCOINDEX_CODE_API_BASE="https://your-openai-compatible-endpoint/v1" \
COCOINDEX_CODE_ENCODING_FORMAT="float" \
OPENAI_API_KEY="your-api-key" \
cocoindex-code index
```

Add the MCP server to Claude Code:

```bash
claude mcp add cocoindex-code \
  --scope user \
  --transport stdio \
  -e COCOINDEX_CODE_EMBEDDING_MODEL=openrouter/qwen/qwen3-embedding-8b \
  -e OPENROUTER_API_KEY=your-api-key \
  -- cocoindex-code
```

Add the MCP server to Codex:

```bash
codex mcp add cocoindex-code \
  -e COCOINDEX_CODE_EMBEDDING_MODEL=openrouter/qwen/qwen3-embedding-8b \
  -e OPENROUTER_API_KEY=your-api-key \
  -- cocoindex-code
```

## Parameters

| Variable | Description | Default |
|----------|-------------|---------|
| `COCOINDEX_CODE_ROOT_PATH` | Codebase root. If unset, the tool walks up from the current directory to find `.cocoindex_code`, `.git`, or another project marker. | Auto-discovered |
| `COCOINDEX_CODE_EMBEDDING_MODEL` | LiteLLM model id. Use `provider/model` form, for example `openai/text-embedding-3-small` or `openrouter/qwen/qwen3-embedding-8b`. | `text-embedding-3-small` |
| `COCOINDEX_CODE_API_BASE` | Optional custom API base URL passed to LiteLLM as `api_base`. Useful for OpenAI-compatible gateways and self-hosted endpoints. | Provider default |
| `COCOINDEX_CODE_ENCODING_FORMAT` | Embedding response encoding format passed to LiteLLM. `float` is the safest choice for this project. Supported values: `float`, `base64`, `bytes`, `bytes_only`. | `float` |
| `COCOINDEX_CODE_INCLUDE_PATTERNS` | Comma-separated glob patterns. When set, replaces the built-in file type list. | Built-in language list |
| `COCOINDEX_CODE_EXTRA_EXTENSIONS` | Extra file extensions to add on top of the built-in list. Format: `ext` or `ext:language`. | _(none)_ |

Provider credentials and provider-specific endpoint variables are still read from the environment variables expected by LiteLLM, for example `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `VOYAGE_API_KEY`, `AZURE_API_KEY`, `AZURE_API_BASE`, or `OLLAMA_API_BASE`.

## MCP Tools

### `search`

Search the codebase using semantic similarity.

```
search(
    query: str,               # Natural language query or code snippet
    limit: int = 10,          # Maximum results (1-100)
    offset: int = 0,          # Pagination offset
    refresh_index: bool = True  # Refresh index before querying
)
```

The `refresh_index` parameter controls whether the index is refreshed before searching:

- `True` (default): Refreshes the index to include any recent changes
- `False`: Skip refresh for faster consecutive queries

Returns matching code chunks with:

- File path
- Language
- Code content
- Line numbers (start/end)
- Similarity score


## Supported Languages

| Language | Aliases | File Extensions |
|----------|---------|-----------------|
| c | | `.c` |
| cpp | c++ | `.cpp`, `.cc`, `.cxx`, `.h`, `.hpp` |
| csharp | csharp, cs | `.cs` |
| css | | `.css`, `.scss` |
| dtd | | `.dtd` |
| fortran | f, f90, f95, f03 | `.f`, `.f90`, `.f95`, `.f03` |
| go | golang | `.go` |
| html | | `.html`, `.htm` |
| java | | `.java` |
| javascript | js | `.js` |
| json | | `.json` |
| kotlin | | `.kt`, `.kts` |
| markdown | md | `.md`, `.mdx` |
| pascal | pas, dpr, delphi | `.pas`, `.dpr` |
| php | | `.php` |
| python | | `.py` |
| r | | `.r` |
| ruby | | `.rb` |
| rust | rs | `.rs` |
| scala | | `.scala` |
| solidity | | `.sol` |
| sql | | `.sql` |
| swift | | `.swift` |
| toml | | `.toml` |
| tsx | | `.tsx` |
| typescript | ts | `.ts` |
| xml | | `.xml` |
| yaml | | `.yaml`, `.yml` |

Common generated directories are automatically excluded:

- `__pycache__/`
- `node_modules/`
- `target/`
- `dist/`
- `vendor/` (Go vendored dependencies, matched by domain-based child paths)

## Troubleshooting

### `sqlite3.Connection object has no attribute enable_load_extension`

Some Python installations (e.g. the one pre-installed on macOS) ship with a SQLite library that doesn't enable extensions.

**macOS fix:** Install Python through [Homebrew](https://brew.sh/):

```bash
brew install python3
```

Then reinstall this fork:

```bash
uv tool install --force "git+https://github.com/CoderDoubleflower/cocoindex-code.git@main"
```

## Large codebase / Enterprise
[CocoIndex](https://github.com/cocoindex-io/cocoindex) is an ultra effecient indexing engine that also works on large codebase at scale on XXX G for enterprises. In enterprise scenarios it is a lot more effecient to do index share with teammates when there are large repo or many repos. We also have advanced features like branch dedupe etc designed for enterprise users.

If you need help with remote setup, please email our maintainer linghua@cocoindex.io, happy to help!!

## License

Apache-2.0
