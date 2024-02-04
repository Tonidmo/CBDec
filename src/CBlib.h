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

#ifndef CBLIB_H_
#define CBLIB_H_

#include <cstdio>
#include <cstdint>
#include <vector>

#include "CBlib_config.h"

#define CBLIB_ERROR(fmt, ...) {fflush(stderr); \
                                 fprintf(stderr, "[ECBLIB_ERROR] %s(%d): " fmt "\n", \
                                          __FUNCTION__, __LINE__, ## __VA_ARGS__); \
                                 fflush(stderr); \
                                 }

#define CBLIB_WARN(fmt, ...) {fflush(stdout); \
                                 fprintf(stdout, "[ECBLIB_WARNING] %s(%d): " fmt "\n", \
                                          __FUNCTION__, __LINE__, ## __VA_ARGS__); \
                                 fflush(stdout); \
                                 }

#ifdef DEBUG_CBLIB
#define CBLIB_DGB(fmt, ...) {fflush(stdout); \
                                 fprintf(stdout, "[ECBLIB_DGB] %s(%d): " fmt "\n", \
                                          __FUNCTION__, __LINE__, ## __VA_ARGS__); \
                                 fflush(stdout); \
                              }
#else 
#define CBLIB_DGB(...)
#endif

namespace CBlib
{
   /********************************************************************************************************************
    * @brief Enumeration that describes the status of the operations of the CBlib methods.
    *******************************************************************************************************************/
   enum ECBStatus
   {
      E_CB_OK           =  0,    //!< Ok status, indicates correct operation.
      E_CB_ERR_GENERIC  = -1,    //!< Generic error, for error types not defined specifically.
      E_CB_ERR_INVAL    = -2     //<! Input value error, the input value is not valid.
   };

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
             * @brief Construct a new Closed Branch object and initialized the members with the passed arguments.
             * 
             * @param checks[in]    Input array of checks.
             * @param events[in]    Input array of events.
             **********************************************************************************************************/
            ClosedBranch(std::vector<bool> const & checks, std::vector<bool> const & events);

            /***********************************************************************************************************
             * @brief Destroy the Closed Branch object.
             **********************************************************************************************************/
            ~ClosedBranch(void);

            /***********************************************************************************************************
             * @brief   Adds a check to the current closed branch object.
             * 
             * @param u64_new_check[in]   Index of the check.
             * 
             * @return ECBStatus Result of the operation:
             *                      - E_CB_OK: successful operation.
             *                      - E_CB_ERR_INVAL: invalid input index.
             *                      - E_CB_ERR_GENERIC: Generic error.
             **********************************************************************************************************/
            ECBStatus add_check_to_closed_branch(uint64_t const & u64_new_check);

            /***********************************************************************************************************
             * @brief   Adds an event to the current closed branch object.
             * 
             * @param u64_new_event[in]   Index of the event.
             * 
             * @return ECBStatus Result of the operation:
             *                      - E_CB_OK: successful operation.
             *                      - E_CB_ERR_INVAL: invalid input index.
             *                      - E_CB_ERR_GENERIC: Generic error.
             **********************************************************************************************************/
            ECBStatus add_event_to_closed_branch(uint64_t const & u64_new_event);
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

#endif // CBLIB_H_