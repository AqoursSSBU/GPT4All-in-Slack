FROM ubuntu:jammy as builder
RUN apt-get update
RUN apt-get install -y liblzma-dev git cmake build-essential python3 python3-pip
WORKDIR /tmp
RUN git clone --recurse-submodules https://github.com/nomic-ai/gpt4all 
WORKDIR /tmp/gpt4all/gpt4all-backend/
RUN mkdir build
WORKDIR /tmp/gpt4all/gpt4all-backend/build
RUN cmake .. && cmake --build . --parallel 
WORKDIR /tmp/gpt4all/gpt4all-bindings/python
RUN pip install -e .


COPY requirements.txt /build/
WORKDIR /build/
RUN pip install -U pip && pip install -r requirements.txt
RUN apt-get upgrade -y gcc

FROM builder as app
WORKDIR /app/
COPY *.py /app/
RUN mkdir /app/app/
COPY app/*.py /app/app/
COPY *.bin /root/.cache/gpt4all/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /usr/local/lib/ /usr/local/lib/
ENTRYPOINT python3 main.py

# docker buildx build . --platform linux/amd64 -t gpt4all-slack
# export SLACK_APP_TOKEN=xapp-...
# export SLACK_BOT_TOKEN=xoxb-...
# docker run -e SLACK_APP_TOKEN=$SLACK_APP_TOKEN -e SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN -it your-repo/chat-gpt-in-slack
