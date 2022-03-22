from bdb import effective
from django.apps import apps
from xmlrpc.client import Boolean
from django.db import models
from django.forms import CharField
from datetime import date
from django.conf import settings

class MembershipType(models.Model):

    name = models.CharField(
        'name',
        max_length=100,
        help_text="The name of this membership type"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class MembershipStatus(models.Model):

    membership_type = models.ForeignKey(
        MembershipType,
        on_delete=models.CASCADE,
        help_text="The type of membership associated with this this status"
    )
    name = models.CharField(
        'name',
        blank=True,
        max_length=100,
        help_text="The name of this membership status"
    )
    is_member = models.BooleanField(
        'is member',
        default=False,
        help_text="If a persion with type and status counts as a members of the committee"
    )
    is_quorum = models.BooleanField(
        'is quorum',
        default=False,
        help_text="If a person with this type and status of membership is a quorum member)"
    )
    can_vote = models.BooleanField(
        'can vote',
        default=False,
        help_text="If a person with this type and status of membership can vote)"
    )
    pays_dues = models.BooleanField(
        'pays dues',
        default=False,
        help_text="If a person with this type and status of membership is expected to pay dues)"
    )

    def __str__(self):
        if self.name > '':
            return '{}: {}'.format(self.membership_type, self.name)
        return self.membership_type.name

    class Meta:
        ordering = ['-is_quorum', 'membership_type', 'name']

class LocationCongress(models.Model):

    name = models.CharField(
        'name',
        max_length=100
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Congressional District'

class LocationStateSenate(models.Model):

    name = models.CharField(
        'name',
        max_length=100

    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'State Senatorial District'

class LocationStateHouse(models.Model):

    name = models.CharField(
        'name',
        max_length=100
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'House of Delegates District'

class LocationMagistrate(models.Model):

    name = models.CharField(
        'name',
        max_length=100
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Magisterial District'

class LocationBorough(models.Model):

    name = models.CharField(
        'name',
        max_length=100
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Borough'

class LocationPrecinct(models.Model):

    name = models.CharField(
        'name',
        max_length=100
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Precinct'


class VotingAddress(models.Model):

    locationcongress = models.ForeignKey(
        LocationCongress,
        verbose_name="Congressional District",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text = "The person's congressional district"
    )
    locationstatesenate = models.ForeignKey(
        LocationStateSenate,
        verbose_name="State Senatorial District",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text = "The person's state senatorial district"
    )
    locationstatehouse = models.ForeignKey(
        LocationStateHouse,
        verbose_name="House of Delegates District",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text = "The person's house of delegates district"
    )
    locationmagestrate = models.ForeignKey(
        LocationMagistrate,
        verbose_name="Magisterial District",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text = "The person's magisterial district"
    )
    locationborough = models.ForeignKey(
        LocationBorough,
        verbose_name="Borough",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text = "The person's borough"
    )
    locationprecinct = models.ForeignKey(
        LocationPrecinct,
        verbose_name="Precinct",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text = "The person's precinct"
    )
    street_address = models.CharField(
        'street address',
        max_length=100,
        blank=True,
        help_text="The street address"
    )
    street_address = models.TextField(
        'street address',
        blank=True,
        help_text="The street address"
    )

    def __str__(self):
        return self.street_address[:50:]


class SubCommittee(models.Model):

    name = models.CharField(
        'name',
        max_length=100,
        help_text="The committee name"
    )
    rank_number = models.IntegerField(
        'rank',
        default=0,
        help_text="A number representing the placement of this committee on a list in descending order (ex if you want this one first, give it a high number like 1000)"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-rank_number', 'name']

class Person(models.Model):

    name_last = models.CharField(
        'last name',
        max_length=100,
        help_text="The person's last name"
    )
    name_first = models.CharField(
        'first name',
        max_length=100,
        blank=True,
        help_text = "The person's first name"
    )
    name_middles = models.CharField(
        'middle names',
        max_length=100,
        blank=True,
        help_text="The person's middle names"
    )
    name_common = models.CharField(
        'friendly name',
        max_length=100,
        blank=True,
        help_text = "The name that this person uses in place of a first name"
    )
    voting_address = models.ForeignKey(
        VotingAddress,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text = "The person's voting adress"
    )
    subcommittees = models.ManyToManyField(
        SubCommittee,
        through='SubMembership',
        help_text="The sub-committees in which this person is a member"
    )
    membership_status = models.ForeignKey(
        'MembershipStatus',
        null=True,
        on_delete=models.SET_NULL,
        help_text="The person's current membership"
    )

    class Meta:
        ordering = ('membership_status__is_quorum', 'name_last', 'name_first')

    def __str__(self):
        return '{} {}'.format(self.name_common if self.name_common else self.name_first, self.name_last)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        make_history = False
        if self.membership_status is not None:
            try:
                last_membership_history = MembershipHistory.objects.filter(person=self).latest('effective_date')
                if not last_membership_history.membership_status == self.membership_status:
                    make_history = True
            except MembershipHistory.DoesNotExist:
                make_history = True

        if make_history:
            MembershipHistory.objects.create(person=self, membership_status=self.membership_status, effective_date=date.today())

class Position(models.Model):

    title = models.CharField(
        'title',
        max_length=100,
        blank=True,
        help_text = "The title of this person's position"
    )
    rank_number = models.IntegerField(
        'rank',
        default=0,
        help_text="A number representing the placement of this position on a list in descending order (ex if you want this one first, give it a high number like 1000)"
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-rank_number', 'title']

class SubMembership(models.Model):

    person = models.ForeignKey(
        Person,
        on_delete = models.CASCADE,
        help_text = "The person who is a member of a subcommittee"
    )
    subcommittee = models.ForeignKey(
        SubCommittee,
        on_delete = models.CASCADE,
        help_text = "The committee in which the person is a member"
    )
    position = models.ForeignKey(
        Position,
        verbose_name='positon',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="The person's position on the committee"
    )

class ContactVoice(models.Model):

    person = models.ForeignKey(
        Person,
        on_delete = models.CASCADE,
        help_text="The person who is contaced with this number"
    )
    number = models.CharField(
        'number',
        max_length=50,
        help_text="The phone number"
    )
    label = models.CharField(
        'label',
        max_length=50,
        blank=True,
        help_text="The label for this phone, such as \"Work\" or \"Home\""
    )
    is_mobile = models.IntegerField(
        'is mobile',
        default=0,
        choices=[(0, ''),(1, 'Not Mobile'), (2, 'Mobile')],
        help_text="If this phone is mobile"
    )
    rank_number = models.IntegerField(
        'rank',
        default=0,
        help_text="A number representing the placement of this phone on a list in descending order (ex: if you want this one first, give it a high number like 1000)"
    )
    extra = models.CharField(
        'extra',
        max_length=100,
        blank=True,
        help_text="Extension or extra calling instructions, ex: 'ext 36', or 'ask for the sales manager'"
    )
    alert = models.CharField(
        'alert',
        max_length=100,
        blank=True,
        help_text="Important information about calling, such as \"Don't call before 10:00am\""
    )
    is_primary = models.BooleanField(
        'is primary',
        default=False,
        help_text="If this is the primary number for voice"
    )

    def __str__(self):
        return self.number

    class Meta:
        ordering = ['-rank_number', 'number']

class ContactText(models.Model):

    person = models.ForeignKey(
        Person,
        on_delete = models.CASCADE,
        help_text="The person who is contaced with this number"
    )

    number = models.CharField(
        'number',
        max_length=50,
        help_text="The phone number"
    )
    extra = models.CharField(
        'extra',
        max_length=100,
        blank=True,
        help_text="Extra texting instructions, such as 'Respond to challange after sending the text'"
    )
    alert = models.CharField(
        'alert',
        max_length=100,
        blank=True,
        help_text="Important information about texting, such as \"Don't text before 10:00am\""
    )
    is_primary = models.BooleanField(
        'is primary',
        default=False,
        help_text="If this is the primary number for text"
    )

class MembershipHistory(models.Model):

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        help_text="The person to whom this membership applies"
    )
    membership_status = models.ForeignKey(
        MembershipStatus,
        on_delete = models.SET_NULL,
        null=True,
        help_text="The status of membership for this period"
    )
    effective_date = models.DateField(
        'effective date',
        default = date.today,
        help_text="The starting date for this membership"
    )

    def __str__(self):
        return '{}: {} {} {}'.format(self.person, self.membership_status , self.membership_type, self.effective_date)


class MembershipApplication(models.Model):

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        help_text="The person to whom this membership applies"
    )
    application_date = models.DateField(
        'date of application',
        blank=True,
        null=True,
        help_text = "The date that the application was signed or submitted"
    )

class PaymentMethod(models.Model):
    name = models.CharField(
        'name',
        max_length=50,
        help_text = "The name of the method of payment"
    )

    def __str__(self):
        return self.name

class DuesPayment(models.Model):

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        help_text="The person to whom this membership applies"
    )
    transaction_date = models.DateField(
        'date of transaction',
        blank=True,
        null=True,
        help_text = "The date of the payment transaction"
    )
    effective_date = models.DateField(
        'date of transaction',
        blank=True,
        null=True,
        help_text = "The effective date of the payment"
    )
    method = models.ForeignKey(
        PaymentMethod,
        blank=True,
        null=True,
        on_delete = models.SET_NULL,
        help_text = "The method of payment"
    )

class History(models.Model):

    when = models.DateTimeField(
        'when',
        auto_now_add=True,
        help_text='The date this change was made'
    )
    modelname = models.CharField(
        'model',
        max_length=50,
        help_text='The model to which this change applies'
    )
    objectid = models.BigIntegerField(
        'object id',
        null=True,
        blank=True,
        help_text='The id of the record that was changed'
    )
    fieldname = models.CharField(
        'field',
        max_length=50,
        help_text='The that was changed',
    )
    old_value = models.TextField(
        'old value',
        blank=True,
        null=True,
        help_text='The value of the field before the change'
    )
    new_value = models.TextField(
        'new value',
        blank=True,
        help_text='The value of the field after the change'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        help_text='The user who made this change'
    )

    class Meta:
        ordering = ('-when', 'modelname', 'objectid')

    def __str__(self):

        new_value_trunc = self.new_value[:17:]+'...' if len(self.new_value) > 20 else self.new_value

        try:
            model = apps.get_model('sdcpeople', self.modelname)
            object = model.objects.get(pk=self.objectid)
            return f'{self.when.strftime("%Y-%m-%d")}: {self.modelname}: [{object}] [{self.fieldname}] changed to "{new_value_trunc}"'

        except Exception as e:
            print (e)

        return f'{"mdy".format(self.when.strftime("%Y-%m-%d"))}: {self.modelname}: {self.objectid} [{self.fieldname}] changed to "{new_value_trunc}"'
