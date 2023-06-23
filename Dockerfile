FROM dipdup/dipdup:6.1-slim
COPY . .
RUN install_dependencies requirements.txt
