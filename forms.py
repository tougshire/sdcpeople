from cProfile import label
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from dataclasses import field
from os import link
from .models import (
    BulkCommunication,
    CommunicationEvent,
    ContactEmail,
    ContactText,
    ContactVoice,
    DuesPayment,
    Event,
    Link,
    ListMembership,
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
    PeopleList,
    Person,
    Position,
    SubCommittee,
    SubMembership,
    VotingAddress
)
from django import forms
#from django.forms import forms.ModelForm, forms.inlineformset_factory, Form

class ContactTextForm(forms.ModelForm):
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

class ContactVoiceForm(forms.ModelForm):
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

class ContactEmailForm(forms.ModelForm):
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


class DuesPaymentForm(forms.ModelForm):
    class Meta:
        model=DuesPayment
        fields = [
            'transaction_date',
            'effective_date',
            'method',
        ]

class EventForm(forms.ModelForm):
    class Meta:
        model=Event
        fields = [
            'name',
            'event_type',
            'when'
        ]

class CommunicationEventForm(forms.ModelForm):
    class Meta:
        model=CommunicationEvent
        fields = [
            "target",
            "volunteer",
            "details",
            "bulk_communication",
            "result",
        ]

class BulkCommunicationForm(forms.ModelForm):
    class Meta:
        model=BulkCommunication
        fields = [
            "name",
        ]

class LocationCityForm(forms.ModelForm):
    class Meta:
        model=LocationCity
        fields = [
            'name',
        ]


class LocationCongressForm(forms.ModelForm):
    class Meta:
        model=LocationCongress
        fields = [
            'name',
        ]

class LocationStateSenateForm(forms.ModelForm):
    class Meta:
        model=LocationStateSenate
        fields = [
            'name',
        ]

class LocationStateHouseForm(forms.ModelForm):
    class Meta:
        model=LocationStateHouse
        fields = [
            'name',
        ]

class LocationMagistrateForm(forms.ModelForm):
    class Meta:
        model=LocationMagistrate
        fields = [
            'name',
        ]

class LocationBoroughForm(forms.ModelForm):
    class Meta:
        model=LocationBorough
        fields = [
            'name',
        ]

class LocationPrecinctForm(forms.ModelForm):
    class Meta:
        model=LocationPrecinct
        fields = [
            'name',
        ]

class MembershipTypeForm(forms.ModelForm):
    class Meta:
        model=MembershipType
        fields = [
            'name',
        ]

class MembershipStatusForm(forms.ModelForm):
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

class VotingAddressForm(forms.ModelForm):
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

class SubCommitteeForm(forms.ModelForm):
    class Meta:
        model=SubCommittee
        fields = [
            'name',
            'rank_number',
        ]

class PeopleListForm(forms.ModelForm):
    class Meta:
        model=PeopleList
        fields = [
            'name',
        ]


class PersonForm(forms.ModelForm):
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

class LinkForm(forms.ModelForm):
    class Meta:
        model=Link
        fields = [
            'person',
            'title',
            'href',
        ]

class PositionForm(forms.ModelForm):
    class Meta:
        model=Position
        fields = [
            'title',
            'rank_number',
        ]

class SubMembershipForm(forms.ModelForm):
    class Meta:
        model=SubMembership
        fields = [
            'person',
            'subcommittee',
            'position',
        ]

class ListMembershipForm(forms.ModelForm):
    class Meta:
        model=ListMembership
        fields = [
            'person',
            'peoplelist',
        ]


class MembershipApplicationForm(forms.ModelForm):
    class Meta:
        model=MembershipApplication
        fields = [
            'application_date',
        ]

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model=PaymentMethod
        fields = [
            'name',
        ]

class ParticipationForm(forms.ModelForm):
    class Meta:
        model=Participation
        fields=[
            'person',
            'event',
            'participation_level',
        ]

def validate_file_single_chunk(file):
    
    if file.multiple_chunks():
        raise ValidationError("The file is too large to process")
    else:
        return file

class PersonCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="File:", help_text='The CSV file to upload', validators=[FileExtensionValidator( ['csv'] ), validate_file_single_chunk ])
    overwrite = forms.BooleanField(label="overwrite", required=False, help_text="Update record if the record is already in the database")

PersonContactVoiceFormset = forms.inlineformset_factory(Person, ContactVoice, form=ContactVoiceForm, extra=10)
PersonContactTextFormset = forms.inlineformset_factory(Person, ContactText, form=ContactTextForm, extra=10)
PersonContactEmailFormset = forms.inlineformset_factory(Person, ContactEmail, form=ContactEmailForm, extra=10)
PersonMembershipApplicationFormset = forms.inlineformset_factory(Person, MembershipApplication, form=MembershipApplicationForm, extra=10)
PersonDuesPaymentFormset = forms.inlineformset_factory(Person, DuesPayment, form=DuesPaymentForm, extra=10)
PersonSubMembershipFormset = forms.inlineformset_factory(Person, SubMembership, form=SubMembershipForm, extra=10)
PersonLinkFormset = forms.inlineformset_factory(Person, Link, form=LinkForm, extra=10)
PersonParticipationFormset = forms.inlineformset_factory(Person, Participation, form=ParticipationForm, extra=10)
PersonListMembershipFormset = forms.inlineformset_factory(Person, ListMembership, form=ListMembershipForm, extra=10)


EventParticipationFormset = forms.inlineformset_factory(Event, Participation, form=ParticipationForm, extra=10)

PeopleListListMembershipFormset = forms.inlineformset_factory(PeopleList, ListMembership, form=ListMembershipForm, extra=10)


SubCommitteeSubMembershipFormset = forms.inlineformset_factory(SubCommittee, SubMembership, form=SubMembershipForm, extra=10)
