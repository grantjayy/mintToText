FROM selenium/standalone-chrome

ENV PATH=$HOME/.local/bin:$PATH
ENV FLASK_ENV=development

RUN sudo apt-get update && \
    sudo apt-get install -y python3-pip python && \
    sudo apt-get clean && \
    sudo rm -rf \
    /tmp/* \
    /var/lib/apt/lists/* \
    /var/tmp/*

EXPOSE 8080

COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN pip install -U Flask

COPY .env ./
COPY app.py ./

CMD ["flask", "run", "-p", "8080", "-h", "0.0.0.0"]