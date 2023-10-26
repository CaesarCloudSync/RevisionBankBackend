docker build -t palondomus/revisionbankbackendsql .
docker push palondomus/revisionbankbackendsql
git add .
git commit -m "$1"
git push origin
docker run -it -p 8000:8000 palondomus/revisionbankbackendsql
