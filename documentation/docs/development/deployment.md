---
title: Deployment
authors: Dr Marcus Baw
---

This page is a work in progress, as we are currently working on migrating to this new deployment method.

Set up a new VPS server instance and access it via SSH

### Adds a command to make OS updates quicker and more consistent

```bash
sudo echo "alias doupdates='sudo apt update && sudo apt dist-upgrade && sudo apt autoremove && sudo apt autoclean'" >> /etc/profile;source /etc/profile
```

### Run the new `doupdates` command

```bash
doupdates
```

### Add other SSH users using their public keys from GitHub

```bash
ssh-import-id gh:eatyourpeas
ssh-import-id gh:pacharanero
```

### Clone the Epilepsy12 repository

```bash
sudo git clone --single-branch --branch development https://github.com/rcpch/rcpch-audit-engine.git /var/rcpch-audit-engine
```

This command clones only the branch `development` and not the whole repository, which saves time and disk space.
It also clones it into the `/var/rcpch-audit-engine` folder, which we have chosen as the standard location for the E12 application.

`cd` into the new folder

```bash
cd rcpch-audit-engine/
```

### Install :fontawesome-brands-docker: Docker

```bash
curl -fsSL get.docker.com | bash
```

### Install Zsh and Oh My Zsh

Two tools I find quite nice when spending a lot of time in the terminal are [Zsh](https://www.zsh.org/) and [oh-my-zsh](https://ohmyz.sh/)

These give you additional features in the terminal, such as better tab completion and a terminal prompt which includes the Git branch you are currently using.

> Note that if you escalate your privileges to `root` using `sudo su` or similar then the new root shell will not have Zsh set up, so you may need to install Zsh into both your userspace and the root userspace.

Install Zsh

```console
sudo apt install zsh
```

Install oh-my-zsh

```console
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

**Optional**: Change the ZSH_THEME from the default to my preferred "bira"

```console
sed -i '/ZSH_THEME="robbyrussell"/c\ZSH_THEME="bira"' ~/.zshrc
```

**Optional**: Add some useful plugins for Git, Docker etc

```console
sed -i '/plugins=(git)/c\plugins=(git git-extras wd docker docker-compose)' ~/.zshrc
```

You can also edit `~/.zshrc` to customise

```console
nano ~/.zshrc
```

### Useful commands

Outputs all the environment variables from within Docker Compose to the console, this can be useful for debugging deployments.

```console
docker compose config
```


