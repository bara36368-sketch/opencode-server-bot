FROM python:3.12-slim
WORKDIR /bot
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV WEB_GATEWAY_PORT=4357
CMD ["python", "opencode_bot.py"]