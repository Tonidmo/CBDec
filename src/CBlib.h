/***********************************************************************************************************************
 * @file    CBlib.h
 * @author  Imanol Etxezarreta (ietxezarretam@gmail.com)
 * 
 * @brief   This file contains the classes and interfaces that are provided by CBlib for handling branches, clusters and
 *          other important and computationally expensive operations in the Closed Branch Decoder.
 * 
 * @version 0.1
 * @date    2024-01-31
 * 
 * @copyright Copyright (c) 2024
 * 
 **********************************************************************************************************************/

#include <cstdint>
#include <vector>

#include "CBlib_config.h"

namespace CBlib
{
   class ClosedBranch
   {
         private:
            std::vector<bool> m_a_u1_checks;
            std::vector<bool> m_a_u1_events;

         public:
            /***********************************************************************************************************
             * @brief Construct a new Closed Branch object. It initializes both checks and events arrays to zeroes.
             **********************************************************************************************************/
            ClosedBranch(void);

            /***********************************************************************************************************
             * @brief Destroy the Closed Branch object.
             **********************************************************************************************************/
            ~ClosedBranch(void);

            void add_check_to_closed_branch(uint64_t const u64_new_check);

            void add_event_to_closed_branch(uint64_t const u64_new_event);
   };

   class Cluster
   {
      private:
         /* data */
      public:
         Cluster(/* args */);
         ~Cluster();
   };
   
}