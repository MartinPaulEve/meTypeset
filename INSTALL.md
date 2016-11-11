The following installation instructions were prepared by ppKrauss on November the 11th 2016 and are included here in case they are helpful to other users.

## Preparation
Supposing a server with clean UBUNTU (16.04 LTS), and  supposing *root* user to simplify scripts (if not root, add `sudo` when necessary). All by terminal (typically `ssh user@server`). 

```sh
# exports only if need (to avoid locale warnings from Perl)
export LC_CTYPE=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```
## Basic meTypeset instalation

```sh
# The basic packages (libreoffice, python, etc.) 
add-apt-repository ppa:libreoffice/ppa  # need most recent versions?
apt-get update
apt-get install libreoffice  # there are a "server option?"
apt-get install  python
apt-get install  unzip 

# Specific meTypeset dependences for basic usages 
apt-get install unoconv 
apt-get install python-lxml
```

Checks:
```sh
python --version  # Python 2.7.12
unzip --version   # UnZip 6.00
update-java-alternatives -l # java-1.8.0-openjdk-amd64 
```

Now all ready to download and start meTypeset and check it: 
```sh
cd /usr/local/
git clone https://github.com/MartinPaulEve/meTypeset.git
cd meTypeset
```
Some checks:
```sh
python bin/meTypeset.py  # return help summary
python bin/meTypeset.py docx tests/Sec004.docx /tmp/Sec004 # create output at /tmp!
```
