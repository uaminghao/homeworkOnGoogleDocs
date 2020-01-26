import argparse
import csv
import json

TEAM = 2

def parse_arg_list():
    """Uses argparse to parse the required parameters

    :returns: command line arguments.
    """
    parser = argparse.ArgumentParser(description='Creates a JSON file with the format required by the `create_and_share_google_docs` script.\n' +
        'Requires the teams csv input file name and an output JSON file name.',
        formatter_class=argparse.RawTextHelpFormatter)
    requiredArgs = parser.add_argument_group('required arguments')
    requiredArgs.add_argument('-i', '--input', help='csv file with teams details', required=True)
    requiredArgs.add_argument('-o', '--output', help='output JSON file name', required=True)

    args = parser.parse_args()
    return args

def main():
  args = parse_arg_list()

  teams = []
  with open(args.input) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for i, row in enumerate(csv_reader):
      if i > 1:
        team = {}
        team['team'] = row[TEAM]
        team['ccids'] = []
        team['surnames'] = []
        for j in range(TEAM + 1, len(row)):
          if j % 2 == 0 and row[j]:
            team['ccids'].append(row[j].lower())
          elif j % 2 == 1 and row[j]:
            team['surnames'].append(row[j].split()[-1])
        teams.append(team)

  with open(args.output, 'w') as outfile:
    json.dump(teams, outfile)

if __name__ == '__main__':
    main()