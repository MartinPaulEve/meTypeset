
_meTypesetpy()
{
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $( compgen -W ' tei docx doc odt docxextracted other bibscan' -- $cur) )
    elif [ $COMP_CWORD -eq 2 ]; then
        COMPREPLY=( $(compgen -f ${cur}) )
    elif [ $COMP_CWORD -eq 3 ]; then
        COMPREPLY=( $(compgen -d ${cur}) )
	elif [ $COMP_CWORD -ge 3 ]; then
		COMPREPLY=( $(compgen -W '-a --aggression --chain -c --clean -d --debug -i --identifiers -h --help -m --metadata --nogit --noimageprocessing --nolink --purenlm --puretei --prettytei -p --proprietary -s --settings -v --version' -- $cur) )
    fi
}

complete -F _meTypesetpy meTypeset.py
