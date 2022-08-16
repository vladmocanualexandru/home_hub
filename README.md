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
sudo mount <drive path>/mnt/storage
```
In order to have the drive mounted at boot:
```
nano /etc/fstab
```
Add the following line at the end:
```
<drive path>    /mnt/storage      ext4        defaults      0       0
```

SOURCE: https://sh-tsang.medium.com/partitioning-formatting-and-mounting-a-hard-drive-in-linux-ubuntu-18-04-324b7634d1e0

## Samba

## Postgres
```
docker run --name postgres -e POSTGRES_PASSWORD=mysecretpassword -d postgres
```