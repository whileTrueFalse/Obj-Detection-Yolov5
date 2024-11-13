# Start FROM Nvidia PyTorch image
FROM nvcr.io/nvidia/pytorch:21.03-py3

# Install essential Linux packages, including libgl1 for OpenGL support
RUN apt-get update && \
    apt-get install -y zip htop screen libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies from requirements.txt
COPY requirements.txt .  # Copy the requirements file into the container
RUN python -m pip install --upgrade pip  # Upgrade pip to the latest version
RUN pip uninstall -y nvidia-tensorboard nvidia-tensorboard-plugin-dlprof  # Avoid conflicts
RUN pip install --no-cache-dir -r requirements.txt coremltools onnx gsutil notebook  # Install dependencies

# Set up the working directory for the application
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Copy application code into the container
COPY . /usr/src/app

# Set environment variables
ENV HOME=/usr/src/app
ENV PYTHONUNBUFFERED=1 

# Expose the port for Streamlit or Flask (choose accordingly)
EXPOSE 8501  
EXPOSE 5000  

# ENTRYPOINT or CMD for Streamlit (use one of these commands in your run configuration):
# ENTRYPOINT ["streamlit", "run", "main.py", "--server.port", "8501"]
# CMD ["python", "app.py"]  # For Flask (or specify the main script if using Flask)



# ---------------------------------------------------  Extra Commands  ---------------------------------------------------
# Below are additional helpful Docker commands for running, debugging, and managing containers.

# To build and push this image to Docker Hub:
# t=yourdockerhubusername/yourimagename:latest && docker build -t $t . && docker push $t

# To pull and run the image with GPU support:
# t=yourdockerhubusername/yourimagename:latest && docker pull $t && docker run -it --ipc=host --gpus all -p 8501:8501 $t

# To bash into a running container:
# docker exec -it <container_id> bash

# To bash into a stopped container:
# id=$(docker ps -qa) && docker start $id && docker exec -it $id bash

# To clean up Docker system:
# docker system prune -a --volumes
