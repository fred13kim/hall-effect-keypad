# Makefile


BUILD_DIR := build

# OpenOCD
OPENOCD_SCRIPTS ?= $(OPENOCD_PATH)/tcl
OPENOCD_CMD = openocd -s $(OPENOCD_SCRIPTS) -f openocd.cfg
TARGET = keypad-fw

.PHONY: all

all: build

build:
	@echo "Creating build directory..."
	@mkdir -p $(BUILD_DIR)
	@cd $(BUILD_DIR) && cmake $(CMAKE_FLAGS) ..
	@cd $(BUILD_DIR) && make $(TARGET)

clean:
	@echo "Cleaning build directory..."
	@rm -rf $(BUILD_DIR)

debug:
	@echo "Starting OpenOCD in debug mode..."
	$(OPENOCD_CMD)

flash:
	@echo "Flashing the target..."
	$(OPENOCD_CMD) -c "program build/$(TARGET).elf verify reset exit"

