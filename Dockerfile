FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl netcat-openbsd wget bzip2 ca-certificates build-essential \
    libglib2.0-0 libnss3 libgconf-2-4 \
    libx11-xcb1 libxcomposite1 libxcursor1 libxi6 libxtst6 \
    libxrandr2 libasound2 libpangocairo-1.0-0 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 && \
    rm -rf /var/lib/apt/lists/*

# Set Conda directory
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

# Install Miniconda (correct ARCH: x86_64 or aarch64)
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh; \
    elif [ "$ARCH" = "aarch64" ]; then \
        wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh -O /tmp/miniconda.sh; \
    else \
        echo "Unsupported architecture: $ARCH"; exit 1; \
    fi && \
    bash /tmp/miniconda.sh -b -p $CONDA_DIR && \
    rm /tmp/miniconda.sh

# Update Conda
RUN conda update -n base -c defaults conda

# Create a Conda environment and install everything needed
RUN conda create -n scraper-env python=3.10 && \
    conda run -n scraper-env conda install -y pytorch torchvision torchaudio cpuonly -c pytorch -c defaults && \
    conda run -n scraper-env pip install \
      transformers==4.51.3 \
      datasets==2.19.0 \
      scikit-learn==1.6.1 \
      selenium==4.31.0 \
      requests==2.32.3 \
      beautifulsoup4==4.13.4 \
      hf_xet \
      accelerate==0.28.0

# exporting the conda environment for faster builds
RUN conda env export --name scraper-env > environment.yml


# Activate the environment for all next layers
SHELL ["conda", "run", "-n", "scraper-env", "/bin/bash", "-c"]

# Set working directory
WORKDIR /app

# Copy your code
COPY . .

# Make wait-for-it.sh executable
RUN chmod +x wait-for-it.sh

# Default entrypoint
ENTRYPOINT ["conda", "run", "-n", "scraper-env", "bash", "wait-for-it.sh", "selenium-hub", "4444", "--"]
