IF(  Business_Group__r.BM_Cycle__r.Project__c = "KSEIP",  NULL ,
IF(ISPICKVAL( Why_Survey_Not_Completed__c , "Business has failed"), "Failed",
   IF (ISPICKVAL ( Why_Survey_Not_Completed__c, "Other"),"Red" ,
 (IF( ISPICKVAL( Visit_Number__c , "Post SB 1"),
         IF( OR(
                 (SB_Grant_Used__c / SB_Grant_Value__c) <= 0.5, Biz_Value__c  < SB_Grant_Value__c *0.5, ISPICKVAL(Of_BOs_Dropped__c, "2")
                ), "Red",
              IF( OR(
                    Proportion_SB_Used__c < 0.75, Biz_Value__c < SB_Grant_Value__c *0.75, ISPICKVAL(Of_BOs_Dropped__c, "1"),
                        (OR( 
                             ISPICKVAL( Records_Up_To_Date__c , "No"), ISPICKVAL( Records_Kept__c , "No"),ISPICKVAL( Records_Up_To_Date__c , "Unable to view business records")
                            ))), "Yellow",
                  IF( OR(
                        Proportion_SB_Used__c >= 0.75, Biz_Value__c >= SB_Grant_Value__c * 0.75
                        ), "Green", "ATTN Needed"
                     ))), 
   IF( ISPICKVAL( Visit_Number__c  , "Post SB 2"),
          IF( OR(
                   Biz_Value__c <  SB_Grant_Value__c  * 0.5,Biz_Profits__c <= 0, ISPICKVAL(Of_BOs_Dropped__c, "2")
                 ), "Red",
              IF( OR(
                      Biz_Value__c < SB_Grant_Value__c *0.75,
                     (Biz_Profits__c >= 0 && Biz_Profits__c < 0.1 * SB_Grant_Value__c ),
                      ISPICKVAL(Of_BOs_Dropped__c, "1"),
                        (OR( 
                             ISPICKVAL( Records_Up_To_Date__c , "No"), ISPICKVAL( Records_Kept__c , "No"),ISPICKVAL( Records_Up_To_Date__c , "Unable to view business records")
                            )
                         )
                     ), "Yellow", 
                   IF( 
                        Biz_Value__c >= SB_Grant_Value__c * 0.75 &&
                        Biz_Profits__c >= 0.1 * SB_Grant_Value__c &&
                        ISPICKVAL(BOs_Dropped__c, "No"
                      ), "Green", "ATTN Needed"
                      ))), 
   IF( 
       OR(ISPICKVAL( Visit_Number__c , "Business Exit"),
          ISPICKVAL( Visit_Number__c , "Post PR")),
           IF( OR(
                   Proportion_PR_Used__c  <= 0.5,
                   Biz_Value__c < (  SB_Grant_Value__c + PR_Grant_Value__c ) * 0.5,
                   Biz_Profits__c <=0 
                  ),"Red",
              IF( OR(
                       Proportion_PR_Used__c <= 0.75,
                       Biz_Value__c < ( SB_Grant_Value__c + PR_Grant_Value__c ) * 0.75,
                       Biz_Profits__c < 0.2* (SB_Grant_Value__c + PR_Grant_Value__c),
                       ISPICKVAL(BOs_Dropped__c, "Yes"),
                         (OR( 
                             ISPICKVAL( Records_Up_To_Date__c , "No"), ISPICKVAL( Records_Kept__c , "No"),ISPICKVAL( Records_Up_To_Date__c , "Unable to view business records")
                            ))), "Yellow", 
                  IF( 
                          Proportion_PR_Used__c >= 0.75 &&
                          Biz_Value__c >= (  SB_Grant_Value__c + PR_Grant_Value__c ) * 0.75 &&
                          Biz_Profits__c >=0.2 * (SB_Grant_Value__c+PR_Grant_Value__c) &&
                          ISPICKVAL(BOs_Dropped__c, "No"),
                      "Green", "ATTN Needed"
                    )))
      ,NULL                                         
)))))))