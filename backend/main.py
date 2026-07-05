import os, json, asyncio, hashlib
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from diskcache import Cache as DiskCache

from config import settings
from models import ReadmeRequest, ReadmeResponse
from llm import query_ollama

app = FastAPI(title="AI README Generator")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
disk_cache = DiskCache(settings.cache_dir)

STACK_RULES = {
    "package.json": lambda d: "Node.js" if not d.get("devDependencies") else "Node.js",
    "requirements.txt": "Python",
    "Cargo.toml": "Rust",
    "go.mod": "Go",
    "pom.xml": "Java (Maven)",
    "Gemfile": "Ruby",
    "composer.json": "PHP",
    "Dockerfile": "Docker",
}

def build_tree(path: str, prefix="") -> str:
    lines = []
    try:
        entries = sorted(os.listdir(path))
    except PermissionError:
        return ""
    for i, entry in enumerate(entries):
        if entry.startswith(".") or entry in ("node_modules", "__pycache__", ".venv", "venv", ".git"):
            continue
        full = os.path.join(path, entry)
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{entry}{'/' if os.path.isdir(full) else ''}")
        if os.path.isdir(full):
            ext = "    " if is_last else "│   "
            lines.append(build_tree(full, prefix + ext))
    return "\n".join(lines)

def detect_stack(path: str) -> list[str]:
    stacks = set()
    for root, dirs, files in os.walk(path):
        for f in files:
            if f == "package.json":
                stacks.add("Node.js")
            elif f == "requirements.txt":
                stacks.add("Python")
            elif f == "Cargo.toml":
                stacks.add("Rust")
            elif f == "Dockerfile":
                stacks.add("Docker")
    return list(stacks) if stacks else ["Unknown"]

async def get_entry_snippet(path: str) -> str:
    main_files = ["main.py", "app.py", "index.js", "index.ts", "main.js", "main.ts", "App.jsx", "App.tsx"]
    for root, dirs, files in os.walk(path):
        for f in files:
            if f in main_files:
                full = os.path.join(root, f)
                try:
                    with open(full) as fh:
                        content = fh.read(3000)
                    if f.endswith((".js", ".ts", ".jsx", ".tsx")):
                        # ponytail: esprima subprocess skipped; sends raw snippet to LLM instead
                        pass
                    # ponytail: ast.parse skipped; raw snippet is sufficient for LLM
                    return f"// {f}\n{content}"
                except Exception:
                    return ""
        if root.count(os.sep) - path.count(os.sep) > 2:
            break
    return ""

@app.post("/generate-readme", response_model=ReadmeResponse)
async def generate_readme(req: ReadmeRequest, background_tasks: BackgroundTasks):
    if not req.folder_path.startswith(settings.allowed_prefix):
        raise HTTPException(400, f"Path must start with {settings.allowed_prefix}")

    if not os.path.isdir(req.folder_path):
        raise HTTPException(400, "Folder path does not exist")

    tree = build_tree(req.folder_path)
    cache_key = hashlib.md5(tree.encode()).hexdigest()

    cached = disk_cache.get(cache_key)
    if cached:
        return cached

    tech_stack = detect_stack(req.folder_path)
    entry = await get_entry_snippet(req.folder_path)

    result = await query_ollama(tree, ", ".join(tech_stack), entry)
    disk_cache.set(cache_key, result, expire=604800)
    return result

@app.get("/health")
async def health():
    return {"status": "ok"}
