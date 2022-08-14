from bdb import effective
import datetime
from tkinter import CASCADE
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
        membership_type_str = self.membership_type if hasattr(self, 'membership_type') else ''
        if self.name > '':
            return '{}: {}'.format(membership_type_str, self.name)
        return membership_type_str

    class Meta:
        ordering = ['-is_quorum', 'membership_type', 'name']

class LocationCity(models.Model):

    name = models.CharField(
        'name',
        max_length=100
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'City or County'

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


class VotingAddress(models.Model):

    street_address = models.TextField(
        'street address',
        blank=True,
        help_text="The street address"
    )
    locationcity = models.ForeignKey(
        LocationCity,
        verbose_name="City or County",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text = "The person's city or county"
    )
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
    locationmagistrate = models.ForeignKey(
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

class NonDeletedPersonManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Person(models.Model):

    name_prefix = models.CharField(
        'prefix',
        blank=True,
        max_length=10,
        help_text="The person's name prefix or title"
    )
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
    name_suffix = models.CharField(
        'suffix',
        blank=True,
        max_length=10,
        help_text="The person's name suffix"
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
    positions = models.ManyToManyField(
        Position,
        blank=True,
        help_text="The person's position in the committee"
    )
    vb_voter_id = models.CharField(
        'voter file VANID',
        max_length=20,
        blank=True,
        help_text='The votebuilder "My Voters" van id'
    )
    vb_campaign_id = models.CharField(
        'campaign VANID',
        max_length=20,
        blank=True,
        help_text='The votebuilder "My Campaign" van id for this campaign or committee'
    )
    is_deleted = models.BooleanField(
        'is_deleted',
        default=False,
        help_text='If this object is soft-deleted'
    )

    class Meta:
        ordering = ['is_deleted', 'membership_status__is_quorum', 'name_last', 'name_first']

    def __str__(self):
        if(self.is_deleted):
            return '--deleted-- {} {}'.format(self.name_common if self.name_common else self.name_first, self.name_last)
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

    def delete(self):
        if(self.is_deleted):
            super().delete()
        else:
            self.is_deleted = True
            self.save()

    def is_user(self, user):
        return PersonUser.objects.filter(person=self, user=user).exists()

    objects = NonDeletedPersonManager()
    all_objects = models.Manager()

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

    def __str__(self):
        person = self.person if hasattr(self, 'person') else '<no person>'
        subcommittee = self.subcommittee if hasattr(self, 'subcommittee') else '<no subcommittee>'
        return '{} {} {}'.format(person, self.position, subcommittee)

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
    label = models.CharField(
        'label',
        max_length=50,
        blank=True,
        help_text="The label for this phone, such as \"Work\" or \"Home\""
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
        help_text="Extra texting instructions, such as 'Respond to challange after sending the text'"
    )
    alert = models.CharField(
        'alert',
        max_length=100,
        blank=True,
        help_text="Important information about texting, such as \"Don't text before 10:00am\""
    )

    def __str__(self):
        return self.number

    class Meta:
        ordering = ['-rank_number', 'number']

class ContactEmail(models.Model):

    person = models.ForeignKey(
        Person,
        on_delete = models.CASCADE,
        help_text="The person who is contaced with this number"
    )
    address = models.CharField(
        'address',
        max_length=250,
        help_text="The email address"
    )
    label = models.CharField(
        'label',
        max_length=50,
        blank=True,
        help_text="The label for this email account, such as \"Work\" or \"Home\""
    )
    rank_number = models.IntegerField(
        'rank',
        default=0,
        help_text="A number representing the placement of this email on a list in descending order (ex: if you want this one first, give it a high number like 1000)"
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

    def __str__(self):
        return self.address

    class Meta:
        ordering = ['-rank_number', 'address']

class Link(models.Model):

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        help_text="The person to whom this link applies"
    )
    title = models.CharField(
        'title',
        max_length=100,
        blank=True,
        help_text = "The title of this link"
    )
    href = models.URLField(
        'href',
        max_length=400,
        help_text="The link"
    )

    def __str__(self):
        person = self.person if hasattr(self, 'person') else '<no person>'
        return '%s: %s: %s' % (person, self.title, self.href)

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
        person = self.person if hasattr(self, 'person') else '<no person>'
        return '%s: %s %s' % (person, self.membership_status , self.effective_date)

class PositionHistory(models.Model):

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        help_text="The person to whom this membership applies"
    )
    position = models.ForeignKey(
        Position,
        on_delete = models.SET_NULL,
        null=True,
        help_text="The position for this period"
    )
    effective_date = models.DateField(
        'effective date',
        default = date.today,
        help_text="The starting date for this positon"
    )
    ending_date = models.DateField(
        'ending date',
        null=True,
        blank=True,
        help_text="The ending date for this positon"
    )

    def __str__(self):
        person = self.person if hasattr(self, 'person') else '<no person>'
        membership_status = self.membership_status if hasattr(self, 'membership_status') else '<no membership_status>'
        membership_type = self.membership_type if hasattr(self, 'membership_type') else '<no membership_type>'

        return '%s: %s %s %s'.format(person, membership_status , membership_type, self.effective_date)


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

    def __str__(self):
        person = self.person if hasattr(self, 'person') else '<no person>'
        return '%s %s' % (person, self.application_date)

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

    def __str__(self):
        person = self.person if hasattr(self, 'person') else '<no person>'
        return '%s %s %s' % (person, self.effective_date, self.method)


class EventType(models.Model):
    name = models.CharField(
        "Event Type",
        max_length=40,
        help_text='The name of the type of event'
    )
    rank_number = models.IntegerField(
        'rank',
        default=0,
        help_text="A number representing the placement of this event type on a list in ascending order (ex if you want this one first, give it a low number like 0)"
    )
    class Meta:
        ordering = ['rank_number']

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(
        "Event Name/Title",
        max_length=40,
        help_text='The name or title of event'
    )
    event_type = models.ForeignKey(
        EventType,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="The type of event"
    )
    when = models.DateField(
        "when",
        help_text = "The date of the event"
    )

    class Meta:
        ordering = ['-when']

    def __str__(self):
        return '%s: %s of %s' % (self.event_type, self.name, self.when)

class ParticipationLevel(models.Model):
    name = models.CharField(
        "Event Name/Title",
        max_length=40,
        help_text='The name or title of event'
    )
    action_name = models.CharField(
        'Action Name',
        max_length=60,
        help_text='An action phrase for this '
    )
    rank_number = models.IntegerField(
        'rank',
        default=0,
        help_text="A number representing the placement of this level on a list in ascending order (ex if you want this one first, give it a low number like 0)"
    )
    class Meta:
        ordering = ['rank_number']

    def __str__(self):
        return self.name

class Participation(models.Model):
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        help_text='The person who attended (or was otherwise associated with) the event',
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        help_text = 'The event that this person attended (or was othersize associated with)'
    )
    participation_level = models.ForeignKey(
        ParticipationLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text = 'The way in which this person is assocated with this event'
    )

    def __str__(self):
        person = self.person if hasattr(self, 'person') else '<no person>'
        action_phrase = self.participation_level.action_phrase if self.participation_level is not None else ''
        event = self.event if hasattr(self, 'event') else '<no event>'

        return '%s %s %s' % (person, action_phrase, event)

class PersonUser(models.Model):
    user=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="The user associated with the person"
    )
    person=models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        help_text="The person associated with the user"
    )
    def __str__(self):
        person = self.person if hasattr(self, 'person') else '<no person>'
        user = self.user if hasattr(self, 'user') else '<no user>'

        return '%s : %s' % (person, user)

class BulkRecordAction(models.Model):
    name = models.CharField(
        'bulk action name',
        max_length=100,
        blank=True,
        help_text='The name of the bulk action'
    )
    when = models.DateTimeField(
        'when',
        auto_now_add=True,
        help_text='The date this action occured'
    )

    def __str__(self):
        return f'{self.name} of {self.when}'

class RecordAction(models.Model):

    model_name = models.CharField(
        'model name',
        max_length=100,
        help_text='The name of the model for which this action applies'
    )
    object_name = models.CharField(
        'object name',
        max_length=100,
        blank=True,
        help_text='The name of the object to which this action applies'
    )
    when = models.DateTimeField(
        'when',
        auto_now_add=True,
        help_text='The date this change was made'
    )
    details = models.TextField(
        'details',
        help_text='The details of this action'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        help_text='The user who made this change'
    )
    bulk_recordact = models.ForeignKey(
        BulkRecordAction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The bulk action of which this record action is a part, such as a CSV Upload"
    )

    class Meta:
        ordering = ['-when',]

    def __str__(self):

        details_trunc = self.details[:97:]+'...' if len(self.details) > 100 else self.details
        when = self.when if self.when is not None else datetime.datetime.now()

        return f"{when.date().isoformat()} {self.object_name} {details_trunc}"

class RecordactPerson(models.Model):
    object = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        help_text = 'The person for which this action applies'
    )
    recordact = models.ForeignKey(
        RecordAction,
        on_delete=models.CASCADE,
        help_text='The recordaction which applies to this object'
    )

    def __str__(self):
        if hasattr(self, 'object') and hasattr(self, 'recordact'):
            return f'{self.object}: {self.recordact}'
        else:
            return '<uninitiated RecordactPeson>'

    class Meta:
        ordering = ('recordact',)

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
    # recordset_action = models.CharField(
    #     'recordset action',
    #     max_length=100,
    #     blank=True,
    #     help_text='A flag to be set for certain actions, such as a CSV Upload event'    
    # )

    class Meta:
        ordering = ['-when', 'modelname', 'objectid']

    def __str__(self):

        new_value_trunc = self.new_value[:17:]+'...' if len(self.new_value) > 20 else self.new_value
        when = self.when if self.when is not None else datetime.datetime.now()

        try:
            model = apps.get_model('sdcpeople', self.modelname)
            object = model.objects.get(pk=self.objectid)
            return f'{"mdy".format(when.strftime("%Y-%m-%d"))}: {self.modelname}: [{object}] [{self.fieldname}] changed to "{new_value_trunc}"'

        except Exception as e:
            print (e)

        return f'{"mdy".format(when.strftime("%Y-%m-%d"))}: {self.modelname}: {self.objectid} [{self.fieldname}] changed to "{new_value_trunc}"'

