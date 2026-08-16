import glob, os, sys, time

DIR = os.path.dirname(os.path.abspath(__file__))
KEEP_DAYS = float(os.environ.get("LOG_KEEP_DAYS", "7"))
MAX_BYTES = int(os.environ.get("LOG_MAX_BYTES", str(50 * 1024 * 1024)))

def main():
    now = time.time()
    cleaned = 0
    for pat in ("*.stderr", "*.log", "*.log.*", "*.old"):
        for f in glob.glob(os.path.join(DIR, pat)):
            try:
                size = os.path.getsize(f)
                age = now - os.path.getmtime(f)
                if age > KEEP_DAYS * 86400 or (pat.endswith(".old") and size > MAX_BYTES):
                    os.remove(f)
                    cleaned += 1
                    print(f"removed {os.path.basename(f)}")
            except OSError:
                pass
    print(f"log_cleanup done: removed {cleaned} files")
    return 0

if __name__ == "__main__":
    sys.exit(main())
