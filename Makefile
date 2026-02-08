DOCKER ?= docker
IMAGE ?= udp-test
PYTHON ?= python3

COUNT ?= 200
INTERVAL_MS ?= 16
TIMEOUT ?= 1.0
PORT ?= 9000
TCP_SIZE ?= 8
DOCKER_RUN = $(DOCKER) run --rm --privileged \
	-v "$$PWD:/workspace" -w /workspace \
	-v /lib/modules:/lib/modules:ro \
	$(IMAGE)

LOSS_LEVELS ?= 1 3 6

.PHONY: help docker-build docker-loss-sweep

help:
	@echo "Targets:"
	@echo "  make docker-build     # build docker image"
	@echo "  make docker-loss-sweep # loss-only sweep (1%/3%/6%)"
	@echo ""
	@echo "Variables:"
	@echo "  COUNT=200 INTERVAL_MS=16 TIMEOUT=1.0 PORT=9000 TCP_SIZE=8"
	@echo "  LOSS_LEVELS=\"1 3 6\""
	@echo "  Output: plots/loss_sweep_p99.png"

docker-build:
	$(DOCKER) build -t $(IMAGE) .

docker-loss-sweep: docker-build
	$(DOCKER_RUN) bash -lc "$(PYTHON) scripts/loss_sweep_plot.py --loss-levels '$(LOSS_LEVELS)' --count $(COUNT) --interval-ms $(INTERVAL_MS) --timeout $(TIMEOUT) --port $(PORT) --tcp-size $(TCP_SIZE)"
