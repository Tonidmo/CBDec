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

# Test paths
TEST_PATH 		:= tests
TEST_OUT_PATH	:= $(BUILD_DIR)/$(TEST_PATH)
TEST_OBJ_PATH 	:= $(BUILD_DIR)/.obj/tests

# GTest macros
GTEST_DIR		:= ./$(TEST_PATH)/googletest/googletest
GTEST_OUT_PATH	:= $(TEST_OUT_PATH)
GTEST_CPPFLAGS := -isystem $(GTEST_DIR)/include
GTEST_CXXFLAGS	:= -g -Wall -Wextra -pthread

# All Google Test headers.  Usually you shouldn't change this
# definition.
GTEST_HEADERS = $(GTEST_DIR)/include/gtest/*.h \
                $(GTEST_DIR)/include/gtest/internal/*.h

# Usually you shouldn't tweak such internal variables, indicated by a
# trailing _.
GTEST_SRCS_ = $(GTEST_DIR)/src/*.cc $(GTEST_DIR)/src/*.h $(GTEST_HEADERS)

# compile macros
TARGET_NAME 		:= CBlib
TARGET_LIB 			:= $(LIB_PATH)/$(TARGET_NAME).so
TARGET_TESTS_OUT 	:= $(TEST_OUT_PATH)/$(TARGET_NAME)_tests

# For the moment, only in linux
#ifeq ($(OS),Windows_NT)
#	TARGET_NAME := $(addsuffix .dll,$(TARGET_NAME))
#endif

TARGET := $(TARGET_LIB)
TARGET_DEBUG := $(DBG_PATH)/$(TARGET_NAME)

# src files & obj files
SRC := $(foreach x, $(SRC_PATH), $(wildcard $(addprefix $(x)/*,.c*)))
OBJ := $(addprefix $(OBJ_PATH)/, $(addsuffix .o, $(notdir $(basename $(SRC)))))
OBJ_DEBUG := $(addprefix $(DBG_PATH)/, $(addsuffix .o, $(notdir $(basename $(SRC)))))

TEST_SRC := $(foreach x, $(TEST_PATH), $(wildcard $(addprefix $(x)/*,.c*)))
TEST_OBJ := $(addprefix $(TEST_OBJ_PATH)/, $(addsuffix .o, $(notdir $(basename $(TEST_SRC)))))

# clean files list
DISTCLEAN_LIST := $(OBJ) \
                  $(OBJ_DEBUG) \
						$(TEST_OBJ_PATH)/*.o
CLEAN_LIST := $(TARGET) \
			  $(TARGET_DEBUG) \
			  $(TARGET_TESTS) \
			  $(GTEST_OUT_PATH)/*.a \
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

# Gtest library compilation rules
$(TEST_OBJ_PATH)/gtest-all.o : $(GTEST_SRCS_)
	$(CXX) $(GTEST_CPPFLAGS) -I$(GTEST_DIR) $(GTEST_CXXFLAGS) -c \
            $(GTEST_DIR)/src/gtest-all.cc -o $@

$(TEST_OBJ_PATH)/gtest_main.o : $(GTEST_SRCS_)
	$(CXX) $(GTEST_CPPFLAGS) -I$(GTEST_DIR) $(GTEST_CXXFLAGS) -c \
            $(GTEST_DIR)/src/gtest_main.cc -o $@

$(GTEST_OUT_PATH)/gtest.a : $(TEST_OBJ_PATH)/gtest-all.o
	$(AR) $(ARFLAGS) $@ $^

$(GTEST_OUT_PATH)/gtest_main.a : $(TEST_OBJ_PATH)/gtest-all.o $(TEST_OBJ_PATH)/gtest_main.o
	$(AR) $(ARFLAGS) $@ $^

# Test rules
$(TARGET_NAME)_tests: $(TEST_OBJ) $(GTEST_OUT_PATH)/gtest_main.a
	$(CXX) $(CXXFLAGS) -I$(GTEST_DIR)/include $^ -lpthread -o $(TEST_OUT_PATH)/$@

$(TEST_OBJ_PATH)/%.o: $(TEST_PATH)/%.c*
	$(CXX) $(COBJFLAGS) -I$(GTEST_DIR)/include -lpthread -o $@ $<


# phony rules
.PHONY: makedir
makedir:
	@mkdir -p $(LIB_PATH) $(OBJ_PATH) $(DBG_PATH) $(TEST_OUT_PATH) $(TEST_OBJ_PATH)

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