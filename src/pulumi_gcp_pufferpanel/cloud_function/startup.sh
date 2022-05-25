#!/usr/bin/env bash
CODENAME=$(grep VERSION_CODENAME /etc/os-release | cut -d = -f 2)
curl -Ls https://packages.adoptium.net/artifactory/api/gpg/key/public > /usr/share/keyrings/adoptium.asc
echo "deb [signed-by=/usr/share/keyrings/adoptium.asc] https://packages.adoptium.net/artifactory/deb $CODENAME main" > /etc/apt/sources.list.d/adoptium.list
curl -s https://packagecloud.io/install/repositories/pufferpanel/pufferpanel/script.deb.sh | bash
apt install -y \
    ca-certificates \
    gnupg \
    lsb-release \
    pufferpanel \
    screen \
    temurin-8-jdk \
    temurin-11-jdk \
    temurin-17-jdk \
    wget
apt -y upgrade
systemctl enable pufferpanel
systemctl restart pufferpanel
