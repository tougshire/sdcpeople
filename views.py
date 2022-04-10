import urllib
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.http import QueryDict
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.views.generic.list import ListView
from tougshire_vistas.models import Vista
from tougshire_vistas.views import (default_vista, delete_vista, get_global_vista, get_latest_vista, make_vista,
                                    retrieve_vista, vista_context_data, vista_fields)

from .forms import (LocationBoroughForm, LocationCongressForm, LocationPrecinctForm, LocationStateHouseForm,
                    LocationStateSenateForm, PersonContactEmailFormset, PersonContactTextFormset, PersonContactVoiceFormset,
                    PersonDuesPaymentFormset, PersonForm, PersonLinkFormset, PersonMembershipApplicationFormset, PersonSubMembershipFormset, VotingAddressForm)
from .models import (ContactText, ContactVoice, History, LocationBorough, LocationCongress, LocationMagistrate,
                     LocationPrecinct, LocationStateHouse, LocationStateSenate, MembershipStatus, Person, PersonUser, SubCommittee, VotingAddress)


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
            context_data['contactvoices'] = PersonContactVoiceFormset(self.request.POST)
            context_data['contacttexts'] = PersonContactTextFormset(self.request.POST)
            context_data['contactemails'] = PersonContactEmailFormset(self.request.POST)
            context_data['membershipapplications'] = PersonMembershipApplicationFormset(self.request.POST)
            context_data['submemberships'] = PersonSubMembershipFormset(self.request.POST )
            context_data['duespayments'] = PersonDuesPaymentFormset(self.request.POST)
            context_data['links'] = PersonLinkFormset(self.request.POST)

        else:
            context_data['contactvoices'] = PersonContactVoiceFormset()
            context_data['contacttexts'] = PersonContactTextFormset()
            context_data['contactemails'] = PersonContactEmailFormset()
            context_data['membershipapplications'] = PersonMembershipApplicationFormset()
            context_data['submemberships'] = PersonSubMembershipFormset()
            context_data['duespayments'] = PersonDuesPaymentFormset()
            context_data['links'] = PersonLinkFormset()

        return context_data

    def form_valid(self, form):

        response = super().form_valid(form)

        update_history(form, 'Person', form.instance, self.request.user)

        self.object = form.save()

        formset_data = {
            'contactvoices':PersonContactVoiceFormset( self.request.POST, instance=self.object ),
            'contacttexts':PersonContactTextFormset( self.request.POST, instance=self.object ),
            'contactemails':PersonContactEmailFormset( self.request.POST, instance=self.object ),
            'membershipapplications':PersonMembershipApplicationFormset( self.request.POST, instance=self.object ),
            'submemberships':PersonSubMembershipFormset(self.request.POST, instance=self.object ),
            'duespayments':PersonDuesPaymentFormset( self.request.POST, instance=self.object ),
            'links':PersonLinkFormset( self.request.POST, instance=self.object ),

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
            context_data['contactvoices'] = PersonContactVoiceFormset(self.request.POST, instance=self.object )
            context_data['contacttexts'] = PersonContactTextFormset(self.request.POST, instance=self.object )
            context_data['contactemails'] = PersonContactEmailFormset(self.request.POST, instance=self.object )
            context_data['membershipapplications'] = PersonMembershipApplicationFormset(self.request.POST, instance=self.object )
            context_data['submemberships'] = PersonSubMembershipFormset(self.request.POST, instance=self.object )
            context_data['duespayments'] = PersonDuesPaymentFormset(self.request.POST, instance=self.object )
            context_data['links'] = PersonLinkFormset(self.request.POST, instance=self.object )

        else:
            context_data['contactvoices'] = PersonContactVoiceFormset( instance=self.object )
            context_data['contacttexts'] = PersonContactTextFormset( instance=self.object )
            context_data['contactemails'] = PersonContactEmailFormset( instance=self.object )
            context_data['membershipapplications'] = PersonMembershipApplicationFormset( instance=self.object )
            context_data['submemberships'] = PersonSubMembershipFormset( instance=self.object )
            context_data['duespayments'] = PersonDuesPaymentFormset( instance=self.object )
            context_data['links'] = PersonLinkFormset( instance=self.object )

        return context_data

    def form_valid(self, form):

        update_history(form, 'Person', form.instance, self.request.user)

        response = super().form_valid(form)

        self.object = form.save()

        formset_data = {
            'contactvoices':PersonContactVoiceFormset( self.request.POST, instance=self.object ),
            'contacttexts':PersonContactTextFormset( self.request.POST, instance=self.object ),
            'contactemails':PersonContactEmailFormset( self.request.POST, instance=self.object ),
            'membershipapplications':PersonMembershipApplicationFormset( self.request.POST, instance=self.object ),
            'submemberships':PersonSubMembershipFormset(self.request.POST, instance=self.object ),
            'duespayments':PersonDuesPaymentFormset( self.request.POST, instance=self.object ),
            'links':PersonLinkFormset( self.request.POST, instance=self.object ),

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
        print('tp m3ja04', self.kwargs)
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

# class PersonSoftDelete(PermissionRequiredMixin, UpdateView):
#     permission_required = 'sdcpeople.delete_person'
#     model = Person
#     template_name = 'sdcpeople/person_confirm_delete.html'
#     success_url = reverse_lazy('sdcpeople:person-list')
#     fields = ['is_deleted']

#     def get_context_data(self, **kwargs):

#         context_data = super().get_context_data(**kwargs)
#         context_data['person_labels'] = { field.name: field.verbose_name.title() for field in Person._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
#         context_data['voting_address_labels'] = { field.name: field.verbose_name.title() for field in VotingAddress._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

#         return context_data

class PersonList(PermissionRequiredMixin, ListView):
    permission_required = 'sdcpeople.view_person'
    model = Person
    # paginate_by = 30

    def setup(self, request, *args, **kwargs):
        self.vista_settings={
            'max_search_keys':5,
            'fields':[],
        }

        self.vista_settings['fields'] = vista_fields(Person, rels=False)
        del(self.vista_settings['fields']['subcommittees'])
        del(self.vista_settings['fields']['name_suffix'])
        del(self.vista_settings['fields']['name_middles'])
        del(self.vista_settings['fields']['voting_address'])
        self.vista_settings['fields']['submembership__subcommittee'] = {
            'label':'Subcommittee',
            'type':'model',
            'queryset': SubCommittee.objects.all(),
            'available_for':[
                'fieldsearch',
            ]
        }
        self.vista_settings['fields']['voting_address__locationborough'] = {
            'label':LocationBorough._meta.verbose_name,
            'type':'model',
            'queryset': LocationBorough.objects.all(),
            'available_for':[
                'fieldsearch',
                'columns',
                'order_by'
            ]
        }
        self.vista_settings['fields']['voting_address__locationprecinct'] = {
            'label':LocationPrecinct._meta.verbose_name,
            'type':'model',
            'queryset': LocationPrecinct.objects.all(),
            'available_for':[
                'fieldsearch',
                'columns',
                'order_by'
            ]
        }
        self.vista_settings['fields']['membership_status__is_quorum'] = {
            'label':'Is Quroum',
            'type':'boolean',
            'choices': [(True, 'True'), (False, 'False')],
            'available_for':[
                'fieldsearch',
                'columns',
                'order_by'
            ]
        }
        self.vista_settings['fields']['voting_address'] = {
            'label':VotingAddress._meta.verbose_name,
            'type':'model',
            'queryset': VotingAddress.objects.all(),
            'available_for':[
                'columns',
            ]
        }
        self.vista_defaults = QueryDict(urlencode([
            ('filter__fieldname', ['membership_status__is_member']),
            ('filter__op', ['exact']),
            ('filter__value', [True]),
            ('order_by', ['membership_status__is_quorum', 'name_last']),
            # ('paginate_by',self.paginate_by),
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
                'sdcpeople.person',
                self.request.POST.get('vista_name'),
                self.vista_settings

            )
        else: #elif 'default_vista' in self.request.POST:
            self.vistaobj = default_vista(
                self.request.user,
                queryset,
                self.vista_defaults,
                self.vista_settings
            )

        return self.vistaobj['queryset']

    # def get_paginate_by(self, queryset):

    #     if 'paginate_by' in self.vistaobj['querydict'] and self.vistaobj['querydict']['paginate_by']:
    #         return self.vistaobj['querydict']['paginate_by']

    #     return super().get_paginate_by(self)

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        vista_data = vista_context_data(self.vista_settings, self.vistaobj['querydict'])
        context_data = {**context_data, **vista_data}

        context_data['vistas'] = Vista.objects.filter(user=self.request.user, model_name='sdcpeople.person').all() # for choosing saved vistas

        if self.request.POST.get('vista_name'):
            context_data['vista_name'] = self.request.POST.get('vista_name')

        context_data['count'] = self.object_list.count()

        return context_data

class PersonClose(PermissionRequiredMixin, DetailView):
    permission_required = 'sdcpeople.view_person'
    model = Person
    template_name = 'sdcpeople/person_closer.html'

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
    # paginate_by = 30

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
            'voting_address__locationcongress',
            'voting_address__locationstatesenate',
            'voting_address__locationborough',
            'voting_address__locationprecinct',
            'voting_address__locationborough',
            'voting_address__locationmagistrate',
        ]

        self.vista_defaults = {
            'order_by': VotingAddress._meta.ordering,
            # 'paginate_by':self.paginate_by,
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

    # def get_paginate_by(self, queryset):

    #     if 'paginate_by' in self.vistaobj['querydict'] and self.vistaobj['querydict']['paginate_by']:
    #         return self.vistaobj['querydict']['paginate_by']

    #     return super().get_paginate_by(self)

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

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
