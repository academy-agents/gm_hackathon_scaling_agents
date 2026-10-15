FROM node:24-bookworm-slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends bash curl ca-certificates git ripgrep openssh-client \
  && rm -rf /var/lib/apt/lists/*
RUN npm install -g --ignore-scripts @earendil-works/pi-coding-agent

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

RUN pi install git:github.com/GusEllerm/pi-lab-profile
RUN git clone --depth 1 https://github.com/GusEllerm/pi-lab-profile /tmp/pi-lab-profile \
  && /tmp/pi-lab-profile/scripts/install.sh lab \
  && rm -rf /tmp/pi-lab-profile

RUN git clone --depth 1 https://github.com/academy-agents/genesis_mission_hackathon /workspace/genesis_mission_hackathon
WORKDIR /workspace/genesis_mission_hackathon

CMD ["pi"]
