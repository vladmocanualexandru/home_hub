# home.hub
Repository for everything concerning home.hub. Mainly how to setup.

## Distro
- Ubuntu Server 22.04.1 LTS
- Installed on nvme
- Added docker during optional packages

## After installation docker stuff
By default user is not added to docker group, so all docker commands must be done through sudo.

```
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
sudo shutdown -r 0
```

SOURCE: https://docs.docker.com/engine/install/linux-postinstall/


## Storage SSD
In order to use as storage, new drive must be formatted as ext4 and then mounted

Check drive (locate drive path, e.g. "/dev/sda")
```
sudo fdisk -l
```
### Format
Open "parted" 
```
sudo parted <drive path>
```
Within "parted":
```
mklabel gpt
mkpart primary 0GB <desired size>GB
quit
```
After closing "parted":
```
sudo mkfs.ext4 <drive path>
```
### Mount
```
sudo mkdir /mnt/storage
sudo mount <drive path> /mnt/storage
```
In order to have the drive mounted at boot:
```
sudo nano /etc/fstab
```
Add the following line at the end:
```
<drive path>    /mnt/storage      ext4        defaults      0       0
```

SOURCE: https://sh-tsang.medium.com/partitioning-formatting-and-mounting-a-hard-drive-in-linux-ubuntu-18-04-324b7634d1e0

## Samba
```
docker run -it --name samba -p 139:139 -p 445:445 -v <shared folder on host>:<shared folder in container> --restart always -d dperson/samba -p -u "<user>;<password>" -s "share;<shared folder in container>;yes;no"
 
```
Shared folder will be available accessing:
```
http://<host>/share
```

SOURCE: https://hub.docker.com/r/dperson/samba

## Postgres
```
docker run --restart=unless-stopped --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=<postgres password> -d postgres
```

## Adding custom DNS rules for Pi-hole
Add a .conf file in "/etc/dnsmasq.d" in which the rules are added following the pattern:
```
address=/<domain>/<ip>
```
```
sudo nano /etc/dnsmasq.d/91-custom-rules.conf 
```
SOURCE: https://blog.mdoff.net/2019/how-add-custom-dns-entries-in-pi-hole/

## Home Assistant

### Install 

Zigbee USB dongle must be plugged in.

```
docker run -d \
  --name homeassistant \
  --privileged \
  --restart=unless-stopped \
  -e TZ=Europe/Bucharest \
  -v /PATH_TO_YOUR_CONFIG:/config \
  --network=host \
  --device /dev/ttyUSB0:/dev/ttyUSB0
  ghcr.io/home-assistant/home-assistant:stable
```

PATH_TO_YOUR_CONFIG points to location of configuration files (must be inside "~", e.g. /home/vlad/home_assistant)

### Open
```
http://home.hub:8123
```

### Backup

#### Create backup automation

Trigger: When time is equal to 03:00:00
Action: Create backup

#### Copy backup

```
#! /bin/bash

unset -v sourceFullPath
for file in "<HOST HA CONFIG FOLDER>/backups"/*; do
  [[ $file -nt $sourceFullPath ]] && sourceFullPath=$file
done

echo $sourceFullPath

destFullPath="<BACKUP DESTINATION>/"$(date "+%Y-%m-%d")".tar"

echo $destFullPath

cp $sourceFullPath $destFullPath
```

#### Schedule backup copy
```
0 1 * * * <PATH TO COPY SH SCRIPT> > <CRONTAB LOG FILE> 2>&1
```

SOURCE: https://www.home-assistant.io/installation/linux#install-home-assistant-container

## MQTT Broker

Create volume folder and inside, create folder "config". Within config, create a file called "mosquitto.conf" with content:
```
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
listener 1883

## Authentication ##
#allow_anonymous false
#password_file /mosquitto/config/password.txt
```

Create container
```
docker run --name mqtt -d --restart=unless-stopped -it -p 1883:1883 -v <PATH TO VOLUME FOLDER>:/mosquitto eclipse-mosquitto
```

Open shell inside container
```
docker exec -it mqtt /bin/sh
```

Create user account
```
mosquitto_passwd -c /mosquitto/config/password.txt hass
```

Close shell, restart container, add broker via HASS MQTT integration.

SOURCE1: https://hub.docker.com/_/eclipse-mosquitto
SOURCE2: https://www.homeautomationguy.io/docker-tips/configuring-the-mosquitto-mqtt-docker-container-for-use-with-home-assistant/

### Register MQTT device
In order to register and MQTT device, send config message on topic
```
homeassistant/<COMPONENT TYPE>/<OBJECT ID>/config
```
e.g.:
```
homeassistant/sensor/laptopVBattery/config
```

Message payload:
```
{
  "device_class": "<DEVICE CLASS>", 
  "name": "<NAME OF OBJECT AS IT APPEARS IN HASS>", 
  "state_topic": "<TOPIC USED TO SEND STATE>", 
  "unit_of_measurement": "<UNIT OF MEASUREMENT>",
  "value_template": "{{ value_json.<NAME OF THE VALUE FIELD IN PAYLOAD> }}" 
}
```
e.g.:
```
{
  "device_class": "battery", 
  "name": "LaptopVBattery", 
  "state_topic": "homeassistant/sensor/laptopV",
  "unit_of_measurement": "%",
  "value_template": "{{ value_json.battery}}" 
}
```

### Publish message from MQTT device
Once registered, the device can publish messages on the <TOPIC USED TO SEND STATE> with the following payload:
```
{
  "<NAME OF THE VALUE FIELD IN PAYLOAD>": <VALUE>
}
```
e.g.:
```
{
  "battery": 90
}
```

SOURCE: https://www.home-assistant.io/docs/mqtt/discovery/
