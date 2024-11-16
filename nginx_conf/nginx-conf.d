 upstream parser_hackaton{
	 server django:8001;
}


server {
	listen 83;
	server_name  parser_hackatons;
	location /static/ {
		alias /server/staticfiles/;
	}

    location /tma {
        alias /server/tma;
        index index.html;
        try_files $uri $uri/ /tma/index.html;
    }

	location / {
        add_header Access-Control-Allow-Origin *;

   		if ($request_method = OPTIONS) {
                   add_header Content-Type text/plain;
                   # add_header Access-Control-Allow-Origin *;
                   add_header Access-Control-Allow-Headers 'Authorization, Content-Type';
                   add_header Access-Control-Allow-Methods 'OPTIONS, GET, POST, PUT, PATCH, DELETE';
                   return 200;
        }

        proxy_pass   http://parser_hackaton;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
	}

}


