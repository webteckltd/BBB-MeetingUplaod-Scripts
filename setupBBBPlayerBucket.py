
import boto3
import os
import time
import pathlib


s3BucketName = '';
s3BucketRegion ='';
os.environ["AWS_ACCESS_KEY_ID"] = "";
os.environ["AWS_SECRET_ACCESS_KEY"] = "";


def upload_folder_to_s3(s3bucket, inputDir):
    print("Uploading results to s3 initiated...");
    os.system("ls -ltR " + inputDir)
    try:
        for path, subdirs, files in os.walk(inputDir):
            for file in files:
                dest_path = path.replace(inputDir,"")
                if dest_path and dest_path.strip():
                   __s3file = os.path.normpath(dest_path + '/' + file)
                else:
                   __s3file = os.path.normpath(file) 
                   
                __local_file = os.path.join(path, file)
                print("upload : " +  __local_file + "  to Target: " +  __s3file);
                
                extension = os.path.splitext(file)[1][1:].strip()
                if(extension == 'js'):
                  s3bucket.upload_file(__local_file, __s3file,ExtraArgs={'ContentType': "application/javascript"})
                elif(extension == 'css'):
                  s3bucket.upload_file(__local_file, __s3file,ExtraArgs={'ContentType': "text/css"})
                elif(extension == 'html'):
                  s3bucket.upload_file(__local_file, __s3file,ExtraArgs={'ContentType': "text/html"})
                elif(extension == 'png'):
                  s3bucket.upload_file(__local_file, __s3file,ExtraArgs={'ContentType': "image/png"})                         
                else:  
                  s3bucket.upload_file(__local_file, __s3file)                                  
                print(" Uplaod ...Success");
    except Exception as e:
        print(" ... Failed!! Quitting Upload!!");


def main():
    current_dir = pathlib.Path(__file__).parent ;
    current_dir.__str__()
    source_dir =   current_dir.__str__() + '/2.0/' ;
    print("\n<-------------------" + time.strftime("%c") + "----------------------->\n");
    s3 = boto3.resource('s3', region_name=s3BucketRegion);
    s3bucket = s3.Bucket(s3BucketName);
    upload_folder_to_s3(s3bucket, source_dir);

if __name__ == "__main__":
    main()
