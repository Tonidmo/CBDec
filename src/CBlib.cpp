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
#include <functional>

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
   m_au1_checks(a_u1_checks), m_au1_events(a_u1_events){}

   ClosedBranch::~ClosedBranch(void){}

   std::vector<bool> ClosedBranch::get_cb_checks(void) const
   {
      return this->m_au1_checks;
   }

   bool ClosedBranch::get_cb_check_idx_value(uint64_t const & u64_check_idx) const
   {
      bool u1_ret = false;
      if (u64_check_idx < m_au1_checks.size())
      {
         u1_ret = m_au1_checks[u64_check_idx];
      }

      return u1_ret;
   }

   std::vector<bool> ClosedBranch::get_cb_events(void) const
   {
      return this->m_au1_events;
   }

   bool ClosedBranch::get_cb_event_idx_value(uint64_t const & u64_event_idx) const
   {
      bool u1_ret = false;
      if (u64_event_idx < m_au1_events.size())
      {
         u1_ret = m_au1_events[u64_event_idx];
      }

      return u1_ret;
   }

   ECBLibStatus ClosedBranch::add_check_to_closed_branch(uint64_t const & u64_new_check)
   {
      ECBLibStatus e_ret = E_CBL_ERR;

      if (u64_new_check >= m_au1_checks.size())
      {
         CBLIB_ERROR("Error (%d)!  Index out of range...", E_CBL_ERR_INVAL);
         e_ret = E_CBL_ERR_INVAL;
      }
      #ifdef EXTRA_SAFETY_CHECKS
      else if (m_au1_checks[u64_new_check] != 1U)
      {
         CBLIB_DGB("Check already flipped for this closed branch");
         e_ret = E_CBL_ERR_SCHECK;
      }
      #endif
      else
      {
         m_au1_checks[u64_new_check] = 1U;
         e_ret = E_CBL_OK;
      }

      return e_ret;
   }

   ECBLibStatus ClosedBranch::add_event_to_closed_branch(uint64_t const & u64_new_event)
   {
      ECBLibStatus e_ret = E_CBL_ERR;

      if (u64_new_event >= m_au1_events.size())
      {
         CBLIB_ERROR("Error (%d)! Index out of range...", E_CBL_ERR_INVAL);
         e_ret = E_CBL_ERR_INVAL;
      }
      else
      {
         m_au1_events[u64_new_event] = (1U + m_au1_events[u64_new_event]) % 2;
         e_ret = E_CBL_OK;
      }

      return e_ret;
   }
   /********************************************************************************************************************
    * CLOSED BRANCH CLASS END
    *******************************************************************************************************************/

   /********************************************************************************************************************
    * CLUSTER CLASS START
    *******************************************************************************************************************/
   Cluster::Cluster(void)
   {
      m_au1_total_checks = std::vector<bool>(INITIAL_MEM_ALLOC, false);
      m_au1_total_events = std::vector<bool>(INITIAL_MEM_ALLOC, false);

      m_ao_dest_grow_cbs = std::vector<ClosedBranch>();
      m_ao_non_dest_grow_cbs = std::vector<ClosedBranch>();
   }

   Cluster::Cluster(std::vector<bool> au1_checks,
                     std::vector<bool> au1_events,
                     std::vector<ClosedBranch> ao_dest_grow_cbs,
                     std::vector<ClosedBranch> ao_non_dest_grow_cbs):
                     m_au1_total_checks(au1_checks),
                     m_au1_total_events(au1_events),
                     m_ao_dest_grow_cbs(ao_dest_grow_cbs),
                     m_ao_non_dest_grow_cbs(ao_non_dest_grow_cbs){}

   Cluster::~Cluster(void){}

   ECBLibStatus Cluster::add_check_to_cluster(std::vector<bool> const & au1_new_check)
   {
      ECBLibStatus e_ret = E_CBL_ERR;

      if (au1_new_check.size() != m_au1_total_checks.size())
      {
         e_ret = E_CBL_ERR_INVAL;
         CBLIB_ERROR("Error (%d)! Vector lengths must be equal for bitwise XOR operations...", e_ret);
      }
      #ifdef EXTRA_SAFETY_CHECKS
      else if (false == std::all_of(m_au1_total_checks.begin(), m_au1_total_checks.end(), [] (bool i){return i == 0;}))
      {
         e_ret = E_CBL_ERR_SCHECK;
         CBLIB_ERROR("Safety check (%d)! Check already flipped for this cluster...", e_ret);
      }
      #endif
      else
      {
         std::transform(m_au1_total_checks.begin(), m_au1_total_checks.end(), 
                        au1_new_check.begin(), m_au1_total_checks.begin(),
                        std::bit_xor<bool>());
         e_ret = E_CBL_OK;
      }

      return e_ret;
   }

   ECBLibStatus Cluster::add_event_to_cluster(std::vector<bool> const & au1_new_event)
   {
      ECBLibStatus e_ret = E_CBL_ERR;
      
      if (m_au1_total_events.size() != au1_new_event.size())
      {
         e_ret = E_CBL_ERR_INVAL;
         CBLIB_ERROR("Error (%d)! Vector lengths must be equal for bitwise XOR operations...", e_ret);
      }
      else
      {
         std::transform(m_au1_total_events.begin(), m_au1_total_events.end(), 
                        au1_new_event.begin(), m_au1_total_events.begin(),
                        std::bit_xor<bool>());
         e_ret = E_CBL_OK;
      }

      return e_ret;
   }

   bool Cluster::check_if_check_in_cluster_cbs(uint64_t const & u64_check)
   {
      bool u1_ret_val = false;

      if (u64_check >= m_au1_total_checks.size())
      {
         CBLIB_ERROR("Error (%d)! Index out of range... Returning false...", E_CBL_ERR_INVAL);
      }
      else
      {
         u1_ret_val = m_au1_total_checks[u64_check];
      }

      return u1_ret_val;
   }

   bool Cluster::deletable_check(uint64_t const & u64_check)
   {
      bool u1_ret_val = false;
      uint64_t u64_ndest_gr_cb_idx = m_ao_non_dest_grow_cbs.size();

      while(u64_ndest_gr_cb_idx > 0)
      {
         --u64_ndest_gr_cb_idx;
         if (true == m_ao_non_dest_grow_cbs[u64_ndest_gr_cb_idx].get_cb_check_idx_value(u64_check))
         {
            u1_ret_val = true;
            break;
         }
      }

      return u1_ret_val;
   }

   ECBLibStatus Cluster::delete_closed_branch_from_cluster(uint64_t const & u64_check)
   {
      ECBLibStatus e_ret = E_CBL_ERR;

      if (u64_check >= m_au1_total_checks.size())
      {
         e_ret = E_CBL_ERR_INVAL;
         CBLIB_ERROR("Error (%d)! Index out of range... Returning false...", e_ret);
      }
      #ifdef EXTRA_SAFETY_CHECKS
      else if (false == m_au1_total_checks[u64_check])
      {
         e_ret = E_CBL_ERR_SCHECK;
         CBLIB_ERROR("Safety check (%d)! Check not in the closed branch from the cluster.", e_ret);
      }
      #endif
      else
      {
         

      }

      return e_ret;
   }

   ECBLibStatus Cluster::include_closed_branch_to_cluster(ClosedBranch const & o_cb, bool u1_pc)
   {
      ECBLibStatus e_ret = E_CBL_ERR;
      (void) o_cb;
      (void) u1_pc;

      return e_ret;
   }
   /********************************************************************************************************************
    * CLUSTER CLASS END
    *******************************************************************************************************************/


}