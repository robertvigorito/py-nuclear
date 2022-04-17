

package = nuclear
python_root = ./nuclear
python_files = $(shell find $(python_root) -name "*.py")


.PHONY: test all install deploy ninstall

all: build clean test install ninstall

build: clean
	$(eval BUILD_LOCATION=./.build/wgid/$(package))
	@for file in $(python_files) ; do \
		new_file="$(BUILD_LOCATION)/$${file#*/*/}" ; \
		mkdir -p `dirname $$new_file` ; \
		cp "$$file" "$$new_file"; \
	done

clean:
	@echo Cleaning the .build directory
	@rm -f -r .build

test: clean build
	@if [ ! -d ~/dev/.wgid/wgid ]; then\
		mkdir ~/dev/.wgid/wgid ; \
	fi
	@ln -sf `realpath $(python_root)` ~/dev/.wgid/wgid/$(package)

ninstall: clean build
	$(eval install_location=~/.nuke/wgid/)
	@echo $(install_location)
	@if [ ! -d ~/dev/.wgid/wgid ]; then\
		mkdir -p $(install_location) ; \
	fi
	@ln -s `realpath $(python_root)` $(install_location) -f



