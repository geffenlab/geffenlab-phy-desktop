# geffenlab-phy-desktop

This sets up a Docker environment with [Phy](https://github.com/cortex-lab/phy) installed.

# Phy sample data

The Phy project has some sample data that might help with testing.

```
wget https://codeload.github.com/kwikteam/phy-data/zip/master -O phy-data.zip
unzip phy-data.zip
```

# Building Docker image versions

This repo is configured to automatically build and publish a new Docker image version, each time a [repo tag](https://git-scm.com/book/en/v2/Git-Basics-Tagging) is pushed to GitHub.

## Published versions

The published images are located in the GitHub Container Registry as [geffenlab-phy-desktop](https://github.com/benjamin-heasly/geffenlab-phy-desktop/pkgs/container/geffenlab-phy-desktop).  You can find the latest published version at this page.

You can access published images using their full names.  For version `v0.0.1` the full name would be `ghcr.io/benjamin-heasly/geffenlab-phy-desktop:v0.0.1`.  You can use this name in [Nexflow pipeline configuration](https://github.com/benjamin-heasly/geffenlab-ephys-pipeline/blob/master/pipeline/main.nf#L103) and with Docker commands like:

```
docker pull ghcr.io/benjamin-heasly/geffenlab-phy-desktop:v0.0.1
```

## Releasing new versions

Here's a workflow for building and realeasing a new Docker image version.

First, make changes to the code in this repo, and `push` the changes to GitHub.

```
# Edit code
git commit -a -m "Now with lasers!"
git push
```

Next, create a new repository [tag](https://git-scm.com/book/en/v2/Git-Basics-Tagging), which marks the most recent commit as important, giving it a unique name and description.

```
# Review existing tags and choose the next version number to use.
git pull --tags
git tag -l

# Create the tag for the next version
git tag -a v0.0.5 -m "Now with lasers!"
git push --tags
```

GitHub should automatically kick off a build and publish workflow for the new tag.
You can follow the workflow progress at the repo's [Actions](https://github.com/benjamin-heasly/geffenlab-phy-desktop/actions) page.

You can see the workflow code in [build-tag.yml](./.github/workflows/build-tag.yml).

# Phy in a container

Running Phy (or any GUI app) inside a container works, but takes some configuration.  The app needs to have access to display resources on the host, and these can vary depending on where the app is running.  Here are two examples that work with X11 displays.

## Local desktop

Running locally is the easiest -- sitting at a computer with a display attached and X11 already running.  Here's a `docker run` command that should work locally:

```
# Run Phy in Docker, as the current user (not root).
# Share the X11 server's socker and DISPLAY variable with the container.
# Share a Phy data/ directory and curation results/ directory with the container.
# Run scripts from the code/ dir of this repo.
docker run --rm --user $(id -u):$(id -g) \
  --volume /tmp/.X11-unix:/tmp/.X11-unix \
  --env DISPLAY=$DISPLAY \
  --volume $PWD/exported/:/data \
  --volume $PWD/curated/:/results \
  ghcr.io/benjamin-heasly/geffenlab-phy-desktop:v0.0.1 /opt/code/conda_run python /opt/code/run_phy.py
```

## Remote server via `ssh -Y`

Running on a remote server should also work, via `ssh -Y`.  In this mode Phy itself would be runnong on a remote server, but the X11 display would be running on your local machine.  To make this work, `ssh` on your local machine and `sshd` on the server work together to set up a TCP tunnel, allowing the app to connect to your local display server.  Here's a `docker run` command that should work via `ssh -Y`.


```
# Run Phy in Docker, as the current user (not root).
# Share the X11 authentication cookie and DISPLAY variable with the container.
# Allow the container to connect to the TCP tunnel on the host.
# Share a Phy data/ directory and curation results/ directory with the container, located within some DATA_DIR on the remote server.
# Run scripts from the code/ dir of this repo.
docker run --rm --user $(id -u):$(id -g) \
  --volume $HOME/.Xauthority:/var/.Xauthority \
  --env DISPLAY=$DISPLAY \
  --env XAUTHORITY=/var/.Xauthority \
  --network=host \
  --volume $DATA_DIR/exported/:/data \
  --volume $DATA_DIR/curated/:/results \
  ghcr.io/benjamin-heasly/geffenlab-phy-desktop:v0.0.1 /opt/code/conda_run python /opt/code/run_phy.py
```
