docker build -t palondomus/revisionbankbackend .
docker push palondomus/revisionbankbackend
git add .
git commit -m "$1"
git push origin
docker run -it -p 8000:8000 palondomus/revisionbankbackend 
