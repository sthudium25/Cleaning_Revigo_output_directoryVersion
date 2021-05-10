import csv
import pandas as pd
from os import chdir, listdir, getcwd, mkdir
from os.path import isdir, abspath, exists, join, split, splitext, basename
import argparse
from collections import Counter


def read_revigo_file(file):
	with open(file, newline='') as f:
		testreader = csv.reader(f, skipinitialspace=True, quotechar='"', quoting=csv.QUOTE_MINIMAL)
		lines = [line for line in testreader]
		dropped = Counter(line[-1] == 'True' for line in lines)
	return lines, dropped


def clean_bad_lines(bad_lines: list) -> list:
	cleaned_lines = bad_lines
	for line in cleaned_lines:
		line[1:3] = [' '.join(line[1:3])]
	for line in cleaned_lines:
		if len(line) != 10:
			raise AttributeError(f'The line, | {line} | is not formatted correctly.')
	print('All bad lines cleaned successfully!!')
	return cleaned_lines


def clean_revigo_df(raw_revigo_df: pd.DataFrame) -> pd.DataFrame:
	revigo = raw_revigo_df.copy()
	revigo.TermID = revigo.TermID.apply(lambda x: x.replace('"', ''))
	revigo.Name = revigo.Name.apply(lambda x: x.replace('"', ''))
	revigo = revigo[revigo.PlotX != "null"]
	revigo.PlotX = revigo.PlotX.astype(float)
	revigo.PlotY = revigo.PlotY.astype(float)
	return revigo

def create_results_folder(inputdir):
	if isdir(args.inputdir):
		chdir(args.inputdir)
		print(f'Current working directory is: {getcwd()}')
	else:
		raise OSError('The provided directory is not in the file system')

	resultsDir = join(abspath(args.inputdir), 'cleanedResults')
	path = resultsDir
	dirs = [d for d in listdir() if isdir(d)]
	print('Base folder name already exists. Creating a new output folder')
	if split(resultsDir)[1] in dirs:
		i = 1
		while exists(path):
			path = f'{resultsDir}_{i}'
			i += 1
	try:
		mkdir(path)
	except OSError:
		print(f'the directory, {resultsDir}, already exists')
	return path

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--inputdir', help='Input directory containing Revigo results to clean')

args = parser.parse_args()

output_folder_path = create_results_folder(args.inputdir)
files = [f for f in listdir() if f.endswith('.csv')]

for file in files:
	good, num_dropped = read_revigo_file(file)
	print('----------------------------------')
	print(f'{file} had {num_dropped[True]} dropped GO terms of {num_dropped[True] + len(good)} total terms')
	col_names = good.pop(0)
	revigo_df = pd.DataFrame(good, columns=[*col_names])
	cleaned_revigo = clean_revigo_df(revigo_df)
	cleaned_revigo.to_csv(path_or_buf=f'{split(output_folder_path)[1]}/{splitext(basename(file))[0]}_cleaned.csv')



