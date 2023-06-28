FROM dipdup/dipdup:6
COPY . .
RUN pip install -r requirements.txt
