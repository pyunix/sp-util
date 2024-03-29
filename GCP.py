import json
import os
import urllib.request
#import requests

# pip install -U google-cloud-resource-manager
#from google.cloud import compute_v1
#from google.cloud import resourcemanager_v3
#from google.cloud.resourcemanager import ProjectsClient

class Base():

    def __init__(self,logger=None):
        self.logger = logger
        self.AuthToken = None
        self.JSON = None
        if os.environ.get("Cust") == None:
            if self.logger: self.logger.error(f'ENVAR "Cust" is not set')
            return(-1)
        else:
            self.BaseDir = os.environ.get("Cust") + "/Gather"

class Auth(Base):

    def LoadAuth(self):
        with open(self.BaseDir + "/AuthFiles/GCPAuth.txt", "r", newline='') as authfile:
            self.AuthToken = authfile.readline().strip()
            
class Compute(Base):
        
    def GetCompute(self,project,zone):

        # Create a client
        
        client = compute_v1.InstancesClient()
        
        # Initialize request argument(s)
        request = compute_v1.ListInstancesRequest(project=project,zone=zone,alt="json")

        # Make the request
        page_result = client.list(request=request)

        # Handle the response
        #print(dir(page_result))
        for response in page_result:
            print(response)
#            if response[1].instances:
#                for instance in response[1].instances:
#                    #newjson = json.loads(instance)
#                    #self.JSON.append(newjson)
#                    #print(f' Got: {response[1].instance}')
#                    print(dir(instance))
#        return(self.JSON)


class DC(Base):
        
    def GetDC(self,auth):
        self.DCURL = 'https://cloudresourcemanager.googleapis.com/v1/projects?alt=json'
        self.headers = {b'content-length': b'0', b'accept': b'application/json', b'authorization': f"Bearer {auth.AuthToken}"}
        if self.logger: self.logger.debug(f'headers = {self.headers}')

        #self.responseJSON = requests.get(self.DCURL, headers=self.headers)
        #if self.logger: self.logger.debug(f'response = {self.responseJSON.text}')
        #self.textJSON = json.loads(self.responseJSON.text)
        #return(0)

        self.req = urllib.request.Request(self.DCURL,headers=self.headers)

        with urllib.request.urlopen(self.req) as f:
            self.responseJSON = f.read()
        if self.logger: self.logger.error(f'response = {self.responseJSON}')
        self.textJSON = json.loads(self.responseJSON)


#        for project in ProjectsClient().search_projects():
#            print(project.display_name)
    

#        client = resourcemanager_v3.ProjectsClient()
#
#        request = resourcemanager_v3.ListProjectsRequest(parent=parent)
#        page_result = client.list_projects(request=request)
#        for response in page_result:
#            print(response)
