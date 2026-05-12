# geffenlab-phy-desktop

This repository sets up a Docker environment with [Phy](https://github.com/cortex-lab/phy) and its dependencies installed.  This is intended as a utility to go along with the [geffenlab-ephys-pipeline](https://github.com/geffenlab/geffenlab-ephys-pipeline).

Geffen lab users should be able to use this image via the [run_phy.py](https://github.com/geffenlab/geffenlab-ephys-pipeline/blob/master/scripts/run_phy.py) Python script.

It's also possible to run Phy from this image directly via `docker run`, see two examples below.

# Lifecycle of this Phy images

This repository defines a Phy [environment](./environment/), including Phy itself and its dependencies.  These can be edited, committed, and pushed to this repository on GitHub.

This repository is the source of truth for this Phy environment, but we don't run Phy directly from here.  Instead we package the environment from this repository into a [Docker image](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/).  This makes the Phy environment relatively portable and reproducible.

The `geffenlab-ephys-pipeline` [run_phy.py](https://github.com/geffenlab/geffenlab-ephys-pipeline/blob/master/scripts/run_phy.py#L102) script refers to this Docker image via its `--docker-image` command line argument.

## Creating new nersions of the Docker image

This repository is configured to automatically build and publish a new Docker image, each time a [repository tag](https://git-scm.com/book/en/v2/Git-Basics-Tagging) is pushed to GitHub.

The published images are located in the GitHub Container Registry as [geffenlab-phy-desktop](https://github.com/benjamin-heasly/geffenlab-phy-desktop/pkgs/container/geffenlab-phy-desktop).  You can find the latest and previous versions of the step's Docker image there.

## Example update workflow

Here's a workflow for building and realeasing a new Docker image version.

First, make changes to the code in this repo, and `push` the changes to GitHub.

```
# Edit code
git commit -a -m "Now with lasers!"
git push
```

Next, create a new repository [tag](https://git-scm.com/book/en/v2/Git-Basics-Tagging), which marks your commit as important and gives it a unique name and description.  For the unique tag name we use version numbers like `v0.0.5`.

```
# Review existing tags and choose the next version number to use.
git pull --tags
git tag --list

# Create the tag for the next version
git tag -a v0.0.5 -m "Now with lasers!"
git push --tags
```

When you `git push --tags`, GitHub will detect your new version and kick off a fresh Docker image build.  The new image will contain the Phy environment from this repository, as of your tagged commit.

You can see the code for this automated workflow in this repository at [build-tag.yml](./.github/workflows/build-tag.yml).

You can follow the progress of the Docker image build at the step [Actions](https://github.com/benjamin-heasly/geffenlab-phy-desktop/actions) page.  When the build completes you should see a new [published version](https://github.com/benjamin-heasly/geffenlab-phy-desktop/pkgs/container/geffenlab-phy-desktop) with the version tag you provided, like `v0.0.5`.

## Update the `run_phy.py` script

When your step's new Docker image is ready you can update your calling code, for example the Geffen lab's [run_phy.py]([run_phy.py](https://github.com/geffenlab/geffenlab-ephys-pipeline/blob/master/scripts/run_phy.py#L102)) script, to use your new version number.

### older verions are still OK

Older Docker images will remain, saved on GitHub, available for use, even after you create a new version.  This means new image versions are always optional.  You can update your calling code to use new versions when you're ready.  Different people and different pipelines can use different versions of the Phy environment without interference.

# Running Phy via `docker run`

Running Phy (or any GUI app) inside a container works, but takes some configuration.  The app needs to have access to display resources on the host, and these can vary depending on where the app is running.  Here are two examples that work with X11 displays.

## Local desktop

Running locally is the easiest -- sitting at a computer with a display attached and X11 already running.  Here's a `docker run` command that should work locally:

```
# Run Phy in Docker, as the current user (not root).
# Share the X11 server's socket and DISPLAY variable with the container.
# Share a Phy data/ directory and curation results/ directory with the container.
# Scripts run from the code/ directory of this Phy environment.
docker run --rm --user $(id -u):$(id -g) \
  --volume /tmp/.X11-unix:/tmp/.X11-unix \
  --env DISPLAY=$DISPLAY \
  --volume $PWD/exported/:/data \
  --volume $PWD/curated/:/results \
  ghcr.io/benjamin-heasly/geffenlab-phy-desktop:v0.0.5 /opt/code/conda_run python /opt/code/run_phy.py
```

## Remote server via `ssh -Y`

Running on a remote server should also work, via `ssh -Y`.  In this mode Phy itself would be running on a remote server, but the X11 display would be running on your local machine.  To make this work, `ssh` on your local machine and `sshd` on the server work together to set up a TCP tunnel, allowing the remote app to connect to your local display server.  Here's a `docker run` command that should work via `ssh -Y`.

```
# Run Phy in Docker, as the current user (not root).
# Share the X11 authentication cookie and DISPLAY variable with the container.
# Allow the container to connect to the TCP tunnel on the host.
# Share a Phy data/ directory and curation results/ directory with the container, located within some DATA_DIR on the remote server.
# Scripts run from the code/ directory of this Phy environment.
docker run --rm --user $(id -u):$(id -g) \
  --volume $HOME/.Xauthority:/var/.Xauthority \
  --env DISPLAY=$DISPLAY \
  --env XAUTHORITY=/var/.Xauthority \
  --network=host \
  --volume $DATA_DIR/exported/:/data \
  --volume $DATA_DIR/curated/:/results \
  ghcr.io/benjamin-heasly/geffenlab-phy-desktop:v0.0.5 /opt/code/conda_run python /opt/code/run_phy.py
```
