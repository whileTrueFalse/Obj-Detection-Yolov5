# Start FROM Nvidia PyTorch image
FROM nvcr.io/nvidia/pytorch:21.03-py3

# Install necessary system packages, including libgl1
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libxrender1 \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /usr/src/app

# Copy the project files into the Docker container
COPY . .

# Upgrade pip and install Python dependencies from requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for Streamlit
EXPOSE 8501

# Set environment variables to configure Streamlit for deployment
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ENABLECORS=false

# Command to run Streamlit app
CMD ["streamlit", "run", "main.py", "--server.port=8501"]
