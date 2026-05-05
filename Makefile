SHELL := /bin/bash

ENV ?=
VERSION ?=

.PHONY: env-use env-show deploy release-prepare release-publish release-status dev-up dev-down dev-check

env-use:
	./scripts/ops/env-use.sh "$(ENV)"

env-show:
	./scripts/ops/env-show.sh

deploy:
	./scripts/ops/deploy.sh

release-prepare:
	./scripts/ops/release-prepare.sh "$(VERSION)"

release-publish:
	./scripts/ops/release-publish.sh "$(VERSION)"

release-status:
	./scripts/ops/release-status.sh "$(VERSION)"

dev-up:
	./scripts/ops/dev-up.sh

dev-down:
	./scripts/ops/dev-down.sh

dev-check:
	./scripts/ops/dev-check.sh
