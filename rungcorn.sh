#nginx 
gunicorn crams_app.wsgi --bind=127.0.0.1:8001

echo ##################### gUnicorn / nginx setup ###############################################################
echo    Make sure the following is added to nginx.conf file   : normally in /usr/local/etc/nginx/nginx.conf
echo            location /vicnode {
echo                  alias /Users/work/projects/vicnode/crams_app/static;
echo            }
Echo            location / {
echo                  proxy_pass http://localhost:8001/;
echo             }
Echo ############################################################################################################
