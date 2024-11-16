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
    }

	location / {
	    	proxy_pass   http://parser_hackaton;
    		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
   		proxy_set_header Host $host;
   		proxy_redirect off;
	}

}


