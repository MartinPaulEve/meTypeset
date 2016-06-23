
_meTypeset()
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
					COMPREPLY=( $(compgen -W '-a --aggression --chain -c --clean -d --debug -h --help -i --identifiers --interactive -m --metadata --nogit --noimageprocessing --nolink --nometa --purenlm --puretei --prettytei -p --proprietary -s --settings -v --version -z --zotero' -- $cur) )
				fi
			;;
		esac
    fi
}

_reLinker()
{
    local cur prev first proceed
    first="${COMP_WORDS[1]}"
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
	proceed='FALSE'

    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $( compgen -W ' scan link prune' -- $cur) )
	else
		if [ "$first" == "scan" ]; then
			if [ $COMP_CWORD -eq 2 ]; then
				COMPREPLY=( $(compgen -f ${cur}) )
			elif [ $COMP_CWORD -ge 3 ]; then
				proceed="TRUE"
			fi
		elif [ "$first" == "link" ]; then
			if [ $COMP_CWORD -eq 2 ]; then
				COMPREPLY=( $(compgen -f ${cur}) )
			elif [ $COMP_CWORD -ge 5 ]; then
				proceed="TRUE"
			fi
		elif [ "$first" == 'prune' ]; then
			if [ $COMP_CWORD -eq 2 ]; then
				COMPREPLY=( $(compgen -f ${cur}) )
			elif [ $COMP_CWORD -ge 3 ]; then
				proceed="TRUE"
			fi
		fi
		
		if [ "$proceed" == "TRUE" ]; then
			COMPREPLY=( $(compgen -W '-d --debug -h --help --interactive -v --version -z --zotero' -- $cur) )
		fi
    fi
}

_nlm()
{
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $( compgen -W ' process' -- $cur) )
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
				if [ $COMP_CWORD -ge 2 ]; then
					COMPREPLY=( $(compgen -W '-a --aggression --chain -c --clean -d --debug -h --help -i --identifiers --nogit --noimageprocessing --nometa -s --settings -v --version -z --zotero' -- $cur) )
				fi
			;;
		esac
    fi
}

complete -F _meTypeset meTypeset.py
complete -F _reLinker referencelinker.py
complete -F _nlm nlmprocessor.py
