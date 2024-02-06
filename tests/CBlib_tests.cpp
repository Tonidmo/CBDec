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

/***********************************************************************************************************************
 * START OF CLOSEDBRANCH CLASS TESTS
 **********************************************************************************************************************/

TEST(CBlib_CLOSED_BRANCH, 001_DEFAULT_CONSTRUCTOR) {

   std::vector<bool> au1_aux_checks = std::vector<bool>(MAX_BRANCH_CHECKS_LEN, false);
   std::vector<bool> au1_aux_events = std::vector<bool>(MAX_BRANCH_EVENTS_LEN, false);

   CBlib::ClosedBranch o_cb = CBlib::ClosedBranch();

   ASSERT_EQ(MAX_BRANCH_CHECKS_LEN, o_cb.get_cb_checks().size());
   ASSERT_EQ(MAX_BRANCH_EVENTS_LEN, o_cb.get_cb_events().size());
   ASSERT_EQ(au1_aux_checks, o_cb.get_cb_checks());
   ASSERT_EQ(au1_aux_events, o_cb.get_cb_events());
}

TEST(CBlib_CLOSED_BRANCH, 002_CONSTRUCTOR_1) {

   std::vector<bool> au1_aux_checks = std::vector<bool>(MAX_BRANCH_CHECKS_LEN/2, false);
   std::vector<bool> au1_aux_events = std::vector<bool>(MAX_BRANCH_EVENTS_LEN/2, false);

   CBlib::ClosedBranch o_cb = CBlib::ClosedBranch(au1_aux_checks, au1_aux_events);

   ASSERT_EQ(MAX_BRANCH_CHECKS_LEN/2, o_cb.get_cb_checks().size());
   ASSERT_EQ(MAX_BRANCH_EVENTS_LEN/2, o_cb.get_cb_events().size());
   ASSERT_EQ(au1_aux_checks, o_cb.get_cb_checks());
   ASSERT_EQ(au1_aux_events, o_cb.get_cb_events());
}