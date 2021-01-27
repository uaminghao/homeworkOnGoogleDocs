import argparse
import json
import pandas as pd


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
    teams = []
    args = parse_arg_list()
    df = pd.read_csv(args.input, index_col=[0])
    cols = df.columns
    for col in cols:
        team = {}
        lastnames = []
        ccids = []
        team['team'] = "Thurs_" + str(col)
        for i in range(1, 15, 3):
            lastnames.append(df.iloc[i][col])
            ccids.append(df.iloc[i+1][col])
        team['lastnames'] = lastnames
        team['ccids'] = ccids
        teams.append(team)
    with open(args.output, 'w') as outfile:
        json.dump(teams, outfile)


if __name__ == '__main__':
    main()