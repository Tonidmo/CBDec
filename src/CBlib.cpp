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
      m_au1_clstr_checks = std::vector<bool>(INITIAL_MEM_ALLOC, false);
      m_au1_clstr_events = std::vector<bool>(INITIAL_MEM_ALLOC, false);

      m_ao_dest_grow_cbs = std::vector<ClosedBranch>();
      m_ao_non_dest_grow_cbs = std::vector<ClosedBranch>();
   }

   Cluster::Cluster(std::vector<bool> au1_checks,
                     std::vector<bool> au1_events,
                     std::vector<ClosedBranch> ao_dest_grow_cbs,
                     std::vector<ClosedBranch> ao_non_dest_grow_cbs):
                     m_au1_clstr_checks(au1_checks),
                     m_au1_clstr_events(au1_events),
                     m_ao_dest_grow_cbs(ao_dest_grow_cbs),
                     m_ao_non_dest_grow_cbs(ao_non_dest_grow_cbs){}

   Cluster::~Cluster(void){}

   ECBLibStatus Cluster::add_check_to_cluster(uint64_t const & u64_new_check)
   {
      ECBLibStatus e_ret = E_CBL_ERR;

      if (u64_new_check >= m_au1_clstr_checks.size())
      {
         e_ret = E_CBL_ERR_INVAL;
         CBLIB_ERROR("Error (%d)! Index out of range...", e_ret);
      }
      #ifdef EXTRA_SAFETY_CHECKS
      else if (true == m_au1_clstr_checks[u64_new_check])
      {
         e_ret = E_CBL_ERR_SCHECK;
         CBLIB_ERROR("Safety check (%d)! Check already flipped for this cluster...", e_ret);
      }
      #endif
      else
      {
         m_au1_clstr_checks[u64_new_check] = true;
         e_ret = E_CBL_OK;
      }

      return e_ret;
   }

   ECBLibStatus Cluster::add_event_to_cluster(uint64_t const & u64_new_event)
   {
      ECBLibStatus e_ret = E_CBL_ERR;
      
      if (u64_new_event >= m_au1_clstr_events.size())
      {
         e_ret = E_CBL_ERR_INVAL;
         CBLIB_ERROR("Error (%d)! Index out of range...", e_ret);
      }
      else
      {
         m_au1_clstr_events[u64_new_event] = 1;
         e_ret = E_CBL_OK;
      }

      return e_ret;
   }

   bool Cluster::check_if_check_in_cluster_cbs(uint64_t const & u64_check)
   {
      bool u1_ret_val = false;

      if (u64_check >= m_au1_clstr_checks.size())
      {
         CBLIB_ERROR("Error (%d)! Index out of range... Returning false...", E_CBL_ERR_INVAL);
      }
      else
      {
         u1_ret_val = m_au1_clstr_checks[u64_check];
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

      if (u64_check >= m_au1_clstr_checks.size())
      {
         e_ret = E_CBL_ERR_INVAL;
         CBLIB_ERROR("Error (%d)! Index out of range... Returning false...", e_ret);
      }
      #ifdef EXTRA_SAFETY_CHECKS
      else if (false == m_au1_clstr_checks[u64_check])
      {
         e_ret = E_CBL_ERR_SCHECK;
         CBLIB_ERROR("Safety check (%d)! Check not in the closed branch from the cluster.", e_ret);
      }
      #endif
      else
      {
         uint64_t u64_ndest_gr_cb_idx = m_ao_non_dest_grow_cbs.size();
         uint64_t u64_triggered_branch_idx = 0;
         uint16_t u16_triggered_count = 0;

         while (u64_ndest_gr_cb_idx > 0)
         {
            --u64_ndest_gr_cb_idx;
            ClosedBranch o_aux_cb = m_ao_non_dest_grow_cbs[u64_ndest_gr_cb_idx];
            if (true == o_aux_cb.get_cb_check_idx_value(u64_check))
            {
               u64_triggered_branch_idx = u64_ndest_gr_cb_idx;
               ++u16_triggered_count;
            }
         }

         if (1U == u16_triggered_count)
         {
            ClosedBranch o_triggered_cb = m_ao_non_dest_grow_cbs[u64_triggered_branch_idx];
            std::vector<bool> au1_triggered_cb_checks = o_triggered_cb.get_cb_checks();
            std::vector<bool> au1_triggered_cb_events = o_triggered_cb.get_cb_events();

            for (uint64_t u64_idx = 0; u64_idx < au1_triggered_cb_checks.size(); ++u64_idx)
            {
               if (true == au1_triggered_cb_checks[u64_idx])
               {
                  m_au1_clstr_checks[u64_idx] = false;
               }
            }

            for (uint64_t u64_idx = 0; u64_idx < au1_triggered_cb_events.size(); ++u64_idx)
            {
               if (true == au1_triggered_cb_events[u64_idx])
               {
                  m_au1_clstr_events[u64_idx] = (m_au1_clstr_events[u64_idx] + 1) % 2;
               }
            }

            m_ao_non_dest_grow_cbs.erase(m_ao_non_dest_grow_cbs.begin() + u64_triggered_branch_idx);
            e_ret = E_CBL_OK;
         }
         #ifdef EXTRA_SAFETY_CHECKS
         else
         {
            e_ret = E_CBL_ERR_SCHECK;
            CBLIB_ERROR("Safety check (%d)! There are more than one closed branch related to the same check.", e_ret);
         }
         #endif

      }

      return e_ret;
   }

   void Cluster::include_closed_branch_to_cluster(ClosedBranch const & o_cb, bool u1_is_destructive = false)
   {
      if (true == u1_is_destructive)
      {
         m_ao_dest_grow_cbs.push_back(o_cb);
      }
      else
      {
         m_ao_non_dest_grow_cbs.push_back(o_cb);
      }
   }
   /********************************************************************************************************************
    * CLUSTER CLASS END
    *******************************************************************************************************************/


}