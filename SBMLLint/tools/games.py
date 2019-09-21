"""
Runs the GAMES algorithm for a local XML file.
Usage: games <filepath>
"""

from SBMLLint.tools import sbmllint

import argparse

def main():
  parser = argparse.ArgumentParser(description='SBML XML file.')
  parser.add_argument('filename', type=str, help='SBML file')
  args = parser.parse_args()
  sbmllint.lint(args.filename, mass_balance_check=sbmllint.GAMES)


if __name__ == '__main__':
  main()