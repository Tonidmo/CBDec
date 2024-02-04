/***********************************************************************************************************************
 * @file    CBlib.cpp
 * @author  Imanol Etxezarreta (ietxezarretam@gmail.com)
 * 
 * @brief   This file implements the methods and operations that require or provides each of the classes defined in the 
 *          header file of the CBlib.
 * 
 * @version 0.1
 * @date    2024-01-31
 * 
 * @copyright Copyright (c) 2024
 * 
 **********************************************************************************************************************/

#include <cstring>
#include <algorithm>

#include "CBlib.h"

namespace CBlib
{
   ClosedBranch::ClosedBranch(void)
   {
      m_a_u1_checks.reserve(MAX_BRANCH_CHECKS_LEN);
      m_a_u1_events.reserve(MAX_BRANCH_EVENTS_LEN);

      memset(&m_a_u1_checks, 0, MAX_BRANCH_CHECKS_LEN);
      memset(&m_a_u1_events, 0, MAX_BRANCH_EVENTS_LEN);
   }

   ClosedBranch::ClosedBranch(std::vector<bool> const & a_u1_checks, std::vector<bool> const & a_u1_events)
   {
      if (MAX_BRANCH_CHECKS_LEN >= a_u1_checks.size())
      {
         m_a_u1_checks = a_u1_checks;
      }
      else
      {
         std::copy_n(a_u1_checks.begin(), MAX_BRANCH_CHECKS_LEN, m_a_u1_checks.begin());
         CBLIB_WARN("Possible information loss! Increase max buffer size...");
      }

      if (MAX_BRANCH_EVENTS_LEN >= a_u1_events.size())
      {
         m_a_u1_events = a_u1_events;
      }
      else
      {
         std::copy_n(a_u1_events.begin(), MAX_BRANCH_EVENTS_LEN, m_a_u1_events.begin());
         CBLIB_WARN("Possible information loss! Increase max buffer size...");
      }
   }

   ClosedBranch::~ClosedBranch(void)
   {
      memset(&m_a_u1_checks, 0, MAX_BRANCH_CHECKS_LEN);
      memset(&m_a_u1_events, 0, MAX_BRANCH_EVENTS_LEN);
   };

   ECBStatus ClosedBranch::add_check_to_closed_branch(uint64_t const u64_new_check)
   {
      ECBStatus e_ret = E_CB_ERR_GENERIC;

      if (u64_new_check > MAX_BRANCH_CHECKS_LEN)
      {
         CBLIB_ERROR("Error (%d)!  Increment the maximum buffer size...", E_CB_ERR_INVAL);
         e_ret = E_CB_ERR_INVAL;
      }
      else
      {
         if (m_a_u1_checks[u64_new_check] != 1)
         {
            m_a_u1_checks[u64_new_check] = 1;
         }
         else
         {
            CBLIB_DGB("Check already flipped for this closed branch");
         }

         e_ret = E_CB_OK;
      }

      return e_ret;
   }

   ECBStatus ClosedBranch::add_event_to_closed_branch(uint64_t const u64_new_event)
   {
      ECBStatus e_ret = E_CB_ERR_GENERIC;

      if (u64_new_event > MAX_BRANCH_EVENTS_LEN)
      {
         CBLIB_ERROR("Error (%d)! Increment the maximum buffer size...", E_CB_ERR_INVAL);
         e_ret = E_CB_ERR_INVAL;
      }
      else
      {
         m_a_u1_events[u64_new_event] = (1 + m_a_u1_events[u64_new_event]) % 2;
         e_ret = E_CB_OK;
      }

      return e_ret;
   }


}