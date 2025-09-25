#!/bin/bash
image="revisionbankbackend"

function getVersions() {
    IN=$(cat main.tf | grep palondomus/$image)
    arrIN=(${IN//:/ })
    oldv=$((${arrIN[3]::-1}))
    newv=$(($oldv+1))
    echo $oldv $newv
}



# Change Docker tag in .tf
read -r oldv newv  <<< $(getVersions)
sed -i -e "s/$image:$oldv/$image:$newv/" main.tf



# Push Docker
docker build -t palondomus/$image:$newv .
docker push palondomus/$image:$newv


# Test application
docker run -it -p 8080:8080 palondomus/$image:$newv






