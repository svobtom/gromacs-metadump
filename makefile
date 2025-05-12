# Makefile Documentation
#
# Overview:
#   This Makefile automates the process of building and pushing Docker containers.
#
# Targets:
#   all
#     - Builds all containers specified in the CONTAINERS variable.
#
#   <container> (e.g., container1, container2, container3)
#     - Builds a specific container by invoking a pattern rule.
#     - Uses a dedicated Dockerfile named "Dockerfile.<container>" for each container.
#
#   push
#     - Runs the 'all' target to build all containers.
#     - Iterates through each container and pushes the built image to a Docker repository.
#
# Variables:
#   VERSION (default: latest)
#     - Used to tag the Docker images with the specified version.
#     - Can be overridden from the command line.
#
#   REPO (default: myrepo)
#     - Specifies the Docker repository where images will be pushed.
#     - Can also be overridden from the command line.
#
# Usage Examples:
#
#   1. Build All Containers:
#        make
#
#   2. Build a Specific Container (e.g., container2):
#        make container2
#
#   3. Build and Push All Containers:
#        make push
#
# Command Line Overrides:
#   You can override the default VERSION and REPO values by passing them as arguments:
#
#       make VERSION=1.0 REPO=yourrepo
#
# End of Documentation
# Version tag and repository can be overridden from the command line.
VERSION ?= latest
REPO    ?= myrepo

# List of containers. Each container should have its own Dockerfile named: Dockerfile.<container>
CONTAINERS := api worker web
REPO := cerit.io/ceitec-biodata-pub
CONT_PREFIX := gromacs-metadump-

# Default target: builds all containers
all: $(CONTAINERS)

$(CONTAINERS):
	docker build -t $(REPO)/$(CONT_PREFIX)$@:$(VERSION) -f Dockerfile.$@ .

# Push routine: pushes all containers after building.
push: all
	@for container in $(CONTAINERS); do \
	  echo "Pushing $(CONT_PREFIX)$$container:$(VERSION)"; \
	  docker push $(REPO)/$(CONT_PREFIX)$$container:$(VERSION); \
	done

deploy-upgrade:
	helm upgrade --install gmxmetadumpv2 ./gmxmetadump-chart -n gmxmetadump2-ns \
		--set image.web.tag=$(VERSION) \
		--set image.api.tag=$(VERSION) \
		--set image.worker.tag=$(VERSION) \

.PHONY: all $(CONTAINERS) push