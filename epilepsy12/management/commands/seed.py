from django.core.management.base import BaseCommand
from ...models.hospital_trust import HospitalTrust
from ...constants import ALL_HOSPITALS


class Command(BaseCommand):
    help = "seed database with hospital trust data for testing and development."

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help="Mode")

    def handle(self, *args, **options):
        if (options['mode'] == 'delete'):
            self.stdout.write('Deleting hospital trust data...')
            delete_hospitals()
        else:
            self.stdout.write('seeding hospital trust data...')
            run_seed()
        self.stdout.write('done.')


def run_seed():
    # this adds all the English hospitals from JSON in the constants folder
    # There are also lists of hospitals across northern ireland, wales and scotland, but the JSON has a different structure
    for index, hospital in enumerate(ALL_HOSPITALS):
        hospital_trust = HospitalTrust(
            OrganisationID=hospital["OrganisationID"],
            OrganisationCode=hospital["OrganisationCode"],
            OrganisationType=hospital["OrganisationType"],
            SubType=hospital["SubType"],
            Sector=hospital["Sector"],
            OrganisationStatus=hospital["OrganisationStatus"],
            IsPimsManaged=hospital["IsPimsManaged"],
            OrganisationName=hospital["OrganisationName"],
            Address1=hospital["Address1"],
            Address2=hospital["Address2"],
            Address3=hospital["Address3"],
            City=hospital["City"],
            County=hospital["County"],
            Postcode=hospital["Postcode"],
            Latitude=hospital["Latitude"],
            Longitude=hospital["Longitude"],
            ParentODSCode=hospital["ParentODSCode"],
            ParentName=hospital["ParentName"],
            Phone=hospital["Phone"],
            Email=hospital["Email"],
            Website=hospital["Website"],
            Fax=hospital["Fax"]
        )
        try:
            hospital_trust.save()
        except:
            print("Exception at "+hospital["OrganisationName"])
        print(f"New hospital added...{index}")
    print(f"Hospitals added...{len(ALL_HOSPITALS)}")


def delete_hospitals():
    try:
        HospitalTrust.objects.all().delete()
    except:
        print("Unable to delete Hospital table")
    print("...all hospitals deleted.")
