# Imagen base
FROM python:3.12-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia archivo de dependencias
COPY requirements.txt .

# Instala dependencias Python
RUN pip install -r requirements.txt

# Copia código fuente
COPY main.py .

# Puerto utilizado por FastAPI
EXPOSE 8000

# Comando que se ejecuta al iniciar el contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]