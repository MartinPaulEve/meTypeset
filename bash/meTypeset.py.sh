
_meTypesetpy()
{
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $( compgen -W ' tei docx doc odt docxextracted other bibscan' -- $cur) )
	else
		case $prev in
			--agression)
			;;
			-a)
			;;
			--chain)
				COMPREPLY=( $(compgen -f ${cur}) )
			;;
			--metadata)
				COMPREPLY=( $(compgen -f ${cur}) )
			;;
			-m)
				COMPREPLY=( $(compgen -f ${cur}) )
			;;
			--settings)
				COMPREPLY=( $(compgen -f ${cur}) )
			;;
			-s)
				COMPREPLY=( $(compgen -f ${cur}) )
			;;
			*)
				if [ $COMP_CWORD -eq 2 ]; then
					COMPREPLY=( $(compgen -f ${cur}) )
				elif [ $COMP_CWORD -eq 3 ]; then
					COMPREPLY=( $(compgen -d ${cur}) )
				elif [ $COMP_CWORD -ge 4 ]; then
					COMPREPLY=( $(compgen -W '-a --aggression --chain -c --clean -d --debug -i --identifiers -h --help -m --metadata --nogit --noimageprocessing --nolink --purenlm --puretei --prettytei -p --proprietary -s --settings -v --version' -- $cur) )
				fi
			;;
		esac
    fi
}

complete -F _meTypesetpy meTypeset.py
