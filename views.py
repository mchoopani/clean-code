from
import


@login_required
@transaction.commit_on_success
def create_w(request, id):
    if Register.objects.filter(id=id).exists() \
            and \
            Register.objects.get(id=id).sender == request.sender:
        return create_response([id], user_friendly=True)
    return HttpResponseRedirect("/")


def map_reduce_task(request, ids):
    registers = get_registers(request)
    ids = get_ids(ids)
    if not registers:
        return HttpResponseRedirect("/")

@csrf_protect
@login_required
def dashboard(request):
    user = get_object_or_404(
        UserProfile, django_user_id=request.user.id
    )  # django_user because we're searching in the registred users

    # check for referral user
    try:
        userPartner = Partner.objects.get(
            django_user=request.user.id)
        logger.info(
            "Partner: %s logged into system" % (userPartner))
        return account(request)
    except ObjectDoesNotExist:
        # handle case for regular user
        pass

    insurancy_policy_info = Policy.objects.order_by('-id').filter(
        user=user.id).exclude(status=PolicyStatus.DELETED)
    DEFAULT_VALUE = "NOT FOUND"
    PERIOD_NOT_IDENTIFIED = "NOT SET UNTIL PAYMENT DONE"
    PAYMENT_ERROR = "REPEAT PAYMENT"
    # NOTE: Getting every {'fee':value} pair so we could use it
    # while filling the form
    try:
        found_fee_values = insurancy_policy_info.values('fee')
    except Exception:
        logger.error("Fee values hasn't been found for user with ID: " +
                     str(user.id))
        found_fee_values = []

    fee_values = []
    for current_fee_json in found_fee_values:
        fee_values.append(current_fee_json)

    # NOTE: Getting every policy's numbers
    policy_numbers = []
    try:
        found_policy_numbers = insurancy_policy_info.values('id')
    except KeyError as error:
        logger.error("Policy number hasn't been found for user with ID: " +
                     str(user.id))
        found_policy_numbers = []

    for current_policy_number_json in found_policy_numbers:
        policy_numbers.append(current_policy_number_json)

    # NOTE: filling 'insurance period' form

    try:
        found_start_dates = insurancy_policy_info.values('start_date')
    except KeyError as _:
        logger.error("Couldn't find start dates for user with ID: " +
                     str(user.id))
        found_start_dates = []

    start_dates = []
    for current_date in found_start_dates:
        start_dates.append(current_date)

    try:
        found_expiration_dates = insurancy_policy_info.values(
            'expiration_date')
    except KeyError as _:
        logger.error("Couldn't find expirations dates for user with ID: " +
                     str(user.id))
        found_expiration_dates = []

    expiration_dates = []
    for current_date in found_expiration_dates:
        expiration_dates.append(current_date)

    # NOTE: filling 'Limit of liability' form
    try:
        found_limits_of_liability = insurancy_policy_info.values('cover_btc')
    except KeyError as _:
        logger.error("Couldn't find limits of liability for user with ID: " +
                     str(user.id))
        found_limits_of_liability = []

    limits_of_liability = []
    for current_limit in found_limits_of_liability:
        limits_of_liability.append(current_limit)

    # NOTE: filling 'date of formatting' form
    try:
        found_dates_of_formatting = insurancy_policy_info.values(
            'request_date')
    except KeyError as _:
        logger.error("Couldn't find dates of formatting for user with ID: " +
                     str(user.id))
        found_dates_of_formatting = []

    dates_of_formatting = []
    for current_date_of_formatting in found_dates_of_formatting:
        dates_of_formatting.append(current_date_of_formatting)

    # NOTE: filling "Crypto exchange" form
    try:
        found_stock_exchanges = insurancy_policy_info.values('exchange')
    except KeyError as error:
        logger.error("Couldn't find stock exchanges for user with ID: " +
                     str(user.id))
        found_stock_exchanges = []

    stock_exchange_ids = []
    for current_stock_exchange_id in found_stock_exchanges:
        stock_exchange_ids.append(current_stock_exchange_id)

    # NOTE: Filling "Status" form
    try:
        found_policy_statuses = insurancy_policy_info.values('status')
    except KeyError as _:
        logger.error("Couldn't find policy statuses for user with ID: " +
                     str(user.id))
        found_policy_statuses = []

    policy_statuses = []
    for policy_status in found_policy_statuses:
        policy_statuses.append(policy_status)

    contextPolicy = []
    for current_id, policy_id in enumerate(insurancy_policy_info):

        context_policy_number = DEFAULT_VALUE
        context_limit = DEFAULT_VALUE
        context_date_of_formatting = DEFAULT_VALUE
        context_insurance_period = PERIOD_NOT_IDENTIFIED
        context_fee = DEFAULT_VALUE
        context_stock_exchange = DEFAULT_VALUE

        # NOTE: filling policy number
        policy_number_tag = "Crypto"
        try:
            context_policy_number = policy_number_tag + \
                                    str((policy_numbers[current_id])['id'])
        except (IndexError, KeyError) as error:
            logger.error(
                "An error has occured while trying to get policy number.\
                Reason: " + str(error))

        # NOTE: filling 'Amount of premium' form
        try:
            context_fee = fee_values[current_id]['fee']
        except (IndexError, KeyError) as error:
            logger.error(
                "An error has occured while trying to get fee. Reason: " +
                str(error))

        # NOTE: filling 'insurane period' form
        try:
            s_date = start_dates[current_id]['start_date']
            e_date = expiration_dates[current_id]['expiration_date']
            context_insurance_period = '%s %s\'%s - %s %s\'%s' % (
                s_date.day, s_date.strftime("%B")[0:3], s_date.year - 2000,
                e_date.day, e_date.strftime("%B")[0:3], e_date.year - 2000)
        except (IndexError, KeyError, AttributeError) as error:
            if policy_id.payment_id and policy_id.payment_id.status < 0:
                context_insurance_period = PAYMENT_ERROR
                logger.error(
                    "An error has occured while trying to get insurane period.\
                    Reason: " + str(error))

        # NOTE: filling 'Limit of liability' form
        try:
            context_limit = limits_of_liability[current_id]['cover_btc']
        except (IndexError, KeyError) as error:
            logger.error(
                "An error has occured while trying to get limit . Reason: " +
                str(error))

        # NOTE: filling 'date of formatting' form
        try:
            context_date_of_formatting = str(
                dates_of_formatting[current_id]['request_date'].date())
        except (IndexError, KeyError, AttributeError) as error:
            logger.error(
                "An error has occured while trying to get date of formatting.\
                Reason: " + str(error))

        # NOTE: filling "Crypto exchange" form
        try:
            exchange_tag = CryptoExchange.objects.filter(id=stock_exchange_ids[
                current_id]['exchange']).values('name')[0]
            context_stock_exchange = exchange_tag['name']
        except (IndexError, KeyError) as error:
            logger.error(
                "An error has occured while trying to get exchange tag.\
                Reason: " + str(error))

        # NOTE: filling "policy status" form

        try:
            policy_status_numerical_value = policy_statuses[current_id][
                'status']
            policy_status_tag = get_policy_status_tag(
                policy_status_numerical_value)
        except (IndexError, KeyError) as error:
            logger.error(
                "An error has occured while trying to get policy status.\
                Reason: " + str(error))

        sos = False
        try:
            sosexists = InsuranceCase.objects.filter(
                insurance=(policy_numbers[current_id])['id'])
            logger.debug(sosexists.count())
            if sosexists.count() > 0:
                sos = True
        except (IndexError, KeyError) as error:
            logger.error(
                "An error has occured while trying to get InsuranceCase.\
                Reason: " + str(error))
        if start_dates[current_id]['start_date']:
            days = expiration_dates[current_id]['expiration_date'] - \
                   timezone.make_aware(
                       datetime.datetime.now())
            if policy_status_numerical_value == 2 and (
                    days < datetime.timedelta(days=10)):
                expired_soon = True
                days_left = int(
                    (expiration_dates[current_id]['expiration_date'] -
                     timezone.make_aware(datetime.datetime.now())).days) + 1
            else:
                expired_soon = False
                days_left = None
        else:
            expired_soon = False
            days_left = None

        context_policies = {
            'id': (policy_numbers[current_id])['id'],
            'policy_number':
                context_policy_number,
            'insurance_period':
                context_insurance_period,
            'limit':
                context_limit,
            'stock':
                context_stock_exchange,
            'formatting_date':
                context_date_of_formatting,
            'amount_of_premium':
                decimal.Decimal(context_fee).quantize(
                    decimal.Decimal('0.00000001'),
                    rounding=decimal.ROUND_DOWN).normalize(),
            'status':
                policy_status_tag,
            'numstatus':
                policy_status_numerical_value,
            'sosexists':
                sos,
            'expired_soon':
                expired_soon,
            'days_left':
                days_left
        }
        logger.debug(context_policies)
        contextPolicy.append(context_policies)

    stock_exchange_tags = set()
    for stock_exchange in stock_exchange_ids:
        current_stock_exchange = (CryptoExchange.objects.select_related(
        ).filter(id=stock_exchange['exchange']).values('name')[0])['name']
        stock_exchange_tags.add(current_stock_exchange)

    user_limit_information_context = []
    for stock_exchange in stock_exchange_tags:
        coverage_limit = (CryptoExchange.objects.select_related().filter(
            name=stock_exchange).values('coverage_limit')[0])['coverage_limit']
        current_stock_exchange = stock_exchange
        amount_of_holdings = 0
        for policy in contextPolicy:
            if policy['stock'] == current_stock_exchange and (
                    policy['numstatus'] == 1
                    or policy['numstatus'] == 2):  # BEFORE 2
                amount_of_holdings += float(policy['limit'])
        user_limit_information = {
            'stock_exchange': current_stock_exchange,
            'summary_of_holdings': amount_of_holdings,
            'coverage_limit': float(coverage_limit),
            'rate': int(amount_of_holdings / float(coverage_limit) * 100)
        }
        user_limit_information_context.append(user_limit_information)
        logger.debug(contextPolicy)
    context = {
        'USER_LIMIT_INFO': user_limit_information_context,
        'POLICIES': contextPolicy,
        'is_referral': False
    }
    return render(request, 'website/dashboard/dashboard.html', context)
