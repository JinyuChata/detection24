
.GIT_COMMIT=$(shell git rev-parse HEAD)
.GIT_VERSION=$(shell git describe --tags --always --dirty 2>/dev/null)
.GIT_UNTRACKEDCHANGES := $(shell git status --porcelain --untracked-files=no)
ifneq ($(.GIT_UNTRACKEDCHANGES),)
	.GIT_VERSION := $(.GIT_VERSION)-$(shell date +"%s")
endif
LDFLAGS := "-s -w -X main.Version=$(.GIT_VERSION) -X main.GitCommit=$(.GIT_COMMIT)"


.IMAGE=dattapubali/of-watchdog
TAG?=latest-dev-x86_64

export GOFLAGS=-mod=vendor

.PHONY: all
all: gofmt dist build hashgen

.PHONY: test
test:
	@echo "+ $@"
	@go test -v ./...

.PHONY: gofmt
gofmt:
	@echo "+ $@"
	@gofmt -l -d $(shell find . -type f -name '*.go' -not -path "./vendor/*")


.PHONY: build
build:
	@echo "+ $@"
	@docker build \
		-t ${.IMAGE}:${TAG} .

.PHONY: hashgen
hashgen:
	./ci/hashgen.sh

.PHONY: dist
dist:
	@echo "+ $@"
	CGO_ENABLED=0 GOOS=linux go build -mod=vendor -a -ldflags $(LDFLAGS) -installsuffix cgo -o bin/fwatchdog-amd64
	GOARM=7 GOARCH=arm CGO_ENABLED=0 GOOS=linux go build -mod=vendor -a -ldflags $(LDFLAGS) -installsuffix cgo -o bin/fwatchdog-arm
	GOARCH=arm64 CGO_ENABLED=0 GOOS=linux go build -mod=vendor -a -ldflags $(LDFLAGS) -installsuffix cgo -o bin/fwatchdog-arm64
	GOOS=windows CGO_ENABLED=0 go build -mod=vendor -a -ldflags $(LDFLAGS) -installsuffix cgo -o bin/fwatchdog.exe

# use this with
# `./ci/copy_redist.sh $(make print-image) && ./ci/hashgen.sh`
print-image:
	@echo ${.IMAGE}
