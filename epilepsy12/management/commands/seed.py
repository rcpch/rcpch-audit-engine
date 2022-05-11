from django.core.management.base import BaseCommand
from ...models import HospitalTrust, Keyword
from ...constants import ALL_HOSPITALS, KEYWORDS


class Command(BaseCommand):
    help = "seed database with hospital trust data for testing and development."

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help="Mode")

    def handle(self, *args, **options):
        if (options['mode'] == 'delete_hospitals'):
            self.stdout.write('Deleting hospital trust data...')
            delete_hospitals()
        elif (options['mode'] == 'seed_hospitals'):
            self.stdout.write('seeding hospital trust data...')
            run_hospitals_seed()
        elif (options['mode'] == 'seed_semiology_keywords'):
            self.stdout.write('seeding hospital trust data...')
            run_semiology_keywords_seed()
        else:
            self.stdout.write('No options supplied...')
        self.stdout.write(image())
        self.stdout.write('done.')


def run_semiology_keywords_seed():
    added = 0
    for index, semiology_keyword in enumerate(KEYWORDS):
        new_keyword = Keyword(
            keyword=semiology_keyword["title"],
            category=semiology_keyword["category"]
        )
        try:
            new_keyword.save()
        except Exception as e:
            print(f"Error at {semiology_keyword['title']}: error: {e}")
        added += 1
        print(
            f"added {semiology_keyword['title']} in category {semiology_keyword['category']}")
    image()
    print(f"Keywords added: {added}")


def run_hospitals_seed():
    # this adds all the English hospitals from JSON in the constants folder
    # There are also lists of hospitals across northern ireland, wales and scotland, but the JSON has a different structure
    added = 0
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
        except Exception as error:
            print("Exception at "+hospital["OrganisationName"])
            print(error)
        added += 1
        chosen_hospital = hospital["OrganisationName"]
        print(f"New hospital added...{added}: {chosen_hospital}")
    print(f"Hospitals added...{added}")


def delete_hospitals():
    try:
        HospitalTrust.objects.all().delete()
    except:
        print("Unable to delete Hospital table")
    print("...all hospitals deleted.")


def image():
    return """

                                .^~^      ^777777!~:       ^!???7~:       
                                ^JJJ:.:!^ 7#BGPPPGBGY:   !5BBGPPGBBY.     
                                 :~!!?J~. !BBJ    YBB?  ?BB5~.  .~J^      
                              .:~7?JJ?:   !BBY^~~!PBB~ .GBG:              
                              .~!?JJJJ^   !BBGGGBBBY^  .PBG^              
                                 ?J~~7?:  !BBJ.:?BB5^   ~GBG?^:^~JP7      
                                :?:   .   !BBJ   ~PBG?.  :?PBBBBBG5!   
                                ..::...     .::. ...:^::. .. .:^~~^:.       
                                !GPGGGGPY7.   :!?JJJJ?7~..PGP:    !GGJ      
                                7BBY~~!YBBY  !JJ?!^^^!??::GBG:    7BBJ      
                                7BB?   .GBG.^JJ7.     .. .GBG!^^^^JBBJ      
                                7BB577?5BBJ ~JJ!         .GBBGGGGGGBBJ      
                                7BBGPPP5J~  :JJJ^.   .^^ .GBG^.::.?BBJ      
                                7#B?         :7JJ?77?JJ?^:GBB:    7##Y      
                                ~YY!           :~!77!!^. .JYJ.    ~YY7      


    @@@@@@@@ @@@@@@@@%  *@@@@ @@@@@   .@@@@@@@% @@@@@@@@%   -@@@@@@@. *@@@%  @@@@=    :::   .::::::.   
    @@@@@@@@ @@@@@@@@@% *@@@@ @@@@@   .@@@@@@@% @@@@@@@@@@ :@@@@@@@@@  @@@@  @@@@.  .::::  .::::::::.  
    @@@@@@@@ @@@@@@@@@@:+@@@@ @@@@@   .@@@@@@@% @@@@@@@@@@-%@@@%-@@@@- %@@@: @@@# .::::::  ::::::::::  
    @@@@%=== @@@@+ +@@@**@@@@ @@@@@   .@@@@%=+= @@@@* %@@@+%@@@# @@@@+ :@@@=.@@@=::::::::  ::::. ::::. 
    @@@@#    @@@@+ =@@@**@@@@ @@@@@   .@@@@%    @@@@* *@@@+%@@@# @@@@*  @@@**@@@ ......::  ..:: ..:.:  
    @@@@*    @@@@+ +@@@**@@@@ @@@@@   .@@@@%    @@@@* *@@@+%@@@@:       %@@@%@@@    :....  .... :.:..  
    @@@@#--: @@@@+ +@@@**@@@@ @@@@@   .@@@@%--- @@@@* #@@@+=@@@@@#      +@@@@@@*    .....       .....  
    @@@@@@@# @@@@@@@@@@-+@@@@ @@@@@   .@@@@@@@% @@@@@@%@@@= @@@@@@@-    :@@@@@@     .....      ......  
    @@@@@@@# @@@@@@@@@@ +@@@@ @@@@@   .@@@@@@@% @@@@@@@@@@  .%@@@@@@+    @@@@@@     .....      .....   
    @@@@@@@# @@@@@@@@@: +@@@@ @@@@@   .@@@@@@@% @@@@@@@@@     *@@@@@@    %@@@@@     .....     .....    
    @@@@*    @@@@*.     +@@@@ @@@@@   .@@@@#    @@@@*.         .%@@@@+   #@@@@*     .....    ......    
    @@@@*    @@@@+      +@@@@ @@@@@   .@@@@#    @@@@*      @@@@# @@@@#   -@@@@-     .....    .....     
    @@@@*    @@@@+      +@@@@ @@@@@   .@@@@#    @@@@*      @@@@* @@@@@    @@@@:     .....   .....      
    @@@@*    @@@@+      +@@@@ @@@@@   .@@@@%    @@@@*      %@@@# @@@@@    @@@@.     .....   .....       
    @@@@@@@@ @@@@+      +@@@@ @@@@@@@@.@@@@@@@@ @@@@*      %@@@%:@@@@#    @@@@.     .....  ..........            
    @@@@@@@@ @@@@+      +@@@@ @@@@@@@@.@@@@@@@@ @@@@*      +@@@@@@@@@-    @@@@.     .....  ..........
    @@@@@@@@ @@@@+      +@@@@ @@@@@@@@.@@@@@@@@ @@@@*       #@@@@@@@+     @@@@.     .....  ..........                        

                """
