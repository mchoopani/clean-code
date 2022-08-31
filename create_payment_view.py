@login_required
def create_payment(request):
    # currency=BTC&version=1&cmd=get_callback_address&key=your_api_public_key&format=json
    public_key = os.environ.get('PUBLIC_KEY')
    private_key = os.environ.get('PRIVATE_KEY')
    # get payment info
    if request.method != "POST":
        return JsonResponse()
    policy_id = request.POST.get('policy_id', '')
    currency = request.POST.get('currency')
    logger.debug(currency)
    policy = InsurancePolicy.objects.get(id=policy_id)
    try:
        payment = policy.payment_id
    except Exception as _:
        post_params = {
            'amount': policy.fee,
            'currency1': 'BTC',
            'currency2': currency,
            'buyer_email':
                request.user.email,
            'item_name': 'Policy for ' + policy.exchange.name,
            'item_number': policy.id
        }
        try:
            client = CryptoPayments(public_key, private_key)
            transaction = client.createTransaction(post_params)
            logger.debug(transaction)  # FOR DEBUG
            if len(transaction) == 0:
                raise Exception
        except Exception as e:
            logger.error(e)
            return JsonResponse({'error': True, 'message': 'Payment gateway is down'})

        try:
            try:
                payment = UserPayments(
                    status=0,
                    update_date=datetime.datetime.now(),
                    amount=transaction.amount,
                    address=transaction.address,
                    payment=transaction.txn_id,
                    confirms_needed=transaction.confirms_needed,
                    timeout=transaction.timeout,
                    status_url=transaction.status_url,
                    qrcode_url=transaction.qrcode_url,
                    currency=currency)

                try:
                    default_email = os.environ.get('DJANGO_EMAIL_DEFAULT_EMAIL')
                    subject = "Website: You’re one step away from being secured"
                    message = render_to_string('first_email.html', {'user': policy.user, 'payment': payment})
                    send_mail(subject, message, default_email, [policy.user.email])
                except Exception as e:
                    logger.error('Error on sending first email: ', e)

            except Exception as e:
                logger.error(e)
                responseData = {
                    'error': True,
                    'message': 'Payment Gateway Error'
                }
                return JsonResponse(responseData)
            else:
                payment.save()
                policy.payment_id = payment
                policy.save()

        except Exception as e:
            logger.error(e)
            return JsonResponse({
                'status': 'false',
                'message': "Error contacting with the Gateway"
            })
        else:
            post_params = post_params_function()
            response = JsonResponse(post_params)
            return response
    else:

        if payment.status == PaymentStatus.PENDING:
            logger.info('status Pending, do nothing')
            return JsonResponse(post_params)
        if payment.status == PaymentStatus.SUCCESS:
            logger.info('status Success')
            return JsonResponse(post_params)
        logger.info('status Error, should create new')
        post_params = {
            'amount': policy.fee,
            'currency1': 'BTC',
            'currency2': currency,
            'buyer_email':
                request.user.email,  # TODO set request.user.mail,
            'item_name': 'Policy for ' + policy.exchange.name,
            'item_number': policy.id
        }

        try:
            client = CryptoPayments(public_key, private_key)
            transaction = client.createTransaction(post_params)
        except Exception as e:
            logger.error(e)
            message = 'Payment gateway is down'
            responseData = {'error': True, 'message': message}
            return JsonResponse(responseData)

        try:
            payment = UserPayments(
                status=0,
                update_date=datetime.datetime.now(),
                amount=transaction.amount,
                address=transaction.address,
                payment=transaction.txn_id,
                confirms_needed=transaction.confirms_needed,
                timeout=transaction.timeout,
                status_url=transaction.status_url,
                qrcode_url=transaction.qrcode_url,
                currency=currency)
            payment.save()
            policy.payment_id = payment
            policy.save()

            default_email = os.environ.get('DJANGO_EMAIL_DEFAULT_EMAIL')
            subject = "Website: You’re one step away from being secured"
            message = render_to_string('first_email.html', {'user': policy.user, 'payment': payment})
            send_mail(subject, message, default_email, [policy.user.email])


        except Exception as e:
            message = "Error contacting with the Gateway"
            response = JsonResponse({
                'status': 'false',
                'message': message
            })
            response.status_code = 418
            logger.error(e)
            return response
        else:
            post_params = post_params_function()

            return JsonResponse(post_params)