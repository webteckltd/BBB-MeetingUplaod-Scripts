
import boto3
import os
import sys
import time
import pathlib
import xml.dom.minidom
import json 
import requests


s3BucketName = '';
s3BucketRegion ='';
os.environ["AWS_ACCESS_KEY_ID"] = "";
os.environ["AWS_SECRET_ACCESS_KEY"] = "";
PATH = '/var/bigbluebutton/published/presentation';
target_dir = 'presentation';

URL = "https://d2avxukljh.execute-api.ap-south-1.amazonaws.com/test/bbb-record";
querystring = {"collegeId":"some-collegeId"}
headers = {
    'content-type': "application/json",
    'x-api-key': ""
    }

def upload_folder_to_s3(s3bucket, inputDir,s3Path):
    print("Uploading results to s3 initiated...");
    os.system("ls -ltR " + inputDir)
    try:
        for path, subdirs, files in os.walk(inputDir):
            for file in files:
                dest_path = path.replace(inputDir,"")
                __s3file = os.path.normpath(s3Path + '/' + dest_path + '/' + file)
                __local_file = os.path.join(path, file)
                print("upload : " +  __local_file + "  to Target: " +  __s3file, file=sys.stderr);
                print("upload : " +  __local_file + "  to Target: " +  __s3file);
                extension = os.path.splitext(file)[1][1:].strip();
                
                if(extension == 'js'):
                  s3bucket.upload_file(__local_file, __s3file,ExtraArgs={'ContentType': "application/javascript"})
                elif(extension == 'css'):
                  s3bucket.upload_file(__local_file, __s3file,ExtraArgs={'ContentType': "text/css"})
                elif(extension == 'html'):
                  s3bucket.upload_file(__local_file, __s3file,ExtraArgs={'ContentType': "text/html"})
                elif(extension == 'png'):
                  s3bucket.upload_file(__local_file, __s3file,ExtraArgs={'ContentType': "image/png"})                         
                elif(extension == 'xml'):
                  s3bucket.upload_file(__local_file, __s3file,ExtraArgs={'ContentType': "text/xml"})
                elif(extension == 'svg'):
                  s3bucket.upload_file(__local_file, __s3file,ExtraArgs={'ContentType': "image/svg+xml"})  
                else:  
                  s3bucket.upload_file(__local_file, __s3file)                                  
                print(" Uplaod ...Success" , file=sys.stderr);
                print(" Uplaod ...Success");
    except Exception as e:
        print(" ... Failed!! Quitting Upload!!");
        

def getMeetingMetaData(xmlFile ,metaXmlPath , internalID ):
    resposneDict = {}
    usersList=[];
    userMap = {}
    poll= {}
    
    doc = xml.dom.minidom.parse(xmlFile);
    meetingdata = doc.getElementsByTagName("metadata");
    meetingmeta = meetingdata[0];

    resposneDict['externalID'] = meetingmeta.getAttribute("meetingId");
    resposneDict['internalID'] = internalID;
    resposneDict['meetingName'] =  meetingmeta.getAttribute("meetingName");
    
    events = doc.getElementsByTagName("event")
    for event in events:
        if (event.getAttribute("eventname") == 'ParticipantJoinEvent'):
            name  = event.getElementsByTagName("name")[0];
            textNode  = name.childNodes[0];
            usersList.append(textNode.data);
            userName=textNode.data
            
            
            name  = event.getElementsByTagName("externalUserId")[0];
            textNode  = name.childNodes[0];
            externalUserId=textNode.data
            
            name  = event.getElementsByTagName("userId")[0];
            textNode  = name.childNodes[0];
            userMap[textNode.data]=userName,externalUserId
            
        elif (event.getAttribute("eventname") == 'PollStartedRecordEvent'):
            newPoll = {}
            name  = event.getElementsByTagName("answers")[0];
            textNode  = name.childNodes[0];
            newPoll["pollOptions"] = textNode.data
            
            name  = event.getElementsByTagName("timestampUTC")[0];
            textNode  = name.childNodes[0];
            newPoll["pollStartTime"] = textNode.data
           
            
            name  = event.getElementsByTagName("pollId")[0];
            textNode  = name.childNodes[0];
            newPoll["pollId"] = textNode.data
            
            newPoll["pollResponses"] = []
            poll[textNode.data] = newPoll
            
        elif (event.getAttribute("eventname") == 'UserRespondedToPollRecordEvent'):
            name  = event.getElementsByTagName("pollId")[0];
            textNode  = name.childNodes[0];
            poolID  = textNode.data
            
            name  = event.getElementsByTagName("answerId")[0];
            textNode  = name.childNodes[0];
            optionID  = textNode.data
            
            name  = event.getElementsByTagName("timestampUTC")[0];
            textNode  = name.childNodes[0];
            responseTime = textNode.data
            
            name  = event.getElementsByTagName("userId")[0];
            textNode  = name.childNodes[0];
            userName  = userMap.get(textNode.data)
            
            if poolID in poll:
               newPoll = poll[poolID]
               d = {"name":userName , "optionId":optionID , "responseTime":responseTime}
               newPoll.get("pollResponses").append(d)
                
    resposneDict['participantsList'] = usersList;
    resposneDict['polls'] =list(poll.values())
    
    doc = xml.dom.minidom.parse(metaXmlPath);
    
    start_time = doc.getElementsByTagName("start_time")[0];
    start_time = start_time.childNodes[0];
    resposneDict['startTime'] = start_time.data;
    
    end_time = doc.getElementsByTagName("end_time")[0];
    end_time = end_time.childNodes[0];
    resposneDict['endTime'] = end_time.data;
    
    
    participants = doc.getElementsByTagName("participants")[0];
    participants = participants.childNodes[0];
    resposneDict['participantCount'] = participants.data;
    
    print(resposneDict, file=sys.stderr)
    return resposneDict;


def postUplaod():
    dirlist = os.listdir(PATH)
    for dir in dirlist: 
        xmlFilePath = "/var/bigbluebutton/recording/raw/"+dir+"/events.xml";
        metaXmlPath = PATH+"/"+dir+"/metadata.xml";
        
        print("xmlFilePath = " + xmlFilePath);
        print("metaXmlPath = " + metaXmlPath);
        
        reqBody  = getMeetingMetaData(xmlFilePath,metaXmlPath,dir)
        resp = requests.request("POST", URL, data=json.dumps(reqBody), headers=headers, params=querystring)
    
        if resp.status_code == 200:
                print(" API call Sucess -- Deleting Meeting recording from this server ", file=sys.stderr)
                #os.system("bbb-record --delete " + meetingId)
        else:
                print('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(resp.status_code, resp.content), file=sys.stderr)
               

def main():
    current_dir = pathlib.Path(__file__).parent ;
    current_dir.__str__()
    LOGFILE =   current_dir.__str__() + '/upload.log' ;
    sys.stderr = open(LOGFILE, 'a')
    
    print("\n<-------------------" + time.strftime("%c") + "----------------------->\n", file=sys.stderr);
    
    s3 = boto3.resource('s3', region_name=s3BucketRegion);
    s3bucket = s3.Bucket(s3BucketName);
    upload_folder_to_s3(s3bucket, PATH,target_dir);
    postUplaod();

if __name__ == "__main__":
    main()
