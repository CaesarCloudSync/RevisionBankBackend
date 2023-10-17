docker build -t palondomus/revisionbankbackend .
docker push palondomus/revisionbankbackend
docker run -it -p 8000:8000 palondomus/revisionbankbackend 
git add .
git commit -m "$1"
git push origin master:main