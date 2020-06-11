# ---------------------------------------------------
# Nuclear
# ---------------------------------------------------

AUTHOR			= rob-v
PACKAGE			= nuclear
VERSION 		= 0.1.0
DESCRIPTION 	= Nuke wrapper module

# ---------------------------------------------------
# Config
# ---------------------------------------------------

#NUKE.ROOT = ./python
#NUKE.FILES = $(shell find $(NUKE.ROOT) -type f -name "*.py")

# ---------------------------------------------------
# Nuke
# ---------------------------------------------------

NUKE.ROOT = ./nuke
NUKE.FILES = $(shell find $(NUKE.ROOT) -type f -name "*.py")

# ---------------------------------------------------
# Python
# ---------------------------------------------------

#SCRIPTS.ROOT = ""
#SCRIPTS.FILES = $(shell find $(SCRIPTS.ROOT) -type f -name "*.py")


# ---------------------------------------------------
# Resources
# ---------------------------------------------------

#SCRIPTS.ROOT = ""
#SCRIPTS.FILES = $(shell find $(SCRIPTS.ROOT) -type f -name "*")

# ---------------------------------------------------
# Scripts
# ---------------------------------------------------

#SCRIPTS.ROOT = ""
#SCRIPTS.FILES = $(shell find $(SCRIPTS.ROOT) -type f -name "*")


# ---------------------------------------------------
# Rules
# ---------------------------------------------------

.PHONY: test all install deploy

all: clean test install

clean:
	@echo Cleaning the .build directory
	@rm -f -r .build

install:
	$(eval TEMP=$(shell echo /software/scripts/$(PACKAGE)/ | tr A-Z a-z))
	@echo Installing scripts to $(TEMP)
	@rm -r -f $(TEMP)
	@mkdir -p $(TEMP)
	@install -v -m 555 $(SCRIPTS.FILES) $(TEMP)

test:
	$(eval NUKE_TEMP=$(shell echo .build/nuke/$(PACKAGE)/$(VERSION)))
	@echo Installing Nuke to $(NUKE_TEMP)
	@mkdir -p $(NUKE_TEMP)
	@install -v -m 444 $(NUKE.FILES) $(NUKE_TEMP)
	@if [ $(SCRIPTS.FILES) ]; then\
	    @mkdir -p .build/scripts;\
	    install -m 555 -v $(SCRIPTS.FILES) .build/scripts/; \
    fi

deploy:
	$(eval NUKE_TEMP=$(shell echo /software/tools/nuke/$(PACKAGE)/$(VERSION)))
	@echo Installing Nuke to $(NUKE_TEMP)
	@mkdir -p $(NUKE_TEMP)
	@ln -s -f $(NUKE_TEMP) $(shell dirname $(NUKE_TEMP))/latest
	@install -v -m 444 $(NUKE.FILES) $(NUKE_TEMP)
	@if [ $(SCRIPTS.FILES) ]; then\
	    @mkdir -p .build/scripts;\
	    install -m 555 -v $(SCRIPTS.FILES) .build/scripts/; \
    fi
	-git tag v$(VERSION)
	-git push --tags

