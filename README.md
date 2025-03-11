# OpenHTI

A lightweight hardware test interface (HTI).

## Install

### Repository

When using git, clone the repository and change your 
present working directory.

```shell
git clone http://github.com/mcpcpc/openhti
cd openhti/
```

Create and activate a virtual environment.

```shell
python -m venv venv
source venv/bin/activate
```

Install OpenHTI to the virtual environment.

```shell
pip install -e .
```

## Commands

### db-init

The backend database can be initialized or re-initialized 
with the following command.

```shell
quart --app openhti init-db
```

## Deploy

## Docker Container

Pulling the latest container image from command line.

```shell
podman pull ghcr.io/mcpcpc/openhti:latest
```

### Service

Stop and/or remove any existing running instances.

```sh
podman stop openhti
podman rm openhti
```

Pull the latest container image and start an instance. Replace `/home/pi/instance/` with the appropriate user home directory and instance path.

```sh
podman pull pull ghcr.io/mcpcpc/openhti:latest
podman run -dt -p 8080:8080 \
  --name uhtf \
  --volume /home/pi/instance/:/app/instance \
  uhtf
```

Replace `pi` with the appropriate user home directory.

```sh
podman generate systemd --new --files --name openhti
mkdir -p /home/pi/.config/systemd/user
cp container-openhti.service /home/pi/.config/systemd/user
systemctl --user daemon-reload
systemctl --user start container-openhti.service
systemctl --user enable container-openhti.service
loginctl enable-linger pi
```

## Test

```shell
python3 -m unittest
```

Run with coverage report.

```shell
coverage run -m unittest
coverage report
coverage html  # open htmlcov/index.html in a browser
```
