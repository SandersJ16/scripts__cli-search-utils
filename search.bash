#!/bin/bash

print_usage() {
    cat <<EOF
Search For any folders or files located in the current directory or subdirectory that contain the regex PATTERNs
Usage: search [OPTION]... PATTERN [ADDITIONAL_PATTERNS]...
ex. search -i "hello" "world"

   -i           Make search case insensitive
   -a           Match on full path instead of just directory or file name
   -d           Display only matching directories
   -f           Display only matching files
   -A           Match all file in all subdirectories (don't ignore special directories)
   -h, --help   displays basic help
   -L           Follow symlinks (default will follow symlinks)
   -l           Don't follow symlinks, opposite of -L
       --color  One of always, never or auto (auto is default)
EOF
}

case_insensitive=false
find_limiter='-type d -printf "%p/\n" -o -type f -print'
full_path_search=false
exclude_special_folders_content=true
print_command=false
follow_symlinks=true
color_setting="auto"

declare -a search_terms

while [ "$#" -gt 0 ]; do
    OPTIND=1
    while getopts ":hidfnapAl-:" opt; do
      case $opt in
        i)
          case_insensitive=true
          ;;
        d)
          find_limiter='-type d -printf "%p/\n"'
          ;;
        f)
          find_limiter="-type f"
          ;;
        a)
          full_path_search=true
          ;;
        A)
          exclude_special_folders_content=false
          ;;
        p)
          print_command=true
          ;;
        L)
          follow_symlinks=true
          ;;
        l)
          follow_symlinks=false
          ;;
        h)
          print_usage
          exit 0
          ;;
        -) # Handle double dash elements
          dd_option="${OPTARG%%=*}"
          [[ "${OPTARG}" == *"="* ]] && dd_value="${OPTARG#*=}" || dd_value=""

          case "$dd_option" in
            help)
              print_usage
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
            *)
              echo "Invalid option: --$OPTARG" >&2
              exit 1
              ;;
          esac
          ;;
        \?)
          echo "Invalid option: -$OPTARG" >&2
          exit 1
          ;;
        :)
          echo "Option -$OPTARG requires an argument." >&2
          exit 1
          ;;
      esac
    done
    shift $(($OPTIND - 1)) #remove processed arguments

    # Continue looping through all arguments, store non options in $arguments array
    # This allows us to place options after arguments but still use getopts to process them
    while [[ "$#" -gt 0 ]] && [[ "${1:0:1}" != "-" ]]; do
        search_terms=("${search_terms[@]}" "$1")
        shift #remove processed arguments
    done
done

# If there were no arguments exit
if [ "${#search_terms[@]}" -eq 0 ]; then
    echo "No search terms given"
    exit 1
fi

# Set case insensitive logic
if [[ "$case_insensitive" == false ]]; then
    find_type="regex"
    grep_command_modifiers=""
else
    find_type="iregex"
    grep_command_modifiers="i"
fi

# Build find command search terms
find_terms=""
for (( i=0; i<${#search_terms[@]}; i++ )); do
    search_term="${search_terms[$i]}"

    # Replace trailing $ with $ or forward slash (grep will take over from there)
    if [[ "${search_term}" == *$ ]]; then
        search_term="${search_term::-1}(/|$)"
    fi

    # Replace ^ with forward slash (grep will take over from there)
    if [[ "${search_term}" == ^* ]]; then
        search_term="/${search_term:1}"
    fi

    # If we are not searching the entire path, make sure the matched file/directory
    # is the last one in the path. This is needed because `find -regex` matches the
    # regex against the entire path and not the file
    if [[ "$full_path_search" == true ]]; then
        trailing_regex=".*"
    else
        trailing_regex="[^/]*"
    fi

    # If we have multiple terms add a space between them
    if [ ! -z "$find_terms" ]; then
        find_terms="${find_terms} "
    fi

    find_terms="${find_terms}-${find_type} \".*${search_term}${trailing_regex}\""
done

# Special folders that should be exclude from the
find_exclude=""
if [[ "$exclude_special_folders_content" == true ]]; then
    special_folders=(".git")
    for special_file in "${special_folders[@]}"; do
       find_exclude=`printf "%s -not -path \"*/%s/*\"" "${find_exclude}" "${special_file}"`
    done
fi

# Figure out additional flags to set for find command
extra_find_args=""
if [[ "$follow_symlinks" == true ]]; then
    extra_find_args="${extra_find_args}L"
fi

if [ ! -z "$extra_find_args" ]; then
    extra_find_args="-${extra_find_args}"
fi

# Build find command
find_command="find ${extra_find_args} . -regextype posix-extended ${find_terms} ${find_exclude} \( ${find_limiter} \) 2>/dev/null"

# For each search term supplied colour the matching results
colourize_command=''
if [[ "$color_setting" != "never" ]]; then
    grep_search_string=''
    # Build grep search string
    for (( i=0; i<${#search_terms[@]}; i++ )); do
        search_term="${search_terms[$i]}"

        if [[ "$full_path_search" == true ]]; then
            if [[ "${search_term}" == *$ ]]; then
                search_term="${search_term::-1}"
                regex_modifer="(?=/|$)"
            else
                regex_modifer=""
            fi
        else
            if [[ "${search_term}" == *$ ]]; then
                search_term="${search_term::-1}"
                regex_modifer="(?=/?$)"
            else
                regex_modifer="(?=[^/]*/?$)"
            fi
        fi

        # If a search term begins with
        if [[ "${search_term}" == ^* ]]; then
            search_term="(?<=/)${search_term:1}"
        fi

        # Figure out color setting for grep command
        if [[ "${color_setting}" == "auto" ]]; then
            if [ -t 1 ]; then
                grep_color_setting="always"
            else
                grep_color_setting="never"
            fi
        else
            grep_color_setting="$color_setting"
        fi

        # Combine multiple regexes to grep for with |
        if [ ! -z "$grep_search_string" ]; then
            grep_search_string="${grep_search_string}|"
        fi
        grep_search_string="${grep_search_string}${search_term}${regex_modifer}"
    done

    # Append grep command to end of current command to color results, (We add `|$` to make sure that grep doesn't actually
    # exclude any lines as it will match everything. We only want grep to color the output, `find` should be doing the filtering)
    colourize_command=" | grep -P${grep_command_modifiers}e \"${grep_search_string}|$\" --color=${grep_color_setting}"
fi

if [ $print_command == true ];then
  echo "${find_command}${colourize_command}"
else
  eval "${find_command}${colourize_command}"
fi
