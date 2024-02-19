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
   enum ECBLibStatus
   {
      E_CBL_OK                 =  0,    //!< Ok status, indicates correct operation.
      E_CBL_ERR                = -1,    //!< Generic error, for error types not defined specifically.
      E_CBL_ERR_INVAL          = -2,    //<! Input value error, the input value is not valid.
      E_CBL_ERR_SCHECK         = -3     //!< Error of an extra safety check, when flag EXTRA_SAFETY_CHECK is on.
   };

   class ClosedBranch
   {
      private:
         std::vector<bool> m_au1_checks;    //!< Member array of checks related to the closed branch
         std::vector<bool> m_au1_events;    //!< Member array of events related to the closed branch

      public:
         /**************************************************************************************************************
          * @brief Construct a new Closed Branch object. It initializes both checks and events arrays to zeroes.
          *************************************************************************************************************/
         ClosedBranch(void);

         /**************************************************************************************************************
          * @brief Construct a new Closed Branch object and initialized the members with the passed arguments.
          * 
          * @param checks[in]    Input array of checks.
          * @param events[in]    Input array of events.
          *************************************************************************************************************/
         ClosedBranch(std::vector<bool> const & checks, std::vector<bool> const & events);

         /**************************************************************************************************************
          * @brief Destroy the Closed Branch object.
          *************************************************************************************************************/
         ~ClosedBranch(void);

         /**************************************************************************************************************
          * @brief   Returns the member array of checks related to the closed branch.
          * 
          * @return std::vector<bool> Return vector of checks.
          *************************************************************************************************************/
         std::vector<bool> get_cb_checks(void) const;

         /**************************************************************************************************************
          * @brief   Returns the value of the specified index for the checks vector member.
          * 
          * @param u64_check_idx[in]   Index to look for in the vector.
          * @return bool[out]
          *************************************************************************************************************/
         bool get_cb_check_idx_value(uint64_t const & u64_check_idx) const;

         /**************************************************************************************************************
          * @brief   Returns the member array of events related to the closed branch.
          * 
          * @return std::vector<bool> Return vector of events.
          *************************************************************************************************************/
         std::vector<bool> get_cb_events(void) const;

         /**************************************************************************************************************
          * @brief   Returns the value of the specified index for the events vector member.
          * 
          * @param u64_event_idx[in]   Index to look for in the vector.
          * @return bool[out]
          *************************************************************************************************************/
         bool get_cb_event_idx_value(uint64_t const & u64_event_idx) const;

         /**************************************************************************************************************
          * @brief   Adds a check to the current closed branch object.
          * 
          * @param u64_new_check[in]   Index of the check.
          * 
          * @return ECBLibStatus Result of the operation:
          *                      - E_CBL_OK: successful operation.
          *                      - E_CBL_ERR: Generic error.
          *                      - E_CBL_ERR_INVAL: invalid input index.
          *                      - E_CBL_ERR_SCHECK: safety check not met.
          *************************************************************************************************************/
         ECBLibStatus add_check_to_closed_branch(uint64_t const & u64_new_check);

         /**************************************************************************************************************
          * @brief   Adds an event to the current closed branch object.
          * 
          * @param u64_new_event[in]   Index of the event.
          * 
          * @return ECBLibStatus Result of the operation:
          *                      - E_CBL_OK: successful operation.
          *                      - E_CBL_ERR: Generic error.
          *                      - E_CBL_ERR_INVAL: invalid input index.
          *************************************************************************************************************/
         ECBLibStatus add_event_to_closed_branch(uint64_t const & u64_new_event);
   };

   class Cluster
   {
      private:
         std::vector<bool> m_au1_clstr_checks;              //!< Member array of the checks related to the cluster
         std::vector<bool> m_au1_clstr_events;              //!< Member array of the events related to the cluster
         std::vector<ClosedBranch> m_ao_dest_grow_cbs;      //!< Member array of destructive growth Closed Branches 
                                                            //!< related to the cluster.
         std::vector<ClosedBranch> m_ao_non_dest_grow_cbs;  //!< Member array of non-destructive growth Closed Branches 
                                                            //!< related to the cluster.

      public:
         /**************************************************************************************************************
          * @brief   Default constructor of Cluster class. Initializes everything to 0.
          *************************************************************************************************************/
         Cluster(void);

         /**************************************************************************************************************
          * @brief   Construct a new Cluster object depending on the parameters given.
          * 
          * @param au1_checks[in]  Array of checks to associate to the cluster object.
          * @param au1_events[in]  Array of events to associate to the cluster object.
          * @param ao_ndes_cbs[in] Array of non-destructive closed branches to associate to the cluster.
          * @param ao_des_cbs[in]  Array of destructive closed branches to associate to the cluster.
          *************************************************************************************************************/
         Cluster(std::vector<bool> au1_checks,
                  std::vector<bool> au1_events,
                  std::vector<ClosedBranch> ao_dest_grow_cbs,
                  std::vector<ClosedBranch> ao_non_dest_grow_cbs);

         /**************************************************************************************************************
          * @brief Default destructor of the Cluster object.
          *************************************************************************************************************/
         ~Cluster(void);

         /**************************************************************************************************************
          * @brief   This routine adds a check into the cluster. The length of the input vector must be equal to the
          *          length of the vector member 'm_ao_clstr_checks'.
          * 
          * @todo Review this implementation for optimisation purposes... depending on the new_check imput parameter it
          *       could be optimised to have as parameter the index of the check to be included.
          * 
          * @param au1_new_check[in]   Input new check vector, to add to the cluster's checks.
          * 
          * @return ECBLibStatus Result of the operation:
          *                      - E_CBL_OK: successful operation.
          *                      - E_CBL_ERR: Generic error.
          *                      - E_CBL_ERR_INVAL: invalid input vector length.
          *                      - E_CBL_ERR_SCHECK: safety check not met.
          *************************************************************************************************************/
         ECBLibStatus add_check_to_cluster(std::vector<bool> const & au1_new_check);

         /**************************************************************************************************************
          * @brief   This routine adds an event into the cluster. The length of the input vector must be equal to the
          *          length of the vector member 'm_ao_clstr_events'.
          * 
          * @param au1_new_event[in]   Input new events vector, to add into the cluster.
          * 
          * @return ECBLibStatus Result of the operation:
          *                      - E_CBL_OK: successful operation.
          *                      - E_CBL_ERR: Generic error.
          *                      - E_CBL_ERR_INVAL: invalid input vector length.
          *************************************************************************************************************/
         ECBLibStatus add_event_to_cluster(std::vector<bool> const & au1_new_event);

         /**************************************************************************************************************
          * @brief   This routine checks whether the cluster's check at the given index is true or false.
          * 
          * @param u64_check[in]    Index of the cluster's check to be checked.
          * 
          * @return bool Result of the operation is:
          *                - True: if the check is already flipped.
          *                - False: if the check is not flipped.
          *************************************************************************************************************/
         bool check_if_check_in_cluster_cbs(uint64_t const & u64_check);

         /**************************************************************************************************************
          * @brief   This routine checks whether a check is deletable or not. The only deletable checks are the ones 
          *          related to closed branches that has been grown in a non-destructive manner.
          * 
          * @param u64_check[in]    Index of the check to assess if it is deletable.
          * 
          * @return bool Result of the operation is:
          *                - True: the check at the given index is deletable.
          *                - False: the check of the given index is not deletable.
          *************************************************************************************************************/
         bool deletable_check(uint64_t const & u64_check);

         /**************************************************************************************************************
          * @brief   This routine deletes a given check from the cluster.
          * 
          * @param u64_check[in]    Input check index to delete from cluster.
          * 
          * @return ECBLibStatus Result of the operation:
          *                      - E_CBL_OK: successful operation.
          *                      - E_CBL_ERR: Generic error.
          *                      - E_CBL_ERR_INVAL: invalid input vector length.
          *                      - E_CBL_ERR_SCHECK: safety check not met.
          *************************************************************************************************************/
         ECBLibStatus delete_closed_branch_from_cluster(uint64_t const & u64_check);

         /**************************************************************************************************************
          * @brief   This routine includes a ClosedBranch instance into the clusters ClosedBranch registries depending
          *          on the parameter 'u1_is_destructive' that indicates if the closed branch instance to add to the
          *          cluster has been grown in a non-destructive or destructive manner.
          * 
          * @param o_cb[in]               The closed branch instance to add to the cluster.
          * @param u1_is_destructive[in]  Flag to indicate whether the closed branch should go to the non-destructive
          *                               growth closed branch collection or to the destructive ones.
          *************************************************************************************************************/
         void include_closed_branch_to_cluster(ClosedBranch const & o_cb, bool u1_is_destructive);


   };
   
}

#endif // CBLIB_H_