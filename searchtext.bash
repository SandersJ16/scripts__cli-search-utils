#!/bin/bash

####################################################################################################################################
#
# Author: Justin Sanders
#
# This script is a wapper for grep that creates and runs grep commands best suited for searching directories of files for text.
# This was made to shorten common grep commands I would run by adding useful defaults and allow multiple regex searches at once.
# This script was designed with GNU grep in mind and is not very portable as a result since it defaults to using the PCRE regex
# engine not available in most other version of grep.
#
####################################################################################################################################

usage() {
  cat <<EOF
Wrapper for grep, search for regex pattern(s) in file(s)
Usage: searchtext [-pVNS] [-f PATH] [GREP_OPTIONS] PATTERN...

Default path is current directory; At least 1 PATTERN must be supplied;
If multiple PATTERNS are supplied all must match a line for it to display;

Examples:
  Search all files in current directory for lines containing text "goodbye" AND "moon"
    searchtext "goodbye" "moon"
  Search foo.bar file for all lines matching regex "hello.*world"
    searchtext "hello.*world" -f foo.bar
  Search files file1.txt and file2.txt for lines containing "test" case-insentively
    searchtext -i "test" -f "file1.txt" -f "file2.txt"  ()

Options:
  -p                          Print grep command that would be run
  -V                          Include all files (by default special files are ignored)
  -N                          Don't show line numbers
  -S                          Suppress text "done" when search completes
  -M                          Multi-line matching, allows matching \n
  -f PATH                     PATH that will be search
      --help                  Display this help text and exit
Most Grep options supported. Common options are (use grep --help) for all options:
  -i, --ignore-case           Ignore case distinctions
  -v, --invert-match          Select non-matching lines
  -H, --with-filename         Print file name with output lines
  -h, --no-filename           Suppress the file name prefix on output
      --include=FILE_PATTERN  Search only files that match FILE_PATTERN
      --exclude=FILE_PATTERN  Skip files and directories matching FILE_PATTERN
      --exclude-dir=PATTERN   Directories that match PATTERN will be skipped.
Following grep options currently only work when a single PATTERN is supplied:
  -o, --only-matching         Show only the part of a line matching PATTERN
  -L, --files-without-match   Print only names of FILEs with no selected lines
  -l, --files-with-matches    Print only names of FILEs with selected lines
  -B, --before-context=NUM    Print NUM lines of leading context
  -A, --after-context=NUM     Print NUM lines of trailing context
  -C, --context=NUM           Print NUM lines of output context
EOF
}

###########################################
# Initialize Defaults
###########################################

# The executable that will be used as the grep command
grep_executable='grep'
# If line numbers should be shown in the output
show_line_numbers=true
# Default grep options that will be applied, applied to grep for first search term only
default_grep_options="-Isr"
# Single character flag grep options that will be applied, applied to grep for all search terms if more than
base_grep_options="-P"
# Additional single character flag grep options that will be applied, applied to grep for first search term only
extra_grep_options=""
# Multi dash grep options and single character with argument grep options that will be applied
other_grep_options=""
# If the default exclude files should be ignored
exclude_defaults=true
# If the command should be executed or printed
echo_grep_command=false
# Display completed message on completion of search
display_completed_message=true
# Color setting (always, auto, never) to apply to the output
color_setting=auto
# All terms to search for
declare -a search_terms
# locations we want to search, search is always recursive
# Default will be current directory if no values supplied
declare -a search_locations

###########################################
# Parse Arguments
###########################################

while [ "$#" -gt 0 ]; do
    OPTIND=1
    while getopts ":ivMVSNpf:e:m:d:A:B:C:D:-:" opt "$@"; do
      case $opt in
        i|v)
          base_grep_options="${base_grep_options}${opt}"
          ;;
        M)
          grep_executable="pcregrep"
          base_grep_options="-M${base_grep_options:2}" # Replace -P (GNUgrep's PCRE flag) with -M (pcregrep's multi line flag)
          ;;
        V)
          exclude_defaults=false
          ;;
        p)
          echo_grep_command=true
          ;;
        N)
          show_line_numbers=false
          ;;
        f)
          search_locations=("${search_locations[@]}" "${OPTARG}")
          ;;
        S)
          display_completed_message=false
          ;;
        e|m|d|A|B|C|D) # Handle grep options that take an argument
          other_grep_options="$other_grep_options -${opt} ${OPTARG}"
          ;;
        -) # Handle double dash elements
          dd_option="${OPTARG%%=*}"
          [[ "${OPTARG}" == *"="* ]] && dd_value="${OPTARG#*=}" || dd_value=""

          case "$dd_option" in
            help)
              usage
              exit 0
              ;;
            color)
              color_setting="$dd_value"
              allowed_color_settings=("always" "never" "auto")
              if [[ ! " ${allowed_color_settings[@]} "  =~ " ${color_setting} " ]]; then
                echo "Invalid value for color: \"${color_setting}\". Must be one of: ${allowed_color_settings[@]}"
                exit 1
              fi
              ;;
            *) # For all other double dash arguments pass them on as is to grep
              other_grep_options="$other_grep_options --${OPTARG}"
              ;;
          esac
          ;;
        \?)
          extra_grep_options="${extra_grep_options}${OPTARG}"
          ;;
        :)
          echo "Option -$OPTARG requires an argument." >&2
          exit 1
          ;;
      esac
    done
    shift $(($OPTIND - 1)) #remove processed arguments

    # Continue looping through all arguments, store non options in $search_term array
    # This allows us to place options after search terms but still use getopts to process them
    while [[ "$#" -gt 0 ]] && [[ "${1:0:1}" != "-" ]]; do
        search_term=`echo "$1" | sed 's/"/\\\"/g'` # escape double quotes in regex
        search_terms=("${search_terms[@]}" "${search_term}")
        shift # remove processed search terms
    done
done

if [ "${#search_terms[@]}" -eq 0 ]; then
  echo "Must supply at least 1 search term"
  exit 1
fi

# If no search locations supplied user current directory
if [ "${#search_locations[@]}" -eq 0 ]; then
  search_locations=(".")
fi

# If we are only searching for one string or not using auto then use color setting passed in
# otherwise set the color setting to always or never depending on if we are printing to tty/pty
if [[ "${#search_terms[@]}" > 1  && "$color_setting" == auto ]]; then
  if [ -t 1 ]; then
    base_grep_color_setting="always"
  else
    base_grep_color_setting="never"
  fi
else
  base_grep_color_setting="$color_setting"
fi

# Our default is to show line numbers, grep does not have a way
# to override this to false once this option is set so we have created
# our own -N to override it by never setting the -n flag at all
if [ $show_line_numbers == true ]; then
  default_grep_options="${default_grep_options}n"
fi

###########################################
# Build grep Command
###########################################

# Search all non binary files for any regex matching the first search term
# pass any additional command flags to this command as well
grep_command="$grep_executable $default_grep_options --color=$base_grep_color_setting ${base_grep_options}${extra_grep_options} -e \"${search_terms[0]}\" $other_grep_options ${search_locations[@]}"

# Exclude directories and files that are usually not helpful (will not be excluded if -V flag is passed)
if [ $exclude_defaults ==  true ]; then
  declare -a exclude_dirs=(".git" "node_modules" "vendor" "log")
  declare -a exclude_files=(".tags" "*.min.js" "*.mo" "*.po" "jit-yc.js" "*.min.css" "*bundle.js" "*.css.map")

  for exclude_dir in "${exclude_dirs[@]}"; do
    grep_command="$grep_command --exclude-dir=\"$exclude_dir\""
  done

  for exclude_file in "${exclude_files[@]}"; do
    grep_command="$grep_command --exclude=\"$exclude_file\""
  done
fi

# If more than one search term was supplied perform grep on on original results for additional search terms
for (( i=1; i<${#search_terms[@]}; i++ )); do
  search_term="${search_terms[$i]}"

  # If search term starts with ^ then replace the carrot with regex look behind for ":{color code}"
  # this regex is to make carrots match where the beginning of the line would be
  if [[ "$search_term" =~ ^"^".* ]]; then
    search_term="(?<=[:-]\\x1b\\[m\\x1b\\[K)${search_term:1}"
  fi

  # If search term does not end with a $ then add regex look ahead to make sure that what we are
  # matching is in the file contents and not the file name
  if [[ ! "$search_term" =~ .*"$"$ ]]; then
    search_term="${search_term}(?!(.*(\\x1b\\[[0-9;]*[mGKH])[-:](\\x1b\\[[0-9;]*[mGKH])+\d+(\\x1b\\[[0-9;]*[mGKH])+[-:]))"
  fi

  # If this is the last item being searched for use the command's color setting,
  # otherwise use the same color setting as the base grep command
  if [ $i -eq $(("${#search_terms[@]}" - 1)) ]; then
    color="$color_setting"
  else
    color="$base_grep_color_setting"
  fi

  grep_command="$grep_command | $grep_executable ${base_grep_options} -e \"${search_term}\" --color=${color}"
done

###########################################
# Print or Evaluate grep Command
###########################################

if [ $echo_grep_command == true ]; then
  # Print the grep command that would be run intead of running it (Useful for debugging)
  echo "$grep_command"
else
  eval "$grep_command"
  if [ -t 1 ]  && [ $display_completed_message == true ]; then
    echo -e "\e[1;36m---------------------------Done---------------------------\e[0m"
  fi
fi
