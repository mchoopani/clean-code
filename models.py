class Payment(models.Model):
    is_paid = models.BooleanField(default=False)
    payment_agent = models.CharField(max_length=30)    

    def get_payment_agent(self):
        if not self.is_paid:
            return u"-"

        if self.payment_agent:
            return self.payment_agent

        if self.provider1.filter(type=1).count():
            self.payment_agent = u"Provider1"
        elif self.qprovider2.filter(type=1).count():
            self.payment_agent = u"AO Provider2"
        elif self.provider3.filter(type=1).count():
            self.payment_agent = u"Provider3"
        elif self.provider4.count():
            self.payment_agent = u"Complex Provider 4 Name With Surname"
        else:
            self.payment_agent = u"Provider5 Full Company-Name"

        self.save()
        return self.payment_agent
