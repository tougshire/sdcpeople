import sys
import urllib
import csv
from urllib.parse import urlencode
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.http import QueryDict
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django.views.generic.list import ListView
from tougshire_vistas.models import Vista
from tougshire_vistas.views import (default_vista, delete_vista,
                                    get_global_vista, get_latest_vista,
                                    make_vista, retrieve_vista,
                                    vista_context_data, make_vista_fields)

from .forms import (EventForm, EventParticipationFormset, LocationBoroughForm, LocationCityForm, LocationCongressForm,
                    LocationPrecinctForm, LocationStateHouseForm,
                    LocationStateSenateForm, ParticipationForm, PersonContactEmailFormset,
                    PersonContactTextFormset, PersonContactVoiceFormset,
                    PersonDuesPaymentFormset, PersonForm, PersonLinkFormset,
                    PersonMembershipApplicationFormset, PersonParticipationFormset,
                    PersonSubMembershipFormset, SubCommitteeForm, SubCommitteeSubMembershipFormset, VotingAddressForm)
from .models import (ContactText, ContactVoice, Event, History, LocationBorough,LocationCity,
                     LocationCongress, LocationMagistrate, LocationPrecinct,
                     LocationStateHouse, LocationStateSenate, MembershipStatus, Participation,
                     Person, PersonUser, Position, SubCommittee, SubMembership, VotingAddress)


def update_history(form, modelname, object, user):
    for fieldname in form.changed_data:
        try:
            old_value=str(form.initial[fieldname]),
        except KeyError:
            old_value=None

        history = History.objects.create(
            user=user,
            modelname=modelname,
            objectid=object.pk,
            fieldname=fieldname,
            old_value=old_value,
            new_value=str(form.cleaned_data[fieldname])
        )

        history.save()

class PersonCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'sdcpeople.add_person'
    model = Person
    form_class = PersonForm

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        if self.request.POST:
            context_data['participations'] = PersonContactVoiceFormset(self.request.POST)
            context_data['contacttexts'] = PersonContactTextFormset(self.request.POST)
            context_data['contactemails'] = PersonContactEmailFormset(self.request.POST)
            context_data['membershipapplications'] = PersonMembershipApplicationFormset(self.request.POST)
            context_data['submemberships'] = PersonSubMembershipFormset(self.request.POST )
            context_data['duespayments'] = PersonDuesPaymentFormset(self.request.POST)
            context_data['links'] = PersonLinkFormset(self.request.POST)
            context_data['participatins'] = PersonParticipationFormset(self.request.POST)

        else:
            context_data['participations'] = PersonContactVoiceFormset()
            context_data['contacttexts'] = PersonContactTextFormset()
            context_data['contactemails'] = PersonContactEmailFormset()
            context_data['membershipapplications'] = PersonMembershipApplicationFormset()
            context_data['submemberships'] = PersonSubMembershipFormset()
            context_data['duespayments'] = PersonDuesPaymentFormset()
            context_data['links'] = PersonLinkFormset()
            context_data['participations'] = PersonParticipationFormset()

        return context_data

    def form_valid(self, form):

        response = super().form_valid(form)

        update_history(form, 'Person', form.instance, self.request.user)

        self.object = form.save()

        formset_data = {
            'participations':PersonContactVoiceFormset( self.request.POST, instance=self.object ),
            'contacttexts':PersonContactTextFormset( self.request.POST, instance=self.object ),
            'contactemails':PersonContactEmailFormset( self.request.POST, instance=self.object ),
            'membershipapplications':PersonMembershipApplicationFormset( self.request.POST, instance=self.object ),
            'submemberships':PersonSubMembershipFormset(self.request.POST, instance=self.object ),
            'duespayments':PersonDuesPaymentFormset( self.request.POST, instance=self.object ),
            'links':PersonLinkFormset( self.request.POST, instance=self.object ),
            'participations':PersonParticipationFormset( self.request.POST, instance=self.object ),

        }

        for formset_name in formset_data.keys():

            if(formset_data[formset_name]).is_valid():
                formset_data[formset_name].save()
            else:
                messages.add_message(self.request, messages.WARNING, 'There was a problem with ' + formset_name + ', ' + formset_name + ' was not saved')
                print('error saving ' + formset_name + ': ' )
                print(formset_data[formset_name].errors)

        return response

    def get_success_url(self):

        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:person-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:person-detail', kwargs={'pk': self.object.pk})

class PersonUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'sdcpeople.change_person'
    model = Person
    form_class = PersonForm

    def has_permission(self):
        return super().has_permission() or PersonUser.objects.filter(user=self.request.user, person=self.get_object()).exists()

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        if self.request.POST:
            context_data['participations'] = PersonContactVoiceFormset(self.request.POST, instance=self.object )
            context_data['contacttexts'] = PersonContactTextFormset(self.request.POST, instance=self.object )
            context_data['contactemails'] = PersonContactEmailFormset(self.request.POST, instance=self.object )
            context_data['membershipapplications'] = PersonMembershipApplicationFormset(self.request.POST, instance=self.object )
            context_data['submemberships'] = PersonSubMembershipFormset(self.request.POST, instance=self.object )
            context_data['duespayments'] = PersonDuesPaymentFormset(self.request.POST, instance=self.object )
            context_data['links'] = PersonLinkFormset(self.request.POST, instance=self.object )
            context_data['participations]'] = PersonParticipationFormset(self.request.POST, instance=self.object )

        else:
            context_data['participations'] = PersonContactVoiceFormset( instance=self.object )
            context_data['contacttexts'] = PersonContactTextFormset( instance=self.object )
            context_data['contactemails'] = PersonContactEmailFormset( instance=self.object )
            context_data['membershipapplications'] = PersonMembershipApplicationFormset( instance=self.object )
            context_data['submemberships'] = PersonSubMembershipFormset( instance=self.object )
            context_data['duespayments'] = PersonDuesPaymentFormset( instance=self.object )
            context_data['links'] = PersonLinkFormset( instance=self.object )
            context_data['participations'] = PersonParticipationFormset( instance=self.object )

        return context_data

    def form_valid(self, form):

        update_history(form, 'Person', form.instance, self.request.user)

        response = super().form_valid(form)

        self.object = form.save()

        formset_data = {
            'participations':PersonContactVoiceFormset( self.request.POST, instance=self.object ),
            'contacttexts':PersonContactTextFormset( self.request.POST, instance=self.object ),
            'contactemails':PersonContactEmailFormset( self.request.POST, instance=self.object ),
            'membershipapplications':PersonMembershipApplicationFormset( self.request.POST, instance=self.object ),
            'submemberships':PersonSubMembershipFormset(self.request.POST, instance=self.object ),
            'duespayments':PersonDuesPaymentFormset( self.request.POST, instance=self.object ),
            'links':PersonLinkFormset( self.request.POST, instance=self.object ),
            'participations':PersonParticipationFormset( self.request.POST, instance=self.object ),

        }

        for formset_name in formset_data.keys():

            if(formset_data[formset_name]).is_valid():
                formset_data[formset_name].save()
            else:
                messages.add_message(self.request, messages.WARNING, 'There was a problem with ' + formset_name + ', ' + formset_name + ' was not saved')
                print('error saving ' + formset_name + ': ')
                print(formset_data[formset_name].errors)

        return response


    def get_success_url(self):
        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:person-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:person-detail', kwargs={'pk': self.object.pk})

class PersonDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_person'
    model = Person

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['person_labels'] = { field.name: field.verbose_name.title() for field in Person._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
        context_data['voting_address_labels'] = { field.name: field.verbose_name.title() for field in VotingAddress._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        context_data['is_this_user'] = PersonUser.objects.filter(user=self.request.user, person=self.get_object()).exists()

        return context_data


class PersonDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'sdcpeople.delete_person'
    model = Person
    template_name = 'sdcpeople/person_confirm_delete.html'
    success_url = reverse_lazy('sdcpeople:person-list')

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['person_labels'] = { field.name: field.verbose_name.title() for field in Person._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
        context_data['voting_address_labels'] = { field.name: field.verbose_name.title() for field in VotingAddress._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data


class PersonList(PermissionRequiredMixin, ListView):
    permission_required = 'sdcpeople.view_person'
    model = Person
    paginate_by = 30

    def setup(self, request, *args, **kwargs):

        self.vista_settings={
            'max_search_keys':5,
            'fields':[],
        }

        self.vista_settings['fields'] = make_vista_fields(Person, field_names=[
            'name_prefix',
            'name_last',
            'name_first',
            'name_middles',
            'name_common',
            'name_suffix',
            'voting_address',
            'subcommittees',
            'membership_status',
            'membership_status__is_member',
            'membership_status__is_quorum',
            'positions',
            'is_deleted',
            'participation__event',
        ])

        self.vista_settings['fields']['participation__event']['label']="Participation in Event"

        self.vista_defaults = QueryDict(urlencode([
            ('filter__fieldname__0', ['membership_status__is_member']),
            ('filter__op__0', ['exact']),
            ('filter__value__0', ['True']),
            ('order_by', ['name_last', 'name_common', ]),
            ('paginate_by',self.paginate_by),
        ],doseq=True) )

        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self, **kwargs):

        queryset = super().get_queryset()

        self.vistaobj = {'querydict':QueryDict(), 'queryset':queryset}

        if 'delete_vista' in self.request.POST:
            delete_vista(self.request)

        if 'query' in self.request.session:
            print('tp 224bc49', 'query in self.request.session')
            querydict = QueryDict(self.request.session.get('query'))
            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                querydict,
                '',
                False,
                self.vista_settings
            )
            del self.request.session['query']

        elif 'vista_query_submitted' in self.request.POST:
            print('tp 224bc50', 'vista_query_submitted')

            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                self.request.POST,
                self.request.POST.get('vista_name') if 'vista_name' in self.request.POST else '',
                self.request.POST.get('make_default') if ('make_default') in self.request.POST else False,
                self.vista_settings
            )
        elif 'retrieve_vista' in self.request.POST:
            print('tp 224bc51', 'retrieve_vista')

            self.vistaobj = retrieve_vista(
                self.request.user,
                queryset,
                'sdcpeople.person',
                self.request.POST.get('vista_name'),
                self.vista_settings

            )
        elif 'default_vista' in self.request.POST:
            print('tp 224bc52', 'default_vista')

            self.vistaobj = default_vista(
                self.request.user,
                queryset,
                self.vista_defaults,
                self.vista_settings
            )
        else:
            self.vistaobj = get_latest_vista(
                self.request.user,
                queryset,
                self.vista_defaults,
                self.vista_settings
            )

        return self.vistaobj['queryset']

    def get_paginate_by(self, queryset):

        if 'paginate_by' in self.vistaobj['querydict'] and self.vistaobj['querydict']['paginate_by']:
            return self.vistaobj['querydict']['paginate_by']

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        vista_data = vista_context_data(self.vista_settings, self.vistaobj['querydict'])

        context_data = {**context_data, **vista_data}

        context_data['vistas'] = Vista.objects.filter(user=self.request.user, model_name='libtekin.item').all() # for choosing saved vistas

        if self.request.POST.get('vista_name'):
            context_data['vista_name'] = self.request.POST.get('vista_name')

        context_data['count'] = self.object_list.count()

        return context_data

class PersonCSV(PersonList):

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="sdcvirginia_people.csv"'},
        )

        writer = csv.writer(response)
        vista_data = vista_context_data(self.vista_settings, self.vistaobj['querydict'])

        row=[]

        if not 'show_columns' in vista_data or 'name_last' in vista_data['show_columns']:
            row.append(context["labels"]["name_last"])
        if not 'show_columns' in vista_data or 'name_first' in vista_data['show_columns']:
            row.append(context["labels"]["name_first"])
        if not 'show_columns' in vista_data or 'is_quorum' in vista_data['show_columns']:
            row.append("Quorum")
        if not 'show_columns' in vista_data or 'membership_status' in vista_data['show_columns']:
            row.append(context["labels"]["membership_status"])
        if not 'show_columns' in vista_data or 'positions' in vista_data['show_columns']:
            row.append("Positions")
        if not 'show_columns' in vista_data or 'submemberships' in vista_data['show_columns']:
            row.append("SubCommittees")
        if not 'show_columns' in vista_data or 'contactvoice' in vista_data['show_columns']:
            row.append("Voice")
        if not 'show_columns' in vista_data or 'contacttext' in vista_data['show_columns']:
            row.append("Text")
        if not 'show_columns' in vista_data or 'contacemail' in vista_data['show_columns']:
            row.append("Email")
        if not 'show_columns' in vista_data or 'voting_address' in vista_data['show_columns']:
            row.append("voting address")
        if not 'show_columns' in vista_data or 'voting_address.locationcity' in vista_data['show_columns']:
            row.append("City")
        if not 'show_columns' in vista_data or 'voting_address.locationcongress' in vista_data['show_columns']:
            row.append("Congress")
        if not 'show_columns' in vista_data or 'voting_address.locationstatesenate' in vista_data['show_columns']:
            row.append("Senate")
        if not 'show_columns' in vista_data or 'voting_address.locationstatehouse' in vista_data['show_columns']:
            row.append("house")
        if not 'show_columns' in vista_data or 'voting_address.locationmagistrate' in vista_data['show_columns']:
            row.append("Magistrate")
        if not 'show_columns' in vista_data or 'voting_address.locationborough' in vista_data['show_columns']:
            row.append("Borough")
        if not 'show_columns' in vista_data or 'voting_address.locationprecinct' in vista_data['show_columns']:
            row.append("precinct")

        writer.writerow(row)

        for object in self.object_list:

            row=[]

            if not 'show_columns' in vista_data or 'name_last' in vista_data['show_columns']:
                row.append(object.name_last)
            if not 'show_columns' in vista_data or 'name_first' in vista_data['show_columns']:
                row.append(object.name_first)
            if not 'show_columns' in vista_data or 'is_quorum' in vista_data['show_columns']:
                row.append(object.membership_status.is_quorum)
            if not 'show_columns' in vista_data or 'membership_status' in vista_data['show_columns']:
                row.append(object.membership_status)
            if not 'show_columns' in vista_data or 'positions' in vista_data['show_columns']:
                positions=''
                if object.positions.all().exists():
                    for position in object.positions.all():
                        positions = positions + position.title + ', '
                    positions = positions[:-2]
                row.append(positions)
            if not 'show_columns' in vista_data or 'submemberships' in vista_data['show_columns']:
                submemberships=''
                if object.submembership_set.all().exists():
                    for submembership in object.submembership_set.all():
                        submemberships = submemberships + str(submembership.subcommittee) + ', '
                    submemberships=submemberships[:-2]
                row.append(submemberships)
            if not 'show_columns' in vista_data or 'contactvoice' in vista_data['show_columns']:
                contactvoices=''
                if object.contactvoice_set.all().exists():
                    for contactvoice in object.contactvoice_set.all():
                        contactvoices = contactvoices + str(contactvoice.number) + ', '
                    contactvoices=contactvoices[:-2]
                row.append(contactvoices)
            if not 'show_columns' in vista_data or 'contacttext' in vista_data['show_columns']:
                contacttexts=''
                if object.contacttext_set.all().exists():
                    for contacttext in object.contacttext_set.all():
                        contacttexts = contacttexts + str(contacttext.number) + ', '
                    contacttexts=contacttexts[:-2]
                row.append(contacttexts)
            if not 'show_columns' in vista_data or 'contacemail' in vista_data['show_columns']:
                contactemails=''
                if object.contactemail_set.all().exists():
                    for contactemail in object.contactemail_set.all():
                        contactemails = contactemails + str(contactemail.address) + ', '
                    contactemails=contactemails[:-2]
                row.append(contactemails)
            if object.voting_address is not None:
                if not 'show_columns' in vista_data or 'voting_address' in vista_data['show_columns']:
                    row.append(str(object.voting_address).replace("\n", " "))
                if not 'show_columns' in vista_data or 'voting_address.locationcity' in vista_data['show_columns']:
                    row.append(object.voting_address.locationcity)
                if not 'show_columns' in vista_data or 'voting_address.locationcongress' in vista_data['show_columns']:
                    row.append(object.voting_address.locationcongress)
                if not 'show_columns' in vista_data or 'voting_address.locationstatesenate' in vista_data['show_columns']:
                    row.append(object.voting_address.locationstatesenate)
                if not 'show_columns' in vista_data or 'voting_address.locationstatehouse' in vista_data['show_columns']:
                    row.append(object.voting_address.locationstatehouse)
                if not 'show_columns' in vista_data or 'voting_address.locationmagistrate' in vista_data['show_columns']:
                    row.append(object.voting_address.locationmagistrate)
                if not 'show_columns' in vista_data or 'voting_address.locationborough' in vista_data['show_columns']:
                    row.append(object.voting_address.locationborough)
                if not 'show_columns' in vista_data or 'voting_address.locationprecinct' in vista_data['show_columns']:
                    row.append(object.voting_address.locationprecinct)

            writer.writerow(row)

        return response


class PersonClose(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_person'
    model = Person
    template_name = 'sdcpeople/person_closer.html'

class EventCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'sdcpeople.add_event'
    model = Event
    form_class = EventForm

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        if self.request.POST:
            context_data['participations'] = EventParticipationFormset(self.request.POST)

        else:
            context_data['participations'] = EventParticipationFormset()

        return context_data

    def form_valid(self, form):

        response = super().form_valid(form)

        update_history(form, 'Event', form.instance, self.request.user)

        self.object = form.save()

        formset_data = {
            'participations':EventParticipationFormset( self.request.POST, instance=self.object ),

        }

        for formset_name in formset_data.keys():

            if(formset_data[formset_name]).is_valid():
                formset_data[formset_name].save()
            else:
                messages.add_message(self.request, messages.WARNING, 'There was a problem with ' + formset_name + ', ' + formset_name + ' was not saved')
                print('error saving ' + formset_name + ': ' )
                print(formset_data[formset_name].errors)

        return response

    def get_success_url(self):

        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:event-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:event-detail', kwargs={'pk': self.object.pk})

class EventUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'sdcpeople.change_event'
    model = Event
    form_class = EventForm

    def has_permission(self):
        return super().has_permission() or EventUser.objects.filter(user=self.request.user, event=self.get_object()).exists()

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        if self.request.POST:
            context_data['participations'] = EventParticipationFormset(self.request.POST, instance=self.object )

        else:
            context_data['participations'] = EventParticipationFormset( instance=self.object )

        return context_data

    def form_valid(self, form):

        update_history(form, 'Event', form.instance, self.request.user)

        response = super().form_valid(form)

        self.object = form.save()

        formset_data = {
            'participations':EventParticipationFormset( self.request.POST, instance=self.object ),

        }

        for formset_name in formset_data.keys():

            if(formset_data[formset_name]).is_valid():
                formset_data[formset_name].save()
            else:
                messages.add_message(self.request, messages.WARNING, 'There was a problem with ' + formset_name + ', ' + formset_name + ' was not saved')
                print('error saving ' + formset_name + ': ')
                print(formset_data[formset_name].errors)
                print('tp228bc40', formset_data[formset_name])

        return response


    def get_success_url(self):
        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:event-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:event-detail', kwargs={'pk': self.object.pk})

class EventDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_event'
    model = Event

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['event_labels'] = { field.name: field.verbose_name.title() for field in SubCommittee._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
        return context_data

class EventDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'sdcpeople.delete_event'
    model = Event
    template_name = 'sdcpeople/event_confirm_delete.html'
    success_url = reverse_lazy('sdcpeople:event-list')


class EventList(PermissionRequiredMixin, ListView):
    permission_required = 'sdcpeople.view_event'
    model = Event
    paginate_by = 30

    def setup(self, request, *args, **kwargs):

        self.vista_settings={
            'max_search_keys':5,
            'fields':[],
        }

        self.vista_settings['fields'] = make_vista_fields(Event, field_names=[
            'name',
            'event_type',
            'when',
            'participation__person',
        ])

        self.vista_defaults = QueryDict(urlencode([
            ('filter__fieldname__0', ['membership_status__is_member']),
            ('filter__op__0', ['exact']),
            ('filter__value__0', ['True']),
            ('order_by', ['name_last', 'name_common', ]),
            ('paginate_by',self.paginate_by),
        ],doseq=True) )

        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self, **kwargs):

        queryset = super().get_queryset()

        self.vistaobj = {'querydict':QueryDict(), 'queryset':queryset}

        if 'delete_vista' in self.request.POST:
            delete_vista(self.request)

        if 'query' in self.request.session:
            print('tp 224bc49', 'query in self.request.session')
            querydict = QueryDict(self.request.session.get('query'))
            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                querydict,
                '',
                False,
                self.vista_settings
            )
            del self.request.session['query']

        elif 'vista_query_submitted' in self.request.POST:
            print('tp 224bc50', 'vista_query_submitted')

            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                self.request.POST,
                self.request.POST.get('vista_name') if 'vista_name' in self.request.POST else '',
                self.request.POST.get('make_default') if ('make_default') in self.request.POST else False,
                self.vista_settings
            )
        elif 'retrieve_vista' in self.request.POST:
            print('tp 224bc51', 'retrieve_vista')

            self.vistaobj = retrieve_vista(
                self.request.user,
                queryset,
                'sdcpeople.event',
                self.request.POST.get('vista_name'),
                self.vista_settings

            )
        elif 'default_vista' in self.request.POST:
            print('tp 224bc52', 'default_vista')

            self.vistaobj = default_vista(
                self.request.user,
                queryset,
                self.vista_defaults,
                self.vista_settings
            )
        else:
            self.vistaobj = get_latest_vista(
                self.request.user,
                queryset,
                self.vista_defaults,
                self.vista_settings
            )

        return self.vistaobj['queryset']

    def get_paginate_by(self, queryset):

        if 'paginate_by' in self.vistaobj['querydict'] and self.vistaobj['querydict']['paginate_by']:
            return self.vistaobj['querydict']['paginate_by']

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        vista_data = vista_context_data(self.vista_settings, self.vistaobj['querydict'])

        context_data = {**context_data, **vista_data}

        context_data['vistas'] = Vista.objects.filter(user=self.request.user, model_name='libtekin.item').all() # for choosing saved vistas

        if self.request.POST.get('vista_name'):
            context_data['vista_name'] = self.request.POST.get('vista_name')

        context_data['count'] = self.object_list.count()

        return context_data

class EventCSV(EventList):

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="sdcvirginia_people.csv"'},
        )

        writer = csv.writer(response)
        vista_data = vista_context_data(self.vista_settings, self.vistaobj['querydict'])

        row=[]

        if not 'show_columns' in vista_data or 'name_last' in vista_data['show_columns']:
            row.append(context["labels"]["name_last"])
        if not 'show_columns' in vista_data or 'name_first' in vista_data['show_columns']:
            row.append(context["labels"]["name_first"])
        if not 'show_columns' in vista_data or 'is_quorum' in vista_data['show_columns']:
            row.append("Quorum")
        if not 'show_columns' in vista_data or 'membership_status' in vista_data['show_columns']:
            row.append(context["labels"]["membership_status"])
        if not 'show_columns' in vista_data or 'positions' in vista_data['show_columns']:
            row.append("Positions")
        if not 'show_columns' in vista_data or 'submemberships' in vista_data['show_columns']:
            row.append("SubCommittees")
        if not 'show_columns' in vista_data or 'contactvoice' in vista_data['show_columns']:
            row.append("Voice")
        if not 'show_columns' in vista_data or 'contacttext' in vista_data['show_columns']:
            row.append("Text")
        if not 'show_columns' in vista_data or 'contacemail' in vista_data['show_columns']:
            row.append("Email")
        if not 'show_columns' in vista_data or 'voting_address' in vista_data['show_columns']:
            row.append("voting address")
        if not 'show_columns' in vista_data or 'voting_address.locationcity' in vista_data['show_columns']:
            row.append("City")
        if not 'show_columns' in vista_data or 'voting_address.locationcongress' in vista_data['show_columns']:
            row.append("Congress")
        if not 'show_columns' in vista_data or 'voting_address.locationstatesenate' in vista_data['show_columns']:
            row.append("Senate")
        if not 'show_columns' in vista_data or 'voting_address.locationstatehouse' in vista_data['show_columns']:
            row.append("house")
        if not 'show_columns' in vista_data or 'voting_address.locationmagistrate' in vista_data['show_columns']:
            row.append("Magistrate")
        if not 'show_columns' in vista_data or 'voting_address.locationborough' in vista_data['show_columns']:
            row.append("Borough")
        if not 'show_columns' in vista_data or 'voting_address.locationprecinct' in vista_data['show_columns']:
            row.append("precinct")

        writer.writerow(row)

        for object in self.object_list:

            row=[]

            if not 'show_columns' in vista_data or 'name_last' in vista_data['show_columns']:
                row.append(object.name_last)
            if not 'show_columns' in vista_data or 'name_first' in vista_data['show_columns']:
                row.append(object.name_first)
            if not 'show_columns' in vista_data or 'is_quorum' in vista_data['show_columns']:
                row.append(object.membership_status.is_quorum)
            if not 'show_columns' in vista_data or 'membership_status' in vista_data['show_columns']:
                row.append(object.membership_status)
            if not 'show_columns' in vista_data or 'positions' in vista_data['show_columns']:
                positions=''
                if object.positions.all().exists():
                    for position in object.positions.all():
                        positions = positions + position.title + ', '
                    positions = positions[:-2]
                row.append(positions)
            if not 'show_columns' in vista_data or 'submemberships' in vista_data['show_columns']:
                submemberships=''
                if object.submembership_set.all().exists():
                    for submembership in object.submembership_set.all():
                        submemberships = submemberships + str(submembership.subcommittee) + ', '
                    submemberships=submemberships[:-2]
                row.append(submemberships)
            if not 'show_columns' in vista_data or 'contactvoice' in vista_data['show_columns']:
                contactvoices=''
                if object.contactvoice_set.all().exists():
                    for contactvoice in object.contactvoice_set.all():
                        contactvoices = contactvoices + str(contactvoice.number) + ', '
                    contactvoices=contactvoices[:-2]
                row.append(contactvoices)
            if not 'show_columns' in vista_data or 'contacttext' in vista_data['show_columns']:
                contacttexts=''
                if object.contacttext_set.all().exists():
                    for contacttext in object.contacttext_set.all():
                        contacttexts = contacttexts + str(contacttext.number) + ', '
                    contacttexts=contacttexts[:-2]
                row.append(contacttexts)
            if not 'show_columns' in vista_data or 'contacemail' in vista_data['show_columns']:
                contactemails=''
                if object.contactemail_set.all().exists():
                    for contactemail in object.contactemail_set.all():
                        contactemails = contactemails + str(contactemail.address) + ', '
                    contactemails=contactemails[:-2]
                row.append(contactemails)
            if not 'show_columns' in vista_data or 'voting_address' in vista_data['show_columns']:
                row.append(str(object.voting_address).replace("\n", " "))
            if not 'show_columns' in vista_data or 'voting_address.locationcity' in vista_data['show_columns']:
                row.append(object.voting_address.locationcity)
            if not 'show_columns' in vista_data or 'voting_address.locationcongress' in vista_data['show_columns']:
                row.append(object.voting_address.locationcongress)
            if not 'show_columns' in vista_data or 'voting_address.locationstatesenate' in vista_data['show_columns']:
                row.append(object.voting_address.locationstatesenate)
            if not 'show_columns' in vista_data or 'voting_address.locationstatehouse' in vista_data['show_columns']:
                row.append(object.voting_address.locationstatehouse)
            if not 'show_columns' in vista_data or 'voting_address.locationmagistrate' in vista_data['show_columns']:
                row.append(object.voting_address.locationmagistrate)
            if not 'show_columns' in vista_data or 'voting_address.locationborough' in vista_data['show_columns']:
                row.append(object.voting_address.locationborough)
            if not 'show_columns' in vista_data or 'voting_address.locationprecinct' in vista_data['show_columns']:
                row.append(object.voting_address.locationprecinct)

            writer.writerow(row)

        return response


class EventClose(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_event'
    model = Event
    template_name = 'sdcpeople/event_closer.html'



class SubCommitteeCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'sdcpeople.add_subcommittee'
    model = SubCommittee
    form_class = SubCommitteeForm

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        if self.request.POST:
            context_data['submemberships'] = SubCommitteeSubMembershipFormset(self.request.POST)

        else:
            context_data['submemberships'] = SubCommitteeSubMembershipFormset()

        return context_data

    def form_valid(self, form):

        response = super().form_valid(form)

        update_history(form, 'SubCommittee', form.instance, self.request.user)

        self.object = form.save()

        formset_data = {
            'participations':SubCommitteeSubMembershipFormset( self.request.POST, instance=self.object ),

        }

        for formset_name in formset_data.keys():

            if(formset_data[formset_name]).is_valid():
                formset_data[formset_name].save()
            else:
                messages.add_message(self.request, messages.WARNING, 'There was a problem with ' + formset_name + ', ' + formset_name + ' was not saved')
                print('error saving ' + formset_name + ': ' )
                print(formset_data[formset_name].errors)

        return response

    def get_success_url(self):

        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:subcommittee-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:subcommittee-detail', kwargs={'pk': self.object.pk})

class SubCommitteeUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'sdcpeople.change_subcommittee'
    model = SubCommittee
    form_class = SubCommitteeForm

    def has_permission(self):
        return super().has_permission() or SubCommittee.objects.filter(user=self.request.user, subcommittee=self.get_object()).exists()

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        if self.request.POST:
            context_data['submemberships'] = SubCommitteeSubMembershipFormset(self.request.POST, instance=self.object )

        else:
            context_data['submemberships'] = SubCommitteeSubMembershipFormset( instance=self.object )

        return context_data

    def form_valid(self, form):

        update_history(form, 'SubCommittee', form.instance, self.request.user)

        response = super().form_valid(form)

        self.object = form.save()

        formset_data = {
            'subcommittees':SubCommitteeSubMembershipFormset( self.request.POST, instance=self.object ),
        }

        for formset_name in formset_data.keys():

            if(formset_data[formset_name]).is_valid():
                formset_data[formset_name].save()
            else:
                messages.add_message(self.request, messages.WARNING, 'There was a problem with ' + formset_name + ', ' + formset_name + ' was not saved')
                print('error saving ' + formset_name + ': ')
                print(formset_data[formset_name].errors)

        return response


    def get_success_url(self):
        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:subcommittee-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:subcommittee-detail', kwargs={'pk': self.object.pk})

class SubCommitteeDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_subcommittee'
    model = SubCommittee

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['subcommittee_labels'] = { field.name: field.verbose_name.title() for field in SubCommittee._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
        context_data['submembership_labels'] = { field.name: field.verbose_name.title() for field in SubMembership._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data


class SubCommitteeDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'sdcpeople.delete_subcommittee'
    model = SubCommittee
    template_name = 'sdcpeople/subcommittee_confirm_delete.html'
    success_url = reverse_lazy('sdcpeople:subcommittee-list')

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['subcommittee_labels'] = { field.name: field.verbose_name.title() for field in SubCommittee._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
        context_data['submembership_labels'] = { field.name: field.verbose_name.title() for field in SubMembership._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data

class SubCommitteeList(PermissionRequiredMixin, ListView):
    permission_required = 'sdcpeople.view_subcommittee'
    model = SubCommittee
    paginate_by = 30

    def setup(self, request, *args, **kwargs):

        self.vista_settings={
            'max_search_keys':2,
            'fields':[],
        }

        self.vista_settings['fields'] = make_vista_fields(SubCommittee, field_names=[
            'name',
            'submembership__person',
        ])

        self.vista_defaults = QueryDict(urlencode([
            # ('filter__fieldname__0', ['membership_status__is_member']),
            # ('filter__op__0', ['exact']),
            # ('filter__value__0', ['True']),
            ('order_by', ['rank', 'name', ]),
            ('paginate_by',self.paginate_by),
        ],doseq=True) )

        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self, **kwargs):

        queryset = super().get_queryset()

        self.vistaobj = {'querydict':QueryDict(), 'queryset':queryset}

        if 'delete_vista' in self.request.POST:
            delete_vista(self.request)

        if 'query' in self.request.session:
            print('tp 224bc49', 'query in self.request.session')
            querydict = QueryDict(self.request.session.get('query'))
            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                querydict,
                '',
                False,
                self.vista_settings
            )
            del self.request.session['query']

        elif 'vista_query_submitted' in self.request.POST:
            print('tp 224bc50', 'vista_query_submitted')

            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                self.request.POST,
                self.request.POST.get('vista_name') if 'vista_name' in self.request.POST else '',
                self.request.POST.get('make_default') if ('make_default') in self.request.POST else False,
                self.vista_settings
            )
        elif 'retrieve_vista' in self.request.POST:
            print('tp 224bc51', 'retrieve_vista')

            self.vistaobj = retrieve_vista(
                self.request.user,
                queryset,
                'sdcpeople.subcommittee',
                self.request.POST.get('vista_name'),
                self.vista_settings

            )
        elif 'default_vista' in self.request.POST:
            print('tp 224bc52', 'default_vista')

            self.vistaobj = default_vista(
                self.request.user,
                queryset,
                self.vista_defaults,
                self.vista_settings
            )
        else:
            self.vistaobj = get_latest_vista(
                self.request.user,
                queryset,
                self.vista_defaults,
                self.vista_settings
            )

            print('tp 224bc53', 'else')

        return self.vistaobj['queryset']


    def get_paginate_by(self, queryset):

        if 'paginate_by' in self.vistaobj['querydict'] and isinstance(self.vistaobj['querydict']['paginate_by'], int):

            return self.vistaobj['querydict']['paginate_by']

        return super().get_paginate_by(self)

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        vista_data = vista_context_data(self.vista_settings, self.vistaobj['querydict'])

        context_data = {**context_data, **vista_data}

        context_data['vistas'] = Vista.objects.filter(user=self.request.user, model_name='libtekin.item').all() # for choosing saved vistas

        if self.request.POST.get('vista_name'):
            context_data['vista_name'] = self.request.POST.get('vista_name')

        context_data['count'] = self.object_list.count()

        return context_data

class SubCommitteeClose(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_subcommittee'
    model = SubCommittee
    template_name = 'sdcpeople/subcommittee_closer.html'


############Participation

class ParticipationCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'sdcpeople.add_participation'
    model = Participation
    form_class = ParticipationForm

    def get_success_url(self):

        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:participation-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:participation-detail', kwargs={'pk': self.object.pk})

class ParticipationUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'sdcpeople.change_participation'
    model = Participation
    form_class = ParticipationForm


    def get_success_url(self):
        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:participation-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:participation-detail', kwargs={'pk': self.object.pk})

class ParticipationDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_participation'
    model = Participation


class ParticipationDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'sdcpeople.delete_participation'
    model = Participation
    template_name = 'sdcpeople/participation_confirm_delete.html'
    success_url = reverse_lazy('sdcpeople:participation-list')


class ParticipationList(PermissionRequiredMixin, ListView):
    permission_required = 'sdcpeople.view_participation'
    model = Participation
    paginate_by = 30


class ParticipationClose(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_participation'
    model = Participation
    template_name = 'sdcpeople/participation_closer.html'


############Participation

class LocationBoroughCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'sdcpeople.add_locationborough'
    model = LocationBorough
    form_class = LocationBoroughForm

    def get_success_url(self):

        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:locationborough-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:locationborough-detail', kwargs={'pk': self.object.pk})

class LocationBoroughUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'sdcpeople.change_locationborough'
    model = LocationBorough
    form_class = LocationBoroughForm

    def get_success_url(self):

        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:locationborough-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:locationborough-detail', kwargs={'pk': self.object.pk})

class LocationBoroughDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_locationborough'
    model = LocationBorough

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['locationborough_labels'] = { field.name: field.verbose_name.title() for field in LocationBorough._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data


class LocationBoroughDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'sdcpeople.delete_locationborough'
    model = LocationBorough
    success_url = reverse_lazy('sdcpeople:locationborough-list')

class LocationBoroughList(PermissionRequiredMixin, ListView):
    permission_required = 'sdcpeople.view_locationborough'
    model = LocationBorough

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['locationborough_labels'] = { field.name: field.verbose_name.title() for field in LocationBorough._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
        return context_data

class LocationBoroughClose(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_locationborough'
    model = LocationBorough
    template_name = 'sdcpeople/locationborough_closer.html'


class LocationCityCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'sdcpeople.add_locationcity'
    model = LocationCity
    form_class = LocationCityForm

    def get_success_url(self):
        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:locationcity-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:locationcity-detail', kwargs={'pk': self.object.pk})

class LocationCityUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'sdcpeople.change_locationcity'
    model = LocationCity
    form_class = LocationCityForm

    def get_success_url(self):
        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:locationongress-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:locationcity-detail', kwargs={'pk': self.object.pk})


class LocationCityDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_locationcity'
    model = LocationCity

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['locationcity_labels'] = { field.name: field.verbose_name.title() for field in LocationCity._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data


class LocationCityDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'sdcpeople.delete_locationcity'
    model = LocationCity
    success_url = reverse_lazy('sdcpeople:locationcity-list')

class LocationCityList(PermissionRequiredMixin, ListView):
    permission_required = 'sdcpeople.view_locationcity'
    model = LocationCity

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['locationcity_labels'] = { field.name: field.verbose_name.title() for field in LocationCity._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
        return context_data

class LocationCityClose(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_locationcity'
    model = LocationCity
    template_name = 'sdcpeople/locationcity_closer.html'

class LocationCongressCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'sdcpeople.add_locationcongress'
    model = LocationCongress
    form_class = LocationCongressForm

    def get_success_url(self):
        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:locationcongress-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:locationcongress-detail', kwargs={'pk': self.object.pk})

class LocationCongressUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'sdcpeople.change_locationcongress'
    model = LocationCongress
    form_class = LocationCongressForm

    def get_success_url(self):
        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:locationongress-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:locationcongress-detail', kwargs={'pk': self.object.pk})


class LocationCongressDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_locationcongress'
    model = LocationCongress

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['locationcongress_labels'] = { field.name: field.verbose_name.title() for field in LocationCongress._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data


class LocationCongressDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'sdcpeople.delete_locationcongress'
    model = LocationCongress
    success_url = reverse_lazy('sdcpeople:locationcongress-list')

class LocationCongressList(PermissionRequiredMixin, ListView):
    permission_required = 'sdcpeople.view_locationcongress'
    model = LocationCongress

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['locationcongress_labels'] = { field.name: field.verbose_name.title() for field in LocationCongress._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
        return context_data

class LocationCongressClose(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_locationcongress'
    model = LocationCongress
    template_name = 'sdcpeople/locationcongress_closer.html'


class LocationStateHouseCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'sdcpeople.add_LocationStateHouse'
    model = LocationStateHouse
    form_class = LocationStateHouseForm

    def get_success_url(self):
        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:locationstatehouse-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:locationstatehouse-detail', kwargs={'pk': self.object.pk})

class LocationStateHouseUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'sdcpeople.change_LocationStateHouse'
    model = LocationStateHouse
    form_class = LocationStateHouseForm

    def get_success_url(self):
        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:locationstatehouse-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:locationstatehouse-detail', kwargs={'pk': self.object.pk})

class LocationStateHouseDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_LocationStateHouse'
    model = LocationStateHouse

class LocationStateHouseDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'sdcpeople.delete_LocationStateHouse'
    model = LocationStateHouse
    success_url = reverse_lazy('sdcpeople:LocationStateHouse-list')

class LocationStateHouseList(PermissionRequiredMixin, ListView):
    permission_required = 'sdcpeople.view_LocationStateHouse'
    model = LocationStateHouse

class LocationStateHouseClose(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_LocationStateHouse'
    model = LocationStateHouse
    template_name = 'sdcpeople/LocationStateHouse_closer.html'


class LocationStateSenateCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'sdcpeople.add_LocationStateSenate'
    model = LocationStateSenate
    form_class = LocationStateSenateForm

    def get_success_url(self):
        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:locationstatesenate-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:locationstatesenate-detail', kwargs={'pk': self.object.pk})

class LocationStateSenateUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'sdcpeople.change_LocationStateSenate'
    model = LocationStateSenate
    form_class = LocationStateSenateForm

    def get_success_url(self):
        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:locationstatesenate-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:locationstatesenate-detail', kwargs={'pk': self.object.pk})

class LocationStateSenateDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_LocationStateSenate'
    model = LocationStateSenate

class LocationStateSenateDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'sdcpeople.delete_LocationStateSenate'
    model = LocationStateSenate
    success_url = reverse_lazy('sdcpeople:LocationStateSenate-list')

class LocationStateSenateList(PermissionRequiredMixin, ListView):
    permission_required = 'sdcpeople.view_LocationStateSenate'
    model = LocationStateSenate

class LocationStateSenateClose(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_LocationStateSenate'
    model = LocationStateSenate
    template_name = 'sdcpeople/LocationStateSenate_closer.html'


class LocationPrecinctCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'sdcpeople.add_locationprecinct'
    model = LocationPrecinct
    form_class = LocationPrecinctForm

    def get_success_url(self):
        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:locationprecinct-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:locationprecinct-detail', kwargs={'pk': self.object.pk})

class LocationPrecinctUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'sdcpeople.change_locationprecinct'
    model = LocationPrecinct
    form_class = LocationPrecinctForm

    def get_success_url(self):
        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:locationprecinct-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:locationprecinct-detail', kwargs={'pk': self.object.pk})

class LocationPrecinctDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_locationprecinct'
    model = LocationPrecinct

class LocationPrecinctDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'sdcpeople.delete_locationprecinct'
    model = LocationPrecinct
    success_url = reverse_lazy('sdcpeople:locationprecinct-list')

class LocationPrecinctList(PermissionRequiredMixin, ListView):
    permission_required = 'sdcpeople.view_locationprecinct'
    model = LocationPrecinct

class LocationPrecinctClose(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_locationprecinct'
    model = LocationPrecinct
    template_name = 'sdcpeople/locationprecinct_closer.html'


class VotingAddressCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'sdcpeople.add_votingaddress'
    model = VotingAddress
    form_class = VotingAddressForm


    def form_valid(self, form):

        response = super().form_valid(form)

        update_history(form, 'VotingAddress', form.instance, self.request.user)

        return response

    def get_success_url(self):

        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:votingaddress-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:votingaddress-detail', kwargs={'pk': self.object.pk})


class VotingAddressUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'sdcpeople.change_votingaddress'
    model = VotingAddress
    form_class = VotingAddressForm

    def form_valid(self, form):

        response = super().form_valid(form)

        update_history(form, 'VotingAddress', form.instance, self.request.user)

        return response

    def get_success_url(self):

        if 'popup' in self.kwargs:
            return reverse_lazy('sdcpeople:votingaddress-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('sdcpeople:votingaddress-detail', kwargs={'pk': self.object.pk})


class VotingAddressDetail(PermissionRequiredMixin, DetailView):

    permission_required = 'sdcpeople.view_votingaddress'
    model = VotingAddress


class VotingAddressDelete(PermissionRequiredMixin, UpdateView):
    permission_required = 'sdcpeople.delete_votingaddress'
    model = VotingAddress
    template_name = 'sdcpeople/votingaddress_confirm_delete.html'
    success_url = reverse_lazy('sdcpeople:votingaddress-list')

class VotingAddressList(PermissionRequiredMixin, ListView):
    permission_required = 'sdcpeople.view_votingaddress'
    model = VotingAddress
    paginate_by = 30

    def setup(self, request, *args, **kwargs):

        self.vista_settings={
            'max_search_keys':5,
            'text_fields_available':[],
            'filter_fields_available':{},
            'order_by_fields_available':[],
            'columns_available':[],
        }

        derived_field_labels={ field.name: field.verbose_name.title() for field in VotingAddress._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
        more_field_labels={
            'voting_address__locationcity__name':'City',
            'voting_address__locationcongress__name':'Congress',
            'voting_address__locationstatesenate__name':'Senate',
            'voting_address__locationborough__name':'Borough',
            'voting_address__locationprecinct__name':'Precinct',
            'voting_address__locationstathouse__name':'HOD',
            'voting_address__locationmagistrate__name':'Magistrate',
        }

        self.field_labels={**derived_field_labels, **more_field_labels}

        self.vista_settings['text_fields_available']=[
            'name_last',
            'name_first',
            'name_middles',
            'name_common',
            'voting_address__locationcity__name',
            'voting_address__locationcongress__name',
            'voting_address__locationstatesenate__name',
            'voting_address__locationborough__name',
            'voting_address__locationprecinct__name',
            'voting_address__locationborough__name',
            'voting_address__locationmagistrate__name',
        ]

        self.vista_settings['filter_fields_available'] = [
            'name_last',
            'name_first',
            'name_middles',
            'name_common',
            'voting_address__locationcity',
            'voting_address__locationcongress',
            'voting_address__locationstatesenate',
            'voting_address__locationborough',
            'voting_address__locationprecinct',
            'voting_address__locationborough',
            'voting_address__locationmagistrate',
        ]

        for field in [
            'name_last',
            'name_first',
            'name_middles',
            'name_common',
        ]:
            self.vista_settings['order_by_fields_available'].append((field[0], field[1]))
            self.vista_settings['order_by_fields_available'].append(('-' + field[0], field[1] + " [Reverse]"))

        self.vista_settings['columns_available'] =[
            'name_last',
            'name_first',
            'name_middles',
            'name_common',
            'voting_address__locationcity',
            'voting_address__locationcongress',
            'voting_address__locationstatesenate',
            'voting_address__locationborough',
            'voting_address__locationprecinct',
            'voting_address__locationborough',
            'voting_address__locationmagistrate',
        ]

        self.vista_defaults = {
            'order_by': VotingAddress._meta.ordering,
            'paginate_by':self.paginate_by,
        }

        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self, **kwargs):

        queryset = super().get_queryset()

        self.vistaobj = {'querydict':QueryDict(), 'queryset':queryset}

        if 'delete_vista' in self.request.POST:
            delete_vista(self.request)

        if 'query' in self.request.session:
            querydict = QueryDict(self.request.session.get('query'))
            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                querydict,
                '',
                False,
                self.vista_settings
            )
            del self.request.session['query']

        elif 'vista_query_submitted' in self.request.POST:

            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                self.request.POST,
                self.request.POST.get('vista_name') if 'vista_name' in self.request.POST else '',
                self.request.POST.get('make_default') if ('make_default') in self.request.POST else False,
                self.vista_settings
            )
        elif 'retrieve_vista' in self.request.POST:
            self.vistaobj = retrieve_vista(
                self.request.user,
                queryset,
                'sdcpeople.votingaddress',
                self.request.POST.get('vista_name'),
                self.vista_settings

            )
        elif 'default_vista' in self.request.POST:
            self.vistaobj = default_vista(
                self.request.user,
                queryset,
                QueryDict(urllib.parse.urlencode(self.vista_defaults)),
                self.vista_settings
            )

        return self.vistaobj['queryset']

    def get_paginate_by(self, queryset):

        if 'paginate_by' in self.vistaobj['querydict'] and self.vistaobj['querydict']['paginate_by']:
            return self.vistaobj['querydict']['paginate_by']

        return super().get_paginate_by(self)

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        context_data['locationcity'] = LocationCity.objects.all()
        context_data['locationcongresss'] = LocationCongress.objects.all()
        context_data['locationstatesenate'] = LocationStateSenate.objects.all()
        context_data['locationstatehouse'] = LocationStateHouse.objects.all()
        context_data['locationprecinct'] = LocationPrecinct.objects.all()
        context_data['locationborough'] = LocationBorough.objects.all()
        context_data['locationmagistrate'] = LocationMagistrate.objects.all()

        context_data['order_by_fields_available'] = []
        for fieldname in self.vista_settings['order_by_fields_available']:
            if fieldname > '' and fieldname[0] == '-':
                context_data['order_by_fields_available'].append({ 'name':fieldname, 'label':VotingAddress._meta.get_field(fieldname[1:]).verbose_name.title() + ' [Reverse]'})
            else:
                context_data['order_by_fields_available'].append({ 'name':fieldname, 'label':VotingAddress._meta.get_field(fieldname).verbose_name.title()})

        context_data['columns_available'] = [{ 'name':fieldname, 'label':VotingAddress._meta.get_field(fieldname).verbose_name.title() } for fieldname in self.vista_settings['columns_available']]

        context_data['filterfields_available'] = self.vista_settings['filter_fields_available']

        context_data['field_labels'] = self.vista_settings['field_labels']

        context_data['vistas'] = Vista.objects.filter(user=self.request.user, model_name='sdcpeople.votingaddress').all() # for choosing saved vistas

        if self.request.POST.get('vista_name'):
            context_data['vista_name'] = self.request.POST.get('vista_name')

        vista_querydict = self.vistaobj['querydict']

        #putting the index before votingaddress name to make it easier for the template to iterate
        context_data['filter'] = []
        for indx in range( self.vista_settings['max_search_keys']):
            cdfilter = {}
            cdfilter['fieldname'] = vista_querydict.get('filter__fieldname__' + str(indx)) if 'filter__fieldname__' + str(indx) in vista_querydict else ''
            cdfilter['op'] = vista_querydict.get('filter__op__' + str(indx) ) if 'filter__op__' + str(indx) in vista_querydict else ''
            cdfilter['value'] = vista_querydict.get('filter__value__' + str(indx)) if 'filter__value__' + str(indx) in vista_querydict else ''
            if cdfilter['op'] in ['in', 'range']:
                cdfilter['value'] = vista_querydict.getlist('filter__value__' + str(indx)) if 'filter__value__'  + str(indx) in vista_querydict else []
            context_data['filter'].append(cdfilter)

        context_data['order_by'] = vista_querydict.getlist('order_by') if 'order_by' in vista_querydict else VotingAddress._meta.ordering

        context_data['combined_text_search'] = vista_querydict.get('combined_text_search') if 'combined_text_search' in vista_querydict else ''

        context_data['votingaddress_labels'] = { field.name: field.verbose_name.title() for field in VotingAddress._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data

class VotingAddressClose(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_votingaddress'
    model = VotingAddress
    template_name = 'sdcpeople/votingaddress_closer.html'
