import csv
from django.core.management import BaseCommand
from django.utils import timezone
from sdcpeople import forms

from sdcpeople.models import Person,  LocationBorough,LocationCongress,LocationCity,LocationMagistrate,LocationPrecinct,LocationStateHouse,LocationStateSenate,VotingAddress,ContactEmail,ContactText,ContactVoice,Event,EventType

class Command(BaseCommand):
    help = "Loads products and product categories from CSV file."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)
        parser.add_argument("--overwrite", nargs='+', type=bool, default=False)

    def handle(self, *args, **options):
        start_time = timezone.now()
        file_path = options["file_path"]
        print('tp228ce00', file_path)
        with open(file_path, "r") as csv_file:
            data = list(csv.reader(csv_file, delimiter=","))
            existing_people = {person.vb_voter_id: {person.id} for person in Person.objects.all()}
            existing_location_cities = {location_city.name: location_city.id for location_city in LocationCity.objects.all()}
            existing_location_boroughs = {location_borough.name: location_borough.id for location_borough in LocationBorough.objects.all()}
            existing_location_congresses = {location_congress.name: location_congress.id for location_congress in LocationCongress.objects.all()}
            existing_location_magistrates = {location_magistrate.name: location_magistrate.id for location_magistrate in LocationMagistrate.objects.all()}
            existing_location_precincts = {location_precinct.name: location_precinct.id for location_precinct in LocationPrecinct.objects.all()}
            existing_location_statehouses = {location_statehouse.name: location_statehouse.id for location_statehouse in LocationStateHouse.objects.all()}
            existing_location_statesenates = {location_statesenate.name: location_statesenate.id for location_statesenate in LocationStateSenate.objects.all()}

            people_to_add = []
            columns_available=[
                'full_name',
                'name_prefix',
                'name_last',
                'name_first',
                'name_middles',
                'name_common',
                'name_suffix',
                'voting_address',
                'membership_status',
                'positions',
                'vb_campaign_id',
                'city',
                'congress',
                'statesenate',
                'statehouse',
                'magistrate',
                'borough',
                'precinct',
                'street_address',

            ]

            data_columns={}
            header = data[0]
            for col in range(1,len(data[0])):
                if data[0][col] in columns_available:
                    data_columns[data[0][col]]=col

            print('tp228cf06', data_columns)
            data.pop(0)

            for row in data:
                update_person = None
                new_van_id = row[0]
                location_models={
                    'city':LocationCity,
                    'borough':LocationBorough,
                    'congress':LocationCongress,
                    'magistrate':LocationMagistrate,
                    'precinct':LocationPrecinct,
                    'statehouse':LocationStateHouse,
                    'statesenate':LocationStateSenate,
                }
                            
                if new_van_id > "":
                    update_person, person_created = Person.objects.get_or_create(vb_voter_id=new_van_id)
                    write_person=False
                    if person_created:
                        write_person=True
                    else:
                        if '--overwrite' in options and options['--overwrite']:
                            write_person=True
                    
                    if update_person is not None:
                        if write_person:
                            lazy_set = {}
                            voting_address = None
                            for col_name, col_num in data_columns.items():
                                row[col_num]=row[col_num].strip()
                                if(row[col_num])>"":
                                    if col_name == 'full_name':
                                        name_parts = row[col_num].split(', ')
                                        setattr(update_person,'name_last',name_parts[0])
                                        name_parts = name_parts[1].split(' ')
                                        setattr(update_person, 'name_first', name_parts[0])
                                        if len(name_parts) > 1:
                                            setattr(update_person, 'name_middles', name_parts[1])
                                    elif col_name == 'voting_address':
                                        voting_address,created = VotingAddress.objects.get_or_create(street_address=row[col_num])
                                        setattr(update_person, 'voting_address', voting_address)
                                        for key, value in lazy_set:
                                            if key[:8]=='location':
                                                setattr(voting_address,key,value)
                                                lazy_set.pop(key)
                                    elif col_name in location_models:
                                        print('tp228ck16', col_name)
                                        try:
                                            location_object = location_models[col_name].objects.get(name=row[col_num])
                                            print('tp228ck17', location_object)
                                            if voting_address is not None:
                                                setattr(voting_address,'location'+col_name,location_object)
                                            else:
                                                lazy_set['location'+col_name] = location_object
                                        except location_models[col_name].DoesNotExist:
                                            print('tp228ck20', 'passing on '+col_name)
                                            pass


                                    else:
                                        setattr(update_person, col_name, row[col_num])

                                
                            print('tp228cf03', update_person)
                            if voting_address is not None:
                                print('tp228ck24', voting_address)
                                voting_address.save()
                            update_person.save()


        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loading CSV took: {(end_time-start_time).total_seconds()} seconds."
            )
        )
