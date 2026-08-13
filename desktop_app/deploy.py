# deploy.py - 通过 GitHub Contents API 增量上传（绕过 git:443）
import os, base64, json, urllib.request, urllib.error

ROOT = r"C:\Users\xinyu6290\WorkBuddy\2026-08-13-20-39-22"
REPO = "yanzien/app-hub"
TOKEN = os.environ["GITHUB_TOKEN"]
API = "https://api.github.com/repos/%s/contents/%%s" % REPO

EXCLUDE_DIRS = {".git", "build", "dist", ".trash", "node_modules", "__pycache__", ".workbuddy"}
EXCLUDE_FILES = {"upload_via_api.py", "build_exe.py"}

def collect():
    out = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in EXCLUDE_DIRS]
        rel = os.path.relpath(dp, ROOT)
        for fn in fns:
            full = os.path.join(dp, fn)
            r = os.path.normpath(os.path.join(rel, fn)) if rel != "." else fn
            if fn in EXCLUDE_FILES:
                continue
            # 跳过超大非必要（这里 exe 14MB 需要上传）
            out.append(r)
    return sorted(out)

def get_sha(path):
    url = API % path.replace("\\", "/")
    req = urllib.request.Request(url)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read()).get("sha")
    except Exception:
        return None

def upload(path):
    full = os.path.join(ROOT, path.replace("/", os.sep))
    with open(full, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    sha = get_sha(path)
    body = {"message": "update " + path, "content": b64, "branch": "main"}
    if sha:
        body["sha"] = sha
    body = json.dumps(body).encode()
    url = API % path.replace("\\", "/")
    req = urllib.request.Request(url, data=body, method="PUT")
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/vnd.github+json")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.getcode(), r.read().decode()[:60]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:160]

def main():
    files = collect()
    print("files:", len(files))
    ok = 0
    for i, p in enumerate(files, 1):
        size = os.path.getsize(os.path.join(ROOT, p.replace("/", os.sep)))
        code, resp = upload(p)
        st = "OK" if 200 <= code < 300 else "FAIL(%s)" % code
        print(f"[{i}/{len(files)}] {st} {p} ({size//1024}KB) {resp}")
        if 200 <= code < 300:
            ok += 1
    print(f"DONE: {ok}/{len(files)}")

if __name__ == "__main__":
    main()
