@staff_member_required
def backup_to_csv(request):
    data = {}
    data['referral'] = ReferralPartner
    data['user'] = UserProfile
    data['exchange'] = CryptoExchange
    data['payments'] = UserPayments
    data['policy'] = InsurancePolicy
    data['case'] = InsuranceCase
    data['additional'] = AdditionalData
    cursor = connection.cursor()
    cursor.execute('''''')
    insurance_report = cursor.fetchall()

    if request.method == 'GET':
        datasets = {'referral': not bool(request.GET.get('referral')), 'user': not bool(request.GET.get('user')),
                    'exchange': not bool(request.GET.get('exchange')),
                    'payments': not bool(request.GET.get('payments')), 'policy': not bool(request.GET.get('policy')),
                    'case': not bool(request.GET.get('case')), 'additional': not bool(request.GET.get('additional'))}
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=backup.csv.zip'
        zip_file = zipfile.ZipFile(response, 'w')
        for key in datasets:
            if datasets[key] is True:
                output = StringIO()
                writer = csv.writer(output, dialect='excel')
                query = data[key].objects.all().values()
                if query.count() > 0:
                    keys = list(query[0])
                    writer.writerow(sorted(keys))
                    for row in query:
                        writer.writerow([row[k] for k in sorted(keys)])
                else:
                    writer.writerow(['NULL TABLE'])
                zip_file.writestr("%s.csv" % key, output.getvalue())

        out = StringIO()
        writer = csv.writer(out)
        header = [
            'Policy_number', 'Policy_date', 'Name', 'Surname', 'E-mail',
            'Policy_start_date', 'Policy_expiry_date', 'Number_of_days',
            'Crypto_exchange_name', 'Limit_BTC', 'Insured_Limit', 'Premium_paid_BTC',
            'User_paid', 'User_currency', 'Premium_rate_%',
            'Premium_payment_date', 'Outstanding_claim_BTC', 'Date_of_claim',
            'Paid_claim_BTC', 'Date_of_claim_payment',
            'Insurance_policy_status', 'User_payments_status',
            'Insurance_case_status'
        ]

        writer.writerow(header)
        for row in insurance_report:
            writer.writerow(row)
        zip_file.writestr("insurance_report.csv", out.getvalue())
        try:
            if not zip_file.testzip():
                responseData = {'error': True, 'message': 'Nothing to backup'}
                return JsonResponse(responseData)
        except Exception:
            return response
