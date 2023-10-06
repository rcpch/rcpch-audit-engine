---
title: Deployment
authors: Dr Marcus Baw
---

This is a work in progress, as we are currently working on migrating to this new deployment method.

Set up a new VPS server instance and access it via SSH

Adds a command to make OS updates quicker and more consistent
```bash
sudo echo "alias doupdates='sudo apt update && sudo apt dist-upgrade && sudo apt autoremove && sudo apt autoclean'" >> /etc/profile;source /etc/profile
```

Run the new `doupdates` command
```bash
doupdates
```

Add other SSH users using their public keys from GitHub
```bash
ssh-import-id gh:eatyourpeas
```

Clone the Epilepsy12 repository
```bash
```bash
sudo git clone --single-branch --branch development https://github.com/rcpch/rcpch-audit-engine.git /var/rcpch-audit-engine
```
This command clones only the branch `development` and not the whole repository, which saves time and disk space.
It also clones it into the `/var/rcpch-audit-engine` folder, which we have chosen as the standard location for the E12 application.

`cd` into the new folder
```bash
cd rcpch-audit-engine/
```

Install Docker
```bash
curl -fsSL get.docker.com | bash
```
