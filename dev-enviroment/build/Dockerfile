# Use an official Python runtime as a parent image
FROM python:3.11.12-slim-bullseye

#ARG	USER=coder
# Set the working directory in the container
WORKDIR /app
# Copy the current directory contents into the container at /app
COPY . /app
# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

#RUN	useradd --groups wheel --no-create-home --shell /bin/bash ${USER} \
#	&& echo "${USER} ALL=(ALL) NOPASSWD:ALL" >/etc/sudoers \
#	&& chmod 0440 /etc/sudoers

#USER	${USER}

#WORKDIR	/home/${USER}
# Run the Python script when the container starts
#CMD ["python", "appLaptop.py"]
CMD ["python", "appUnraid.py"]
