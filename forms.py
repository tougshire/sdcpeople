from dataclasses import field
from os import link
from .models import (
    ContactEmail,
    ContactText,
    ContactVoice,
    DuesPayment,
    Event,
    Link,
    LocationCity,
    LocationBorough,
    LocationCongress,
    LocationMagistrate,
    LocationPrecinct,
    LocationStateHouse,
    LocationStateSenate,
    MembershipApplication,
    MembershipStatus,
    MembershipType,
    Participation,
    PaymentMethod,
    Person,
    Position,
    SubCommittee,
    SubMembership,
    VotingAddress
)
from django.forms import ModelForm, inlineformset_factory

class ContactTextForm(ModelForm):
    class Meta:
        model=ContactText
        fields = [
            'person',
            'number',
            'label',
            'extra',
            'alert',
            'rank_number',
        ]

class ContactVoiceForm(ModelForm):
    class Meta:
        model=ContactVoice
        fields = [
            'person',
            'number',
            'label',
            'is_mobile',
            'extra',
            'alert',
            'rank_number',
        ]

class ContactEmailForm(ModelForm):
    class Meta:
        model=ContactEmail
        fields = [
            'person',
            'address',
            'label',
            'extra',
            'alert',
            'rank_number',
        ]


class DuesPaymentForm(ModelForm):
    class Meta:
        model=DuesPayment
        fields = [
            'transaction_date',
            'effective_date',
            'method',
        ]

class EventForm(ModelForm):
    class Meta:
        model=Event
        fields = [
            'name',
            'event_type',
            'when'
        ]

class LocationCityForm(ModelForm):
    class Meta:
        model=LocationCity
        fields = [
            'name',
        ]


class LocationCongressForm(ModelForm):
    class Meta:
        model=LocationCongress
        fields = [
            'name',
        ]

class LocationStateSenateForm(ModelForm):
    class Meta:
        model=LocationStateSenate
        fields = [
            'name',
        ]

class LocationStateHouseForm(ModelForm):
    class Meta:
        model=LocationStateHouse
        fields = [
            'name',
        ]

class LocationMagistrateForm(ModelForm):
    class Meta:
        model=LocationMagistrate
        fields = [
            'name',
        ]

class LocationBoroughForm(ModelForm):
    class Meta:
        model=LocationBorough
        fields = [
            'name',
        ]

class LocationPrecinctForm(ModelForm):
    class Meta:
        model=LocationPrecinct
        fields = [
            'name',
        ]

class MembershipTypeForm(ModelForm):
    class Meta:
        model=MembershipType
        fields = [
            'name',
        ]

class MembershipStatusForm(ModelForm):
    class Meta:
        model=MembershipStatus
        fields = [
            'membership_type',
            'name',
            'can_vote',
            'is_member',
            'is_quorum',
            'pays_dues',
        ]

class VotingAddressForm(ModelForm):
    class Meta:
        model=VotingAddress
        fields = [
            'locationcity',
            'locationcongress',
            'locationstatesenate',
            'locationstatehouse',
            'locationmagistrate',
            'locationborough',
            'locationprecinct',
            'street_address',
        ]

class SubCommitteeForm(ModelForm):
    class Meta:
        model=SubCommittee
        fields = [
            'name',
            'rank_number',
        ]


class PersonForm(ModelForm):
    class Meta:
        model=Person
        fields = [
            'name_prefix',
            'name_last',
            'name_first',
            'name_middles',
            'name_common',
            'name_suffix',
            'voting_address',
            'membership_status',
            'positions',
            'vb_voter_id',
            'vb_campaign_id',
        ]

class LinkForm(ModelForm):
    class Meta:
        model=Link
        fields = [
            'person',
            'title',
            'href',
        ]

class PositionForm(ModelForm):
    class Meta:
        model=Position
        fields = [
            'title',
            'rank_number',
        ]

class SubMembershipForm(ModelForm):
    class Meta:
        model=SubMembership
        fields = [
            'person',
            'subcommittee',
            'position',
        ]

class MembershipApplicationForm(ModelForm):
    class Meta:
        model=MembershipApplication
        fields = [
            'application_date',
        ]

class PaymentMethodForm(ModelForm):
    class Meta:
        model=PaymentMethod
        fields = [
            'name',
        ]

class ParticipationForm(ModelForm):
    class Meta:
        model=Participation
        fields=[
            'person',
            'event',
            'participation_level',
        ]


PersonContactVoiceFormset = inlineformset_factory(Person, ContactVoice, form=ContactVoiceForm, extra=10)
PersonContactTextFormset = inlineformset_factory(Person, ContactText, form=ContactTextForm, extra=10)
PersonContactEmailFormset = inlineformset_factory(Person, ContactEmail, form=ContactEmailForm, extra=10)
PersonMembershipApplicationFormset = inlineformset_factory(Person, MembershipApplication, form=MembershipApplicationForm, extra=10)
PersonDuesPaymentFormset = inlineformset_factory(Person, DuesPayment, form=DuesPaymentForm, extra=10)
PersonSubMembershipFormset = inlineformset_factory(Person, SubMembership, form=SubMembershipForm, extra=10)
PersonLinkFormset = inlineformset_factory(Person, Link, form=LinkForm, extra=10)
PersonParticipationFormset = inlineformset_factory(Person, Participation, form=ParticipationForm, extra=10)

EventParticipationFormset = inlineformset_factory(Event, Participation, form=ParticipationForm, extra=10)

SubCommitteeSubMembershipFormset = inlineformset_factory(SubCommittee, SubMembership, form=SubMembershipForm, extra=10)
