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

#define  INITIAL_MEM_ALLOC   UINT16_MAX

namespace CBlib
{

   /********************************************************************************************************************
    * CLOSED BRANCH CLASS START
    *******************************************************************************************************************/
   ClosedBranch::ClosedBranch(void)
   {
      m_au1_checks = std::vector<bool>(INITIAL_MEM_ALLOC, false);
      m_au1_events = std::vector<bool>(INITIAL_MEM_ALLOC, false);
   }

   ClosedBranch::ClosedBranch(std::vector<bool> const & a_u1_checks, std::vector<bool> const & a_u1_events):
   m_au1_checks(a_u1_checks), m_au1_events(a_u1_events){};

   ClosedBranch::~ClosedBranch(void){}

   std::vector<bool> ClosedBranch::get_cb_checks(void) const
   {
      return this->m_au1_checks;
   }

   std::vector<bool> ClosedBranch::get_cb_events(void) const
   {
      return this->m_au1_events;
   }

   ECBStatus ClosedBranch::add_check_to_closed_branch(uint64_t const & u64_new_check)
   {
      ECBStatus e_ret = E_CB_ERR_GENERIC;

      if (u64_new_check > m_au1_checks.size())
      {
         CBLIB_ERROR("Error (%d)!  Increment the maximum buffer size...", E_CB_ERR_INVAL);
         e_ret = E_CB_ERR_INVAL;
      }
      else
      {
         if (m_au1_checks[u64_new_check] != 1U)
         {
            m_au1_checks[u64_new_check] = 1U;
         }
         else
         {
            CBLIB_DGB("Check already flipped for this closed branch");
         }

         e_ret = E_CB_OK;
      }

      return e_ret;
   }

   ECBStatus ClosedBranch::add_event_to_closed_branch(uint64_t const & u64_new_event)
   {
      ECBStatus e_ret = E_CB_ERR_GENERIC;

      if (u64_new_event > m_au1_events.size())
      {
         CBLIB_ERROR("Error (%d)! Increment the maximum buffer size...", E_CB_ERR_INVAL);
         e_ret = E_CB_ERR_INVAL;
      }
      else
      {
         m_au1_events[u64_new_event] = (1U + m_au1_events[u64_new_event]) % 2;
         e_ret = E_CB_OK;
      }

      return e_ret;
   }
   /********************************************************************************************************************
    * CLOSED BRANCH CLASS END
    *******************************************************************************************************************/



}