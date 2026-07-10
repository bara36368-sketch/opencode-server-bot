import sys, os, traceback
os.environ['TELEGRAM_BOT_TOKEN'] = '8839361042:AAGqZQv0D18kdvpWXgC5PZpiihKW3SsboEA'
os.environ['OWNER_ID'] = '8585609360'
try:
    with open('opencode_bot.py', 'r', encoding='utf-8') as f:
        code = f.read()
    print(f'File size: {len(code)} bytes')
    exec(compile(code, 'opencode_bot.py', 'exec'))
except Exception as e:
    traceback.print_exc()
input('Press Enter to exit')
