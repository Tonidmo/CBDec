# Template Makefile taken from https://github.com/TheNetAdmin/Makefile-Templates and modified to suit the needs of 
# CBlib.

# tool macros
CC ?= gcc
CXX ?= g++
CFLAGS := -Wall -Wextra -Werror -Wstack-protector -fPIC
CXXFLAGS := -Wall -Wextra -Werror -Wstack-protector -fPIC
DBGFLAGS := -g -D DEBUG_CBLIB
COBJFLAGS := $(CXXFLAGS) -c

# path macros
BUILD_DIR := build
LIB_PATH := $(BUILD_DIR)/lib
OBJ_PATH := $(BUILD_DIR)/.obj
SRC_PATH := src
INC_PATH := src
DBG_PATH := $(BUILD_DIR)/debug

# compile macros
TARGET_NAME := CBlib.so

# For the moment, only in linux
#ifeq ($(OS),Windows_NT)
#	TARGET_NAME := $(addsuffix .dll,$(TARGET_NAME))
#endif

TARGET := $(LIB_PATH)/$(TARGET_NAME)
TARGET_DEBUG := $(DBG_PATH)/$(TARGET_NAME)

# src files & obj files
SRC := $(foreach x, $(SRC_PATH), $(wildcard $(addprefix $(x)/*,.c*)))
OBJ := $(addprefix $(OBJ_PATH)/, $(addsuffix .o, $(notdir $(basename $(SRC)))))
OBJ_DEBUG := $(addprefix $(DBG_PATH)/, $(addsuffix .o, $(notdir $(basename $(SRC)))))

# clean files list
DISTCLEAN_LIST := $(OBJ) \
                  $(OBJ_DEBUG)
CLEAN_LIST := $(TARGET) \
			  $(TARGET_DEBUG) \
			  $(DISTCLEAN_LIST)

# default rule
default: makedir all

# non-phony targets
$(TARGET): $(OBJ)
	$(CXX) $(CXXFLAGS) -shared -I$(INC_PATH) -o $@ $(OBJ) 

$(OBJ_PATH)/%.o: $(SRC_PATH)/%.c*
	$(CXX) $(COBJFLAGS) -I$(INC_PATH) -o $@ $<

$(DBG_PATH)/%.o: $(SRC_PATH)/%.c*
	$(CXX) $(COBJFLAGS) $(DBGFLAGS) -I$(INC_PATH) -o $@ $<

$(TARGET_DEBUG): $(OBJ_DEBUG)
	$(CXX) $(CXXFLAGS) $(DBGFLAGS) -I$(INC_PATH) $(OBJ_DEBUG) -o $@

# phony rules
.PHONY: makedir
makedir:
	@mkdir -p $(LIB_PATH) $(OBJ_PATH) $(DBG_PATH)

.PHONY: all
all: $(TARGET)

.PHONY: debug
debug: $(TARGET_DEBUG)

.PHONY: clean
clean:
	@echo CLEAN $(CLEAN_LIST)
	@rm -f $(CLEAN_LIST)

.PHONY: distclean
distclean:
	@echo CLEAN $(DISTCLEAN_LIST)
	@rm -f $(DISTCLEAN_LIST)