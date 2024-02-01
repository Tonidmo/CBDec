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

#include "CBlib.h"

namespace CBlib
{
   ClosedBranch::ClosedBranch(void)
   {
      std::array<bool, MAX_CHECKS_BUFF> a_u1_aux_checks = {0};
      std::array<bool, MAX_EVENTS_BUFF> a_u1_aux_events = {0};

      m_a_u1_checks = a_u1_aux_checks;
      m_a_u1_events = a_u1_aux_events;
   }

   ClosedBranch::~ClosedBranch(void){};

   ECBStatus ClosedBranch::add_check_to_closed_branch(uint64_t const u64_new_check)
   {
      ECBStatus e_ret = E_CB_ERR_GENERIC;

      if (u64_new_check > MAX_CHECKS_BUFF)
      {
         ECBLIB_ERROR("Error (%d)!  Increment the maximum buffer size...", E_CB_ERR_INVAL);
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
            ECBLIB_DGB("Check already flipped for this closed branch");
         }

         e_ret = E_CB_OK;
      }

      return e_ret;
   }

   ECBStatus ClosedBranch::add_event_to_closed_branch(uint64_t const u64_new_event)
   {
      ECBStatus e_ret = E_CB_ERR_GENERIC;

      if (u64_new_event > MAX_EVENTS_BUFF)
      {
         ECBLIB_ERROR("Error (%d)! Increment the maximum buffer size...", E_CB_ERR_INVAL);
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