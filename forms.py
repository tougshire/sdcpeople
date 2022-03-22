from dataclasses import field
from .models import (
    ContactText,
    ContactVoice,
    DuesPayment,
    LocationBorough,
    LocationCongress,
    LocationMagistrate,
    LocationPrecinct,
    LocationStateHouse,
    LocationStateSenate,
    MembershipApplication,
    MembershipStatus,
    MembershipType,
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

class DuesPaymentForm(ModelForm):
    class Meta:
        model=DuesPayment
        fields = [
            'transaction_date',
            'effective_date',
            'method',
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
            'name_last',
            'name_first',
            'name_middles',
            'name_common',
            'voting_address',
            'membership_status',
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

PersonContactVoiceFormset = inlineformset_factory(Person, ContactVoice, form=ContactVoiceForm, extra=10)
PersonContactTextFormset = inlineformset_factory(Person, ContactText, form=ContactTextForm, extra=10)
PersonMembershipApplicationFormset = inlineformset_factory(Person, MembershipApplication, form=MembershipApplicationForm, extra=10)
PersonDuesPaymentFormset = inlineformset_factory(Person, DuesPayment, form=DuesPaymentForm, extra=10)
PersonSubMembershipFormset = inlineformset_factory(Person, SubMembership, form=SubMembershipForm, extra=10)
