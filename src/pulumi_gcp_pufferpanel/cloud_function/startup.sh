#!/usr/bin/env bash
CODENAME=$(grep VERSION_CODENAME /etc/os-release | cut -d = -f 2)
curl -Ls https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public > /tmp/public
gpg --no-default-keyring --keyring /tmp/adoptopenjdk-keyring.gpg --import /tmp/public
gpg --no-default-keyring --keyring /tmp/adoptopenjdk-keyring.gpg --export --output /usr/share/keyrings/adoptopenjdk-archive-keyring.gpg
rm -f /tmp/public /tmp/adopt*
echo "deb [signed-by=/usr/share/keyrings/adoptopenjdk-archive-keyring.gpg] https://adoptopenjdk.jfrog.io/adoptopenjdk/deb $CODENAME main" > /etc/apt/sources.list.d/adoptopenjdk.list
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
curl -s https://packagecloud.io/install/repositories/pufferpanel/pufferpanel/script.deb.sh | bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt -y install adoptopenjdk-8-hotspot adoptopenjdk-16-hotspot apt-transport-https ca-certificates curl gnupg lsb-release pufferpanel screen wget
apt -y upgrade
systemctl enable docker
systemctl enable pufferpanel
systemctl restart docker
systemctl restart pufferpanel
