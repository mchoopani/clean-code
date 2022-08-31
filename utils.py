## JSONIC: the decorator
class jsonic(object):

    def __init__(self, *decorargs, **deckeywords):
        self.deckeywords = deckeywords

    def __call__(self, fn):
        def jsoner(obj, **kwargs):
            dic = {}
            key = None
            thedic = None
            recurse_limit = 2
            thefields = obj._meta.get_all_field_names()
            kwargs.update(self.deckeywords)  # ??

            recurse = kwargs.get('recurse', 0)
            incl = kwargs.get('include')
            sk = kwargs.get('skip')
            if incl:
                if type(incl) == type([]):
                    thefields.extend(incl)
                else:
                    thefields.append(incl)
            if sk:
                if type(sk) == type([]):
                    for skipper in sk:
                        if skipper in thefields:
                            thefields.remove(skipper)
                else:
                    if sk in thefields:
                        thefields.remove(sk)

            ## first vanilla fields
            for f in thefields:
                try:
                    thedic = getattr(obj, "%s_set" % f)
                except AttributeError:
                    try:
                        thedic = getattr(obj, f)
                    except AttributeError:
                        pass
                    except ObjectDoesNotExist:
                        pass
                    else:
                        key = str(f)
                except ObjectDoesNotExist:
                    pass
                else:
                    key = "%s_set" % f

                if key:
                    if hasattr(thedic, "__class__") and hasattr(thedic, "all"):
                        if callable(thedic.all):
                            if hasattr(thedic.all(), "json"):
                                if recurse < recurse_limit:
                                    kwargs['recurse'] = recurse + 1
                                    dic[key] = thedic.all().json(**kwargs)
                    elif hasattr(thedic, "json"):
                        if recurse < recurse_limit:
                            kwargs['recurse'] = recurse + 1
                            dic[key] = thedic.json(**kwargs)
                    else:
                        try:
                            theuni = thedic.__str__()
                        except UnicodeEncodeError:
                            theuni = thedic.encode('utf-8')
                        dic[key] = theuni

            ## now, do we have imagekit stuff in there?
            if hasattr(obj, "_ik") and hasattr(obj, obj._ik.image_field)
                and hasattr(getattr(obj, obj._ik.image_field), 'size') and getattr(obj, obj._ik.image_field):
                for ikaccessor in [getattr(obj, s.access_as) for s in obj._ik.specs]:
                    key = ikaccessor.spec.access_as
                    dic[key] = {
                        'url': ikaccessor.url,
                        'width': ikaccessor.width,
                        'height': ikaccessor.height,
                    }

        return fn(obj, json=dic, **kwargs)

    return jsoner
