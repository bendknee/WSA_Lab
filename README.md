# Web Service Finale

## Outline
1. [Installation](#installation)
    1. [Prerequisites](#prerequisites)
    2. [Dependencies](#dependencies)
2. [Usage](#usage)
3. [Changing defaults](#defaults)
4. [Author](#author)

## <a name="installation"></a> Installation 
This service requires root access.
Every instruction from now on will require superuser access with `sudo`.

You can ignore using `sudo` if you are already root: `sudo su -`

1. <a name="prerequisites"></a> Prerequisites 
    1. **Nginx**. Find your UNIX system [here](https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-open-source/) 

    2.  **Pip** (Python package manager)
        ```
        $ sudo apt-get install python3-pip
        ```
  
2. <a name="dependencies"></a> Install python dependencies 
    ```
    $ sudo pip3 install -r requirements.txt
    ```
    > Python environment is not required here since since we'll execute by root anyway 

## <a name="usage"></a> Usage
1. Open terminal and change directory into this source code root directory.
2. Run the service from the script conductor

    ```
    $ sudo bash run.sh
    ```
   > No need to kill the running services whenever you need to restart. The script does it for you.

3. Open up a browser and go to http://{host}:{port}. With host=_localhost_ and port=_20013_, by default.
   > You could use your system's public IP address as the host too.

4. Enter 10 URLs which links to the files that you request to compress altogether.
   
   It is highly recommended to submit a static link with the file extension at the end; _example: http//link.to/the_file.txt_ 
   > Duplicates are perfectly fine.
   
   ![form](https://i.ibb.co/d2H8tkz/Screenshot-from-2020-06-18-19-45-03.png "Fill the form")

5. You will be redirected to a page where you can watch the download and compression progress.

   ![progress](https://i.ibb.co/3vxsBdx/Screenshot-from-2020-06-18-19-46-05.png "Download and compression progress, asynchronously")

   At the end of compression you will receive the link to download your 10 files, compressed into one.

   ![final](https://i.ibb.co/M8BYFPb/Screenshot-from-2020-06-18-19-59-40.png "Link to download final product")

6. The said link will expire in 20 minutes, by default. Any changes to the timestamp and _md5_ parameter will cause a failure in downloading the file.


## <a name="defaults"></a> Changing defaults
You can change some default environment variables at the top of **run.sh** script.
- **FEND_PORT** is the port used by the front end server (server 1)
- **COMPRESS_PORT** is the port used by the compressor server (server 3)
- **SECURE_EXPIRY** is the age of secure links in minutes.

Feel free to change this values should you need it, for example, avoiding port collisions.
But FEND_PORT != COMPRESS_PORT, obviously.

> The service will use /law directory to store static files. 
> If you wish to change this you can change the **ROOT_DIR** value 
> but don't forget to change the value at **nginx.conf, root directive** aswell.

## <a name="author"></a> Author
Benny William Pardede (bpardedewilliam@gmail.com)

