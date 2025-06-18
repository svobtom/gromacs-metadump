VERSION      ?= latest
REPO         ?= cerit.io/ceitec-biodata-pub
CONT_PREFIX  ?= gromacs-metadump-
CONTAINERS   := api worker web

# Default target: build and push all containers
.PHONY: all build-all push-all
all: build-all push-all

# Build all containers
.PHONY: build-all
build-all: $(CONTAINERS:%=build-%)

# Push all containers
.PHONY: push-all
push-all: $(CONTAINERS:%=push-%)

# Build a single container
.PHONY: build-%
build-%:
	@echo "Building $(CONT_PREFIX)$*:$(VERSION)"
	docker build -t $(REPO)/$(CONT_PREFIX)$*:$(VERSION) -f Dockerfile.$* .

# Push a single container
.PHONY: push-%
push-%:
	@echo "Pushing $(CONT_PREFIX)$*:$(VERSION)"
	docker push $(REPO)/$(CONT_PREFIX)$*:$(VERSION)

# Deploy all containers via Helm
.PHONY: deploy
deploy:
	@echo "Deploying all containers with tags from values.yaml"
	helm upgrade --install gmxmetadumpv2 ./gmxmetadump-chart -f ./gmxmetadump-chart/values.yaml -n gmxmetadump2-ns

# Retrieve last deployed version
.PHONY: last-version
last-version:
	@helm get manifest gmxmetadumpv2 -n gmxmetadump2-ns | grep "image:" | awk '{print $$2}'