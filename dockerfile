FROM apache/spark:3.5.1

USER root

RUN apt-get update && apt-get install -y curl build-essential && \
    rm -rf /var/lib/apt/lists/*

ENV CONDA_DIR=/opt/conda
RUN curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh" && \
    bash Miniforge3-Linux-x86_64.sh -b -p $CONDA_DIR && \
    rm Miniforge3-Linux-x86_64.sh

ENV PATH=$CONDA_DIR/bin:$PATH

RUN rm -f /usr/bin/python3 && ln -s /opt/conda/bin/python /usr/bin/python3 && \
    rm -f /usr/bin/python && ln -s /opt/conda/bin/python /usr/bin/python

COPY requirements.txt /tmp/requirements.txt

RUN conda install -y python=3.11 numpy pandas && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    conda clean -afy

RUN chown -R spark:spark $CONDA_DIR

RUN mkdir -p /home/spark/.ivy2 && \
    chown -R spark:spark /home/sparkRUN mkdir -p /home/spark/.ivy2 && \
    chown -R spark:spark /home/spark

USER spark