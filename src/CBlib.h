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
            std::vector<bool> m_au1_checks;    //!< Member array of checks related to the closed branch
            std::vector<bool> m_au1_events;    //!< Member array of events related to the closed branch

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
             * @brief   Returns the member array of checks related to the closed branch.
             * 
             * @return std::vector<bool> Return vector of checks.
             **********************************************************************************************************/
            std::vector<bool> get_cb_checks(void) const;

            /***********************************************************************************************************
             * @brief   Returns the member array of events related to the closed branch.
             * 
             * @return std::vector<bool> Return vector of events.
             **********************************************************************************************************/
            std::vector<bool> get_cb_events(void) const;

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
         std::vector<bool> m_a_u1_total_checks;
         std::vector<bool> m_a_u1_total_events;

         std::vector<ClosedBranch> m_a_closed_branches_1;
         std::vector<ClosedBranch> m_a_closed_branches_2;

      public:
         Cluster(void);

         Cluster(std::vector<bool> a_u1_checks,
                  std::vector<bool> a_u1_events,
                  std::vector<ClosedBranch> a_o_cbs1,
                  std::vector<ClosedBranch> a_o_cbs2);

         ~Cluster(void);
   };
   
}

#endif // CBLIB_H_