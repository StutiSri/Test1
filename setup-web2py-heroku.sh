read -p "Choose your admin password?" passwd
sudo pip install virtualenv
virtualenv venv --distribute
source venv/bin/activate
sudo pip install psycopg2
pip freeze > requirements.txt
echo "web: python web2py.py -a '$passwd' -i 0.0.0.0 -p \$PORT" > Procfile
git init
git add .
git add Procfile
git commit -a -m "first commit"
git push heroku master
heroku config:set AWS_ACCESS_KEY_ID=AKIAJ4LGE7F25ECGBVYQAWS_SECRET_ACCESS_KEY=0hK7uWPqwJBtq5e3k/WR4XqlwjQKMPDloHk56hNy
heroku addons:add heroku-postgresql:hobby-dev
heroku config -s | grep HEROKU_POSTGRESQL
heroku pg:backups restore 'https://s3-ap-southeast-1.amazonaws.com/waochersdumpdb/waochersdump.dump' DATABASE_URL
heroku scale web=1
heroku open
