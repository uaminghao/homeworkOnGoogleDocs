import argparse
import csv
import json

FIRST_NAME = 0
SURNAME = 1
EMAIL = 2
STUDENT_ID = 3
CCID = 4

def parse_arg_list():
    """Uses argparse to parse the required parameters

    :returns: command line arguments.
    """
    parser = argparse.ArgumentParser(description='Creates a JSON file with the format required by the `create_and_share_google_docs` script.\n' +
        'Requires the students csv input file name and an output JSON file name.',
        formatter_class=argparse.RawTextHelpFormatter)
    requiredArgs = parser.add_argument_group('required arguments')
    requiredArgs.add_argument('-i', '--input', help='csv file with student details, retrieved from eClass', required=True)
    requiredArgs.add_argument('-o', '--output', help='output JSON file name', required=True)

    args = parser.parse_args()
    return args

def main():
  args = parse_arg_list()

  students = []
  with open(args.input) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for i, row in enumerate(csv_reader):
      if i != 0:
        student = {}
        student['prename'] = row[FIRST_NAME]
        student['surname'] = row[SURNAME]
        student['email'] = row[EMAIL]
        student['student_id'] = row[STUDENT_ID]
        student['ccid'] = row[CCID]
        students.append(student)

  with open(args.output, 'w') as outfile:
    json.dump(students, outfile)

if __name__ == '__main__':
    main()