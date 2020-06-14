step1 : 
    update "src/bbb_s3_upload.py" , "setupBBBPlayerBucket.py" and bbb_s3_uploadall.py to provide S3 connectivity details and collage ID for API call 

    s3BucketName = '';
    s3BucketRegion ='';
    os.environ["AWS_ACCESS_KEY_ID"] = "";
    os.environ["AWS_SECRET_ACCESS_KEY"] = "";
    querystring = {"collegeId":"some-collegeId"}

setp2 :

    this needs to be run on all BBB servers ( to add Postpublish script) and upload all already existing recordings 
    sudo ./install.sh 
    sudo python3 bbb_s3_uploadall.py 


Step3:
    this needs to be exceuted once only .. this is to setup Bucket with Gneric Popcord Playing setup
    python3 setupBBBPlayerBucket.py
    
    
Note : Deleting of meeting from BBB servers is commented as of now on scripts 