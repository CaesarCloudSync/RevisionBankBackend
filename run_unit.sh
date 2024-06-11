if [[ $1 == "" ]]
then
  python -m unittest revisionbankunit.RevisionBankUnittest
else
  python -m unittest revisionbankunit.RevisionBankUnittest.$1
fi