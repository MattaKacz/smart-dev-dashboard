FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# [opcjonalnie] Azure ustawia PORT, ale możesz jawnie zadeklarować
ENV PORT=8000

# Wystaw port (ważne dla Azure)
EXPOSE 8000

# Upewnij się, że ścieżka "app.main:app" jest zgodna z Twoją strukturą projektu!
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]