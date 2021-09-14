#!/usr/bin/env bash
CODENAME=$(grep VERSION_CODENAME /etc/os-release | cut -d = -f 2)
curl -Ls https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public > /tmp/public
gpg --no-default-keyring --keyring /tmp/adoptopenjdk-keyring.gpg --import /tmp/public
gpg --no-default-keyring --keyring /tmp/adoptopenjdk-keyring.gpg --export --output /usr/share/keyrings/adoptopenjdk-archive-keyring.gpg
rm -f /tmp/public /tmp/adopt*
echo "deb [signed-by=/usr/share/keyrings/adoptopenjdk-archive-keyring.gpg] https://adoptopenjdk.jfrog.io/adoptopenjdk/deb $CODENAME main" > /etc/apt/sources.list.d/adoptopenjdk.list
curl -s https://packagecloud.io/install/repositories/pufferpanel/pufferpanel/script.deb.sh | bash
apt -y install adoptopenjdk-8-hotspot adoptopenjdk-16-hotspot apt-transport-https gnupg pufferpanel screen wget
apt -y upgrade
systemctl enable pufferpanel
systemctl start pufferpanel
