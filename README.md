## Toneprint Server

If you are a user of the TC Electronic toneprint series of effects pedals you  know about how versatile they are.

And with the Toneprint editor they are even more, with this software you can edit a lot of hidden settings of the pedals.

There is only one limitation, you can only edit the template toneprints. And not the artists toneprints.

This will allow that.

### Why?

The toneprints data is stored in an encrypted sqlite (```~/Library/Application Support/TonePrint/databaseV1.sqlite3```)

That database is populated with the content of this 6 XML files located in ```~/Library/Application Support/TonePrint/XML```

- artists.xml
- effects.xml
- products.xml
- producttypes.xml
- selecttypes.xml
- toneprints.xml

In older versions of the software I believe you can just edit the xml and that lead to the modification of the databse.

But now it will download them from the cloud and only then it will update de database. So modify them has no effect.

So I came with this solution after tried to find how to decrypt the database with a debugger (I came very close, but I gave up).

Without direct access to the database our only possibility is to feed modified xmls to the app, so I have created a fake server.

### How it works?

This will create a fake server so the app thinks it is connected to the tcelectronic server and download the modified xmls.
With the modified files it will update the database.

The change is very simple, you just need to change the ```CanBeEdited``` value of the artist to ```True```

And you will be allowed to edit every toneprint.

### How to use it?

In order to this to work you will need to do 2 thins before

1. You will need to redirect the domain ```tp.tcelectronic.com``` to localhost in the ```/etc/hosts```
2. You will need to create a selfsigned certificate for that domain, put the files in the ```ssl``` folder and install the ```cert.pem``` (be sure to select to trust it). 
   
Example how to create it, just be sure to enter ```tp.tcelectronic.com```  as the common name.
```
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

Now with the traffic redirected to localhost and the certificate installed you are ready to start the server.

***Because it needs to listen on the port 443 you will need to run it as root, or you can use nginx or some webserver but it's a lot of work just to do this.***

```
sudo ./app.py
```

You have some options
```
Options:
  -h, --host TEXT     Listen host  [default: 0.0.0.0]
  -p, --port INTEGER  Listen port  [default: 443]
  --cert PATH         Certificate File  [default: ssl/cert.pem]
  --key PATH          Key File  [default: ssl/key.pem]
  --static-xml        Serve static XML
  --debug             Debug mode
  --help              Show this message and exit.
  ```

### XML options

You have two options, by default when you run the server it will download all the xml from the TC Electronic server.
Then it will apply a patch to enable the edit mode, and will serve that xml.

Or you can serve your own modified xml with the parameter ```--static-xml```.

The only problem with patch the xml in real time is because you need to add ```tp.tcelectronic.com``` to the hosts file it will not be able to connect to it.

That its why I added a docker file, because in that way you can use different dns in the container (or run the server in a VM).

### Use it with docker

***Build***
```
docker build -t toneprint --rm .

or

docker-compose build
```

***Run***
```
docker run --rm --dns=8.8.8.8 -p 443:443 --name toneprint toneprint
```

Or if you want to serve the static XML and try things (you don't need to use the ```--dns``` option this way)

```
docker run --rm -p 443:443 -v $(pwd)/src/xml:/app/xml --name toneprint toneprint --static-xml
```

Keep in mind that no matter if you use the static xml or the patched online, the reponse is cached.

So if you modify the xml by hand you will need to restart it.


If every thing is ok you will see this when the app connects and download the files

```
-2021-06-06 21:37:54,583 - __main__ - INFO - --------------------------------------
2021-06-06 21:37:54,583 - __main__ - INFO - Request for Action:GetVersionsAndInfo
2021-06-06 21:37:54,583 - __main__ - DEBUG - Headers: Host: tp.tcelectronic.com
Content-Type: text/xml; charset=utf-8
Connection: keep-alive
Soapaction: "http://tempuri.org/ITonePrintService/GetVersionsAndInfo"
Accept: */*
Accept-Language: es-es
Content-Length: 176
Accept-Encoding: br, gzip, deflate
User-Agent: TonePrint/4.2.0 CFNetwork/902.6 Darwin/17.7.0 (x86_64)


2021-06-06 21:37:54,584 - werkzeug - INFO - 172.17.0.1 - - [06/Jun/2021 21:37:54] "POST /TonePrintService.svc HTTP/1.1" 200 -
2021-06-06 21:37:54,837 - __main__ - INFO - --------------------------------------
2021-06-06 21:37:54,838 - __main__ - INFO - Request for Action:GetAllToneprintsFullBeta
2021-06-06 21:37:54,839 - __main__ - DEBUG - Headers: Host: tp.tcelectronic.com
Content-Type: text/xml; charset=utf-8
Connection: keep-alive
Soapaction: "http://tempuri.org/ITonePrintService/GetAllToneprintsFullBeta"
Accept: */*
Accept-Language: es-es
Content-Length: 212
Accept-Encoding: br, gzip, deflate
User-Agent: TonePrint/4.2.0 CFNetwork/902.6 Darwin/17.7.0 (x86_64)


2021-06-06 21:37:54,856 - werkzeug - INFO - 172.17.0.1 - - [06/Jun/2021 21:37:54] "POST /TonePrintService.svc HTTP/1.1" 200 -
2021-06-06 21:37:55,704 - __main__ - INFO - --------------------------------------
2021-06-06 21:37:55,705 - __main__ - INFO - Request for Action:GetAllArtistsFullBeta
2021-06-06 21:37:55,706 - __main__ - DEBUG - Headers: Host: tp.tcelectronic.com
Content-Type: text/xml; charset=utf-8
Connection: keep-alive
Soapaction: "http://tempuri.org/ITonePrintService/GetAllArtistsFullBeta"
Accept: */*
Accept-Language: es-es
Content-Length: 206
Accept-Encoding: br, gzip, deflate
User-Agent: TonePrint/4.2.0 CFNetwork/902.6 Darwin/17.7.0 (x86_64)


2021-06-06 21:37:55,707 - werkzeug - INFO - 172.17.0.1 - - [06/Jun/2021 21:37:55] "POST /TonePrintService.svc HTTP/1.1" 200 -
2021-06-06 21:37:55,767 - __main__ - INFO - --------------------------------------
2021-06-06 21:37:55,768 - __main__ - INFO - Request for Action:GetAllProductsFullBeta
2021-06-06 21:37:55,769 - __main__ - DEBUG - Headers: Host: tp.tcelectronic.com
Content-Type: text/xml; charset=utf-8
Connection: keep-alive
Soapaction: "http://tempuri.org/ITonePrintService/GetAllProductsFullBeta"
Accept: */*
Accept-Language: es-es
Content-Length: 208
Accept-Encoding: br, gzip, deflate
User-Agent: TonePrint/4.2.0 CFNetwork/902.6 Darwin/17.7.0 (x86_64)


2021-06-06 21:37:55,771 - werkzeug - INFO - 172.17.0.1 - - [06/Jun/2021 21:37:55] "POST /TonePrintService.svc HTTP/1.1" 200 -
2021-06-06 21:37:55,818 - __main__ - INFO - --------------------------------------
2021-06-06 21:37:55,819 - __main__ - INFO - Request for Action:GetAllEffectsFullBeta
2021-06-06 21:37:55,820 - __main__ - DEBUG - Headers: Host: tp.tcelectronic.com
Content-Type: text/xml; charset=utf-8
Connection: keep-alive
Soapaction: "http://tempuri.org/ITonePrintService/GetAllEffectsFullBeta"
Accept: */*
Accept-Language: es-es
Content-Length: 206
Accept-Encoding: br, gzip, deflate
User-Agent: TonePrint/4.2.0 CFNetwork/902.6 Darwin/17.7.0 (x86_64)


2021-06-06 21:37:55,821 - werkzeug - INFO - 172.17.0.1 - - [06/Jun/2021 21:37:55] "POST /TonePrintService.svc HTTP/1.1" 200 -
2021-06-06 21:37:55,861 - __main__ - INFO - --------------------------------------
2021-06-06 21:37:55,861 - __main__ - INFO - Request for Action:GetAllProductTypesFull
2021-06-06 21:37:55,862 - __main__ - DEBUG - Headers: Host: tp.tcelectronic.com
Content-Type: text/xml; charset=utf-8
Connection: keep-alive
Soapaction: "http://tempuri.org/ITonePrintService/GetAllProductTypesFull"
Accept: */*
Accept-Language: es-es
Content-Length: 208
Accept-Encoding: br, gzip, deflate
User-Agent: TonePrint/4.2.0 CFNetwork/902.6 Darwin/17.7.0 (x86_64)


2021-06-06 21:37:55,862 - werkzeug - INFO - 172.17.0.1 - - [06/Jun/2021 21:37:55] "POST /TonePrintService.svc HTTP/1.1" 200 -
2021-06-06 21:37:55,901 - __main__ - INFO - --------------------------------------
2021-06-06 21:37:55,901 - __main__ - INFO - Request for Action:GetAllSelectTypes
2021-06-06 21:37:55,902 - __main__ - DEBUG - Headers: Host: tp.tcelectronic.com
Content-Type: text/xml; charset=utf-8
Connection: keep-alive
Soapaction: "http://tempuri.org/ITonePrintService/GetAllSelectTypes"
Accept: */*
Accept-Language: es-es
Content-Length: 198
Accept-Encoding: br, gzip, deflate
User-Agent: TonePrint/4.2.0 CFNetwork/902.6 Darwin/17.7.0 (x86_64)


2021-06-06 21:37:55,903 - werkzeug - INFO - 172.17.0.1 - - [06/Jun/2021 21:37:55] "POST /TonePrintService.svc HTTP/1.1" 200 -
```

![Example](./media/edit_enabled.jpg)

The xml files in the xml folder already have the modification to enable artists toneprint edit

***In the original_xml folder you will have the unmodified xml files in case you brake something***


***This is made for Mac but it should work on Windows***
