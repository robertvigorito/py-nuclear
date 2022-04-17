

package = nuclear
python_root = ./nuclear
python_files = $(shell find $(python_root) -name "*.py")


.PHONY: test all install deploy ninstall

all: build clean test install ninstall

build: clean
	$(eval BUILD_LOCATION=./.build/)
	pip install . -t $(BUILD_LOCATION)

clean:
	@echo Cleaning the .build directory
	@rm -f -r .build .pytest_cache .tox dist

test: clean build
	@if [ ! -d ~/dev/.wgid/wgid ]; then\
		mkdir ~/dev/.wgid/wgid ; \
	fi
	@ln -sf `realpath $(python_root)` ~/dev/.wgid/wgid/$(package)

ninstall: clean build
	$(eval install_location=~/.nuke/wgid/)
	@echo $(install_location)
	@if [ ! -d $(install_location) ]; then\
		mkdir -p $(install_location) ; \
	fi
	cp -r `realpath $(python_root)` $(install_location)



