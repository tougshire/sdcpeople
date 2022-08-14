from sys import displayhook
from django.contrib import admin

from .models import (
    ContactEmail,
    ContactText,
    ContactVoice,
    DuesPayment,
    EventType,
    Event,
    History,
    RecordactPerson,
    Link,
    LocationCity,
    LocationBorough,
    LocationCongress,
    LocationMagistrate,
    LocationPrecinct,
    LocationStateHouse,
    LocationStateSenate,
    MembershipApplication,
    MembershipHistory,
    MembershipStatus,
    MembershipType,
    Participation,
    ParticipationLevel,
    PaymentMethod,
    Person,
    PersonUser,
    Position,
    PositionHistory,
    SubCommittee,
    SubMembership,
    VotingAddress,
)


admin.site.register(ContactText)

admin.site.register(ContactEmail)

admin.site.register(ContactVoice)

admin.site.register(DuesPayment)

admin.site.register(EventType)

admin.site.register(Event)

admin.site.register(Link
)
admin.site.register(LocationBorough)

admin.site.register(LocationCity)

admin.site.register(LocationCongress)

admin.site.register(LocationMagistrate)

admin.site.register(LocationPrecinct)

admin.site.register(LocationStateHouse)

admin.site.register(LocationStateSenate)

admin.site.register(History)


admin.site.register(Participation)

admin.site.register(ParticipationLevel)

admin.site.register(PositionHistory)

admin.site.register(MembershipApplication)

class MembershipHistoryAdmin(admin.ModelAdmin):
    list_display=('person', 'membership_status', 'effective_date')

admin.site.register(MembershipHistory, MembershipHistoryAdmin)

class MembershipStatusAdmin(admin.ModelAdmin):
    list_display=('membership_type', 'name', 'is_quorum', 'is_member')

admin.site.register(MembershipStatus, MembershipStatusAdmin)

admin.site.register(MembershipType)

admin.site.register(PaymentMethod)

class PersonManager(admin.ModelAdmin):

    def get_queryset(self, request):
        return Person.all_objects.all()

admin.site.register(Person, PersonManager)

class PositionAdmin(admin.ModelAdmin):
    list_display=('title', 'rank_number')

admin.site.register(Position, PositionAdmin)

admin.site.register(SubCommittee)

admin.site.register(SubMembership)

admin.site.register(VotingAddress)

admin.site.register(PersonUser)

admin.site.register(RecordactPerson)
