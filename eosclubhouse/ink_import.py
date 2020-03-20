# script for importing csv data into ink format
import csv
import os
import datetime

string_files_path = os.path.expanduser("~/clubhouse/data/quests_strings/")
current_time = datetime.datetime.now().strftime("%M%S")
dumpdir = current_time + "_stringdump"

try:
    os.mkdir(dumpdir)
except Exception:
    print("something went wrong with mkdir")
else:
    file_list = os.listdir(string_files_path)
    print("dumping these files to ink-friendly text: \n")
    print(file_list)
    print("\n")

    for rawfile in file_list:
        file_to_dump = string_files_path + rawfile
        print("now dumping" + file_to_dump)

        csv_file = csv.reader(open(file_to_dump))

        stringlist = []
        for row in csv_file:
            stringlist.append(" -" + row[1] + "\n")

        dumped_strings_filename = os.path.join(os.getcwd(), dumpdir, rawfile)
        dumped_string_fileobj = open(dumped_strings_filename + "_dumpedstrings.txt", "a")
        for entry in stringlist:
            dumped_string_fileobj.write(entry)
        dumped_string_fileobj.close()
