SELECT insurance_policy.id                                              AS Policy_number,
       insurance_policy.request_date                                    AS Policy_date,
       user_profile.first_name                                          AS First_name,
       user_profile.last_name                                           AS Last_name,
       user_profile.email                                               AS Email,
       insurance_policy.start_date                                      AS Start_date,
       insurance_policy.expiration_date                                 AS Expiration_date,
       insurance_policy.expiration_date - \ insurance_policy.start_date AS Number_of_days,
       crypto_exchange.name                                             AS Crypto_exchange_name,
       crypto_exchange.coverage_limit                                   AS Limit_BTC,
       insurance_policy.cover                                           AS Insured_Limit,
       insurance_policy.fee                                             AS Premium_paid,
       user_payments.amount                                             AS User_paid,
       user_payments.currency                                           AS User_currency,
       crypto_exchange.rate                                             AS Premium_rate,
       user_payments.update_date                                        AS Premium_payment_date,
       insurance_case.loss_value                                        AS Outstanding_claim_BTC,
       insurance_case.incident_date                                     AS Date_of_claim,
       insurance_case.refund_paid                                       AS Paid_claim_BTC,
       insurance_case.request_date                                      AS Date_of_claim_payment,
       insurance_policy.status                                          AS Insurance_policy_status,
       user_payments.status                                             AS User_payments_status,
       insurance_case.status                                            AS Insurance_case_status
FROM insurance_policy
         LEFT JOIN user_profile ON user_profile.id = \ insurance_policy.user
         LEFT JOIN crypto_exchange ON crypto_exchange.id = \ insurance_policy.exchange
         LEFT JOIN user_payments ON user_payments.id = \ insurance_policy.payment_id
         LEFT JOIN insurance_case ON \ insurance_case.insurance = insurance_policy.id