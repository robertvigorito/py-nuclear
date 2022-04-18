

package = nuclear
python_root = ./nuclear
python_files = $(shell find $(python_root) -name "*.py")


.PHONY: test all install deploy ninstall

all: build clean test install ninstall

build: clean
	$(eval BUILD_LOCATION=./.build)
	pip install . -t $(BUILD_LOCATION)

clean:
	@echo Cleaning the .build directory
	@rm -f -r .build .pytest_cache .tox dist *.egg-info build

test: clean build
	@if [ ! -d ~/dev/.wgid/wgid ]; then\
		mkdir ~/dev/.wgid/wgid ; \
	fi

ninstall:
	$(eval BUILD_LOCATION=~/.nuke/site-packages/)
	pip install . -t $(BUILD_LOCATION) --upgrade
	$(MAKE) clean