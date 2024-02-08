/***********************************************************************************************************************
 * @file    CBlib_tests.cpp
 * @author  Imanol Etxezarreta (ietxezarretam@gmail.com)
 * 
 * @brief   This file defines tests associated with CBlib to ensure correct operation of the library.
 * 
 * @version 0.1
 * @date    2024-02-06
 * 
 * @copyright Copyright (c) 2024
 * 
 **********************************************************************************************************************/
#include <stdio.h>
#include <vector>
#include <gtest/gtest.h>

#include "CBlib.h"

#define  INITIAL_MEM_ALLOC   (uint16_t)UINT16_MAX

/***********************************************************************************************************************
 * START OF CLOSEDBRANCH CLASS TESTS
 **********************************************************************************************************************/
TEST(CBlib_CLOSED_BRANCH, 001_DEFAULT_CONSTRUCTOR) {

   // To initialize with
   std::vector<bool> au1_aux_checks = std::vector<bool>(INITIAL_MEM_ALLOC, false);
   std::vector<bool> au1_aux_events = std::vector<bool>(INITIAL_MEM_ALLOC, false);

   // To compare with
   std::vector<bool> au1_aux2_checks = std::vector<bool>(INITIAL_MEM_ALLOC, false);
   std::vector<bool> au1_aux2_events = std::vector<bool>(INITIAL_MEM_ALLOC, false);

   CBlib::ClosedBranch o_cb = CBlib::ClosedBranch();

   au1_aux_checks.clear();
   au1_aux_events.clear();

   ASSERT_EQ(au1_aux_checks.empty(), true);
   ASSERT_EQ(au1_aux_events.empty(), true);
   ASSERT_EQ(INITIAL_MEM_ALLOC, o_cb.get_cb_checks().size());
   ASSERT_EQ(INITIAL_MEM_ALLOC, o_cb.get_cb_events().size());
   ASSERT_EQ(au1_aux2_checks, o_cb.get_cb_checks());
   ASSERT_EQ(au1_aux2_events, o_cb.get_cb_events());
}

TEST(CBlib_CLOSED_BRANCH, 002_CONSTRUCTOR_1) {

   std::vector<bool> au1_aux_checks = std::vector<bool>(INITIAL_MEM_ALLOC/2, false);
   std::vector<bool> au1_aux_events = std::vector<bool>(INITIAL_MEM_ALLOC/2, false);

   CBlib::ClosedBranch o_cb = CBlib::ClosedBranch(au1_aux_checks, au1_aux_events);

   ASSERT_EQ(INITIAL_MEM_ALLOC/2U, o_cb.get_cb_checks().size());
   ASSERT_EQ(INITIAL_MEM_ALLOC/2U, o_cb.get_cb_events().size());
   ASSERT_EQ(au1_aux_checks, o_cb.get_cb_checks());
   ASSERT_EQ(au1_aux_events, o_cb.get_cb_events());
}