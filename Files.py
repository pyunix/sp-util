import base64
import csv
import json
import operator
import re
from urllib.parse import unquote
from xml.dom import minidom
#import xml.etree.ElementTree as ET
import zlib


class Compare():
    #------------------------------------------------------------------------------------------------------------------------------       
    def __init__(self,originalfile,comparefile,logger=None):
        self.originalfile = originalfile
        self.comparefile = comparefile
        self.mapping = {}
        self.lookup = None
        self.logger = logger
    #------------------------------------------------------------------------------------------------------------------------------    
    def RemoveMaps(self):
        if self.logger: self.logger.debug(f'Removing all mappings')
        self.mapping = {}
        
    #------------------------------------------------------------------------------------------------------------------------------        
    def AddMaps(self,newmaps):
        for map in newmaps:
            if map in self.mapping.keys():
                if self.logger: self.logger.debug(f'Already mapped: {map}')
                continue
                
            if not map in self.originalfile.headers:
                if self.logger: self.logger.debug(f"No header: {map} in originalfile {self.originalfile.filename} : {self.originalfile.headers}")
                continue

            if not newmaps[map] in self.comparefile.headers:
                if self.logger: self.logger.debug(f"No header: {newmaps[map]} in comparefile {self.comparefile.filename} : {self.comparefile.headers}")
                continue
                
            if self.logger: self.logger.debug(f"Adding map: {map} : {newmaps[map]}")
            self.mapping.update({map: newmaps[map]})
    #------------------------------------------------------------------------------------------------------------------------------            
    def Match(self,action="check"):
        if self.logger: self.logger.debug(f"action: {action}")
        
        if action.lower() == "check":
            for c_row in self.comparefile.content:
                o_row = self.originalfile.FindRow(self.originalfile.lookup,c_row[self.comparefile.lookup])
                
                if o_row == None:
                    if self.logger: self.logger.info(f'Not Found - {self.originalfile.filename} Does not contain {self.comparefile.lookup}: {c_row[self.comparefile.lookup]}')
                else:
                    for map in self.mapping:
                        if o_row[map] != c_row[self.mapping[map]]:
                            if o_row[map] == "":
                                if self.logger: self.logger.info(f'Not Populated - {self.originalfile.filename} Does not have "{map}" whereas {self.comparefile.filename} says "{self.mapping[map]}" : "{c_row[self.mapping[map]]}"')
                            else:
                                if self.logger: self.logger.info(f'Differences - {self.originalfile.filename} says "{map}" : "{o_row[map]}", {self.comparefile.filename} says "{self.mapping[map]}" : "{c_row[self.mapping[map]]}"')
            return(0)
        
        if action.lower() == "merge":
            for c_row in self.comparefile.content:
                o_row = self.originalfile.FindRow(self.originalfile.lookup,c_row[self.comparefile.lookup])
                if o_row == None:
                    if self.logger: self.logger.debug(f'Adding Row - {self.originalfile.filename} {self.originalfile.lookup}: {c_row[self.comparefile.lookup]}')
                    o_row = self.originalfile.AddRow({self.originalfile.lookup:  c_row[self.comparefile.lookup]})
                    for header in self.originalfile.headers:

                        if not header == self.originalfile.lookup:
                            o_row.update({header: ""})
                            if self.logger: self.logger.debug(f'Initialising Row - {self.originalfile.filename}:{c_row[self.comparefile.lookup]} {header}')
                            
                if self.logger: self.logger.debug(f'O Row is - {o_row}')
                for map in self.mapping:
                    if self.logger: self.logger.debug(f'Checking map - {map}')
                    if not map in o_row.keys():
                        o_row.update({map: ""})
                        
                    if self.logger: self.logger.debug(f'Has Key {map} with value {o_row[map]}')

                    if o_row[map] == "":
                        if self.logger: self.logger.debug(f'Adding Value - {self.originalfile.filename} "{map}" : "{c_row[self.mapping[map]]}"')


                            
                        o_row.update({map: c_row[self.mapping[map]]})
                    if self.logger != None:
                        self.logger.debug(f'New O_Row is {o_row}')
                        
            
class File():
    #------------------------------------------------------------------------------------------------------------------------------
    def __init__(self,logger=None,lookup=None,index=None,headers=[],content=[],filename=None):
        self.index = index
        self.logger = logger
        self.lookup = lookup
        self.headers = headers
        self.content = content
        self.filename = filename
    #------------------------------------------------------------------------------------------------------------------------------
    def SetIndex(self,index):
        if index == None or index in self.headers:
            self.index = index
            if self.logger: self.logger.debug(f"Index set to {index}")
        else:
            if self.logger: self.logger.error(f"Can't set Index {index} - Not found")
    #------------------------------------------------------------------------------------------------------------------------------            
    def SetLookup(self,lookup):
        if lookup == None or lookup in self.headers:
            self.lookup = lookup
            if self.logger: self.logger.debug(f"Lookup set to {lookup}")
        else:
            if self.logger: self.logger.error(f"Can't set Lookup {lookup} - Not found")
    #------------------------------------------------------------------------------------------------------------------------------    
    def FindRow(self,column,value):
        if self.lookup == None:
            if self.logger: self.logger.error(f"No Lookup set for {self.filename}")
            return []
                    
        for row in self.content:
            if row[column] == value:
                if self.logger: self.logger.debug(f"Found match in {self.filename}: {column}:{value} = {row[column]}")
                return(row)
                
        if self.logger: self.logger.debug(f"No match in {self.filename}: {column}:{value}")

    #------------------------------------------------------------------------------------------------------------------------------
    def BuildHeaders(self):
        self.headers = []
        
        #if self.logger: self.logger.debug(f"{self.filename}: BuildHeaders - content is type: {type(self.content)}")

        if isinstance(self.content,dict):
            for row in self.content:
                #if self.logger: self.logger.debug(f"{self.filename}: BuildHeaders - row is type: {type(self.content[row])} : {self.content[row]}")
                if (isinstance(self.content[row],dict)):                
                    for x in self.content[row].keys():
                        #if self.logger: self.logger.debug(f"{self.filename}: Checking Key: {x}")
                        if not x in self.headers:
                            #if self.logger: self.logger.debug(f"{self.filename}: Adding New Header: {x}")
                            self.headers += [x]

        if isinstance(self.content,list):
            #if self.content:
                #if self.logger: self.logger.debug(f"{self.filename}: Processing List headers {self.content[0]}")
            for row in self.content:
                #if self.logger: self.logger.debug(f"{self.filename}: row is type: {type(row)}")
                if (isinstance(row,dict)):                
                    for x in row.keys():
                        #if self.logger: self.logger.debug(f"{self.filename}: Checking Key: {x}")
                        if not x in self.headers:
                            #if self.logger: self.logger.debug(f"{self.filename}: Adding New Header: {x}")
                            self.headers += [x]
                            
                            
        if self.logger: self.logger.debug(f"Headers built: {self.filename} = {self.headers}")

    #------------------------------------------------------------------------------------------------------------------------------           
    def AddHeaders(self,newheaders):
        for header in newheaders:
            if header in self.headers:
                #if self.logger: self.logger.debug(f"{self.filename}: already has header: {header}")
                continue
            
            self.headers += [header]
            if self.logger: self.logger.debug(f"{self.filename}: adding header: {header}")

    #------------------------------------------------------------------------------------------------------------------------------                
    def RemoveRow(self,row):
        #if self.logger: self.logger.debug(f"{self.filename}: Removing Row: {row}")
        self.content.remove(row)

        
class CSVFile(File):

    #------------------------------------------------------------------------------------------------------------------------------
    def ReadCSVFile(self,filename):
        # Open the CSV file and create a reader object
        self.filename = filename
        with open(filename, "r", newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            self.content = list(reader)
        
        if self.logger: self.logger.debug(f"Read CSV File: {filename}")
        
    #------------------------------------------------------------------------------------------------------------------------------    
    def WriteCSVFile(self,filename):
        with open(filename, "w", newline='',encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile,fieldnames=self.headers)
            writer.writeheader()
            for row in self.content:
                line = {}
                for header in self.headers:
                    if header in row.keys(): line.update({header: row[header]})
                    else: line.update({header: ""})
                #if self.logger: self.logger.debug(f"Writing line: {line}")
           
                writer.writerow(line)
        
        if self.logger: self.logger.debug(f"Wrote CSV File: {filename}")

    #------------------------------------------------------------------------------------------------------------------------------
    def JSON2CSV(self,JSONObject,filename=None):
        self.filename = filename
        self.content = []
        
        if self.lookup == None:
            self.lookup = "Index"

        if self.logger: self.logger.debug(f"{filename}: JSON2CSV - JSONObject content is type: {type(JSONObject)}")
            
        if isinstance(JSONObject,dict):
            for row in JSONObject:
                line = {}
                #if self.logger: self.logger.debug(f"{filename}: JSON2CSV: {type(JSONObject[row])} : {JSONObject[row]}")
                if (isinstance(JSONObject[row],dict)):                
                    line.update({self.lookup: row})
                    line.update(JSONObject[row])
                #if self.logger: self.logger.debug(f"{filename}: JSON2CSV - New Line is : {line}")
                self.content  += [line]
                
        if isinstance(JSONObject,list):
            for row in JSONObject:
                line = {}

                #if self.logger: self.logger.debug(f"{filename}: JSON2CSV: row type is {type(row)}")
                if (isinstance(row,dict)): 
                    for key in row.keys():
                        line.update({key: json.dumps(row[key], sort_keys=True)})
                else:
                    line.update(row)
                self.content += [line]        
                
        if self.logger: self.logger.debug(f"Converted JSON to CSV: {self.filename}")

    #------------------------------------------------------------------------------------------------------------------------------
    # Convert XML content to CSV
    def XML2CSV(self,content,filename=None,newxdepth=0):
        self.filename = filename
        xdepth = newxdepth
        root = ''
        tagName = ''
        text = ''
        attributes = []
        
        if content.nodeType == content.DOCUMENT_NODE:
                root = content.toxml().split(">")[0] + ">"

        if content.nodeType == content.ELEMENT_NODE:
            tagName = content.tagName
            #if self.logger: self.logger.debug(f'Element_Node (Depth={xdepth}): {tagName}')
            
            if content.hasAttributes():
                attributes = content.attributes.items()
                #if self.logger: self.logger.debug(f'Attributes (Depth={xdepth}): {attributes}')
                    
        if content.nodeType == content.TEXT_NODE:
            text = content.toxml().strip()
            if len(text) > 0:
                tagName = "textNode"
                #if self.logger: self.logger.debug(f'Text_Node (Depth={xdepth}): {text}')

        if root: print(f'{xdepth}: root={root}')
        elif text: 
            line = {}
            line.update({"depth": xdepth, "tagName": tagName, "text": text})
            print(f'{xdepth}: line={line} len={len(text)}')
        elif tagName: 
            line = {}
            line.update({"depth": xdepth, "tagName": tagName})
            for attribute in attributes:
                line.update({attribute[0]: attribute[1]})
            if self.logger: self.logger.debug(f'{xdepth}: Adding line={line}')
            self.content.append(line)

        if content.childNodes:
            #if self.logger: self.logger.debug(f'Has childNodes (Depth={xdepth}): {len(content.childNodes)}')
            for i in content.childNodes:
                #if self.logger: self.logger.debug(f'childNodes (Depth={xdepth}): {type(i)}')
                self.XML2CSV(i,newxdepth=(xdepth + 1))
                
    #------------------------------------------------------------------------------------------------------------------------------
    def AddRow(self,line):
        if self.logger: self.logger.debug(f"Addrow line: {line}")
        self.content.append(line)
        return self.FindRow(self.lookup,line[self.lookup])

    #------------------------------------------------------------------------------------------------------------------------------                
    def GrepCol(self,column,pattern):
        if self.logger: self.logger.debug(f"{self.filename}: matching column {column} with pattern {pattern}")
        if not column in self.headers:
            if self.logger: self.logger.warn(f"{self.filename}: column {column} not in headers {self.headers}")
            return None
            
        newcontent = []
        for row in self.content:
            #if self.logger: self.logger.debug(f"{self.filename}: checking #{row[column]}# against {pattern}")
            if re.match(pattern,row[column]):
                #if self.logger: self.logger.debug(f"{self.filename}: matched #{row[column]}# against {pattern}")
                newcontent.append(row)
        return newcontent
        
    def SortCol(self,column,rev=False):
        if self.logger: self.logger.debug(f"{self.filename}: sorting column {column}")
        if not column in self.headers:
            if self.logger: self.logger.warn(f"{self.filename}: column {column} not in headers {self.headers}")
            return None

        sortedcontent = sorted(self.content,key=operator.itemgetter(column),reverse=rev)
        return(sortedcontent)
        
    def UniqueCol(self,column):
        if self.logger: self.logger.debug(f"{self.filename}: removing duplicates in column {column}")
        if not column in self.headers:
            if self.logger: self.logger.warn(f"{self.filename}: column {column} not in headers {self.headers}")
            return None

        ulist = []
        uniquecontent = []
        for row in self.content:
            if row[column] in ulist:
                if self.logger: self.logger.debug(f'{self.filename}: already seen {row[column]} - skipping')
            else:
                uniquecontent.append(row)
                ulist += [row[column]]
        return(uniquecontent)
        
class JSONFile(File):
    #------------------------------------------------------------------------------------------------------------------------------
    def ReadJSONFile(self,filename):
        self.filename = filename
        with open(filename,"r") as jsonfile:
            self.raw = json.load(jsonfile)
            if self.logger: self.logger.info(f"Read JSON File: {filename}")
        
        self.content = self.raw

class XMLFile(File):
    #------------------------------------------------------------------------------------------------------------------------------
    def ReadXMLFile(self,filename):
        self.filename = filename
        self.content = minidom.parse(filename)
        
        if self.logger: self.logger.info(f"Read XML File: {filename}")

    #------------------------------------------------------------------------------------------------------------------------------
    # Print the contents of an object, maybe recurse for sub objects
    def ParseXML(self,content,newxdepth=0):
        xdepth = newxdepth
        root = ''
        tagName = ''
        text = ''
        attributes = []
        
        if content.nodeType == content.DOCUMENT_NODE:
                root = content.toxml().split(">")[0] + ">"

        if content.nodeType == content.ELEMENT_NODE:
            tagName = content.tagName
            #if self.logger: self.logger.debug(f'Element_Node (Depth={xdepth}): {tagName}')
            
            if content.hasAttributes():
                attributes = content.attributes.items()
                #if self.logger: self.logger.debug(f'Attributes (Depth={xdepth}): {attributes}')
                    
        if content.nodeType == content.TEXT_NODE:
            text = content.toxml().strip()
            if len(text) > 0:
                tagName = "textNode"
                #if self.logger: self.logger.debug(f'Text_Node (Depth={xdepth}): {text}')

        if root: print(f'{xdepth}: root={root}')
        elif text: 
            line = {}
            line.update({"depth": xdepth, "tagName": tagName, "text": text})
            print(f'{xdepth}: line={line} len={len(text)}')
        elif tagName: 
            line = {}
            line.update({"depth": xdepth, "tagName": tagName})
            for attribute in attributes:
                line.update({attribute[0]: attribute[1]})
            print(f'{xdepth}: line={line}')

        if content.childNodes:
            #if self.logger: self.logger.debug(f'Has childNodes (Depth={xdepth}): {len(content.childNodes)}')
            for i in content.childNodes:
                #if self.logger: self.logger.debug(f'childNodes (Depth={xdepth}): {type(i)}')
                self.ParseXML(i,newxdepth=(xdepth + 1))

        
class DrawIOFile(XMLFile):
    #------------------------------------------------------------------------------------------------------------------------------
    def ReadDrawIOFile(self,filename):
        self.rawdiagrams = []
        self.diagrams = {}
        if self.logger: self.logger.info(f"Reading XML content: {filename}")
        self.ReadXMLFile(filename)
        if self.logger: self.logger.info(f"Extracting Diagrams: {filename}")
        pointer = self.content
        if pointer.nodeType == pointer.DOCUMENT_NODE:
            if pointer.childNodes:
                #if self.logger: self.logger.debug(f"Elevating past: Document_Node(0)")
                pointer = pointer.childNodes[0]
                
                if pointer.nodeType == pointer.ELEMENT_NODE:
                    if pointer.childNodes and pointer.tagName == "mxfile":
                        #if self.logger: self.logger.debug(f"Elevating past: mxfile(1)")
                        #pointer = pointer.childNodes[0]
                        
                        #if pointer.nodeType == pointer.ELEMENT_NODE:
                        if pointer.childNodes:
                            #if self.logger: self.logger.debug(f"Looking for diagram elements(2)")
                            for element in pointer.childNodes:
                                if element.nodeType == element.ELEMENT_NODE:
                                    #if self.logger: self.logger.debug(f"Checking {element.tagName} of {len(pointer.childNodes)} attributes {element.attributes.items()}")
                                    if element.tagName == "diagram":
                                        attributes = {}
                                        for attribute in element.attributes.items():
                                            attributes.update({attribute[0]: attribute[1]})
                                        #if self.logger: self.logger.debug(f"Got attributes {attributes}")
                                        if element.childNodes:
                                            if element.childNodes[0].nodeType == element.TEXT_NODE:
                                                if element.childNodes[0].data[0] in " \t\n\r" or len(element.childNodes[0].data) <= 0:
                                                    #if self.logger: self.logger.debug(f"Found XML data {element.toxml()}")
                                                    data = element
                                                else:                                                    
                                                    #if self.logger: self.logger.debug(f"Found compressed data {element.childNodes[0].toxml()}")
                                                    cdata = base64.b64decode(element.childNodes[0].data)
                                                    ddata = zlib.decompress(cdata, wbits=-15)
                                                    udata = unquote(ddata)
                                                    data = minidom.parseString(udata)

                                                attributes.update({"xml": data})
                                        if "name" in attributes.keys():
                                            self.diagrams.update({attributes["name"]: attributes})
                                        #if self.logger: self.logger.debug(f"Got diagrams {self.diagrams}")

    #------------------------------------------------------------------------------------------------------------------------------
    # Convert CSV content to XML
    def CSV2XML(self,content,filename=None,newxdepth=0):
        xdepth = newxdepth
        
        if xdepth == 0:
            self.content = minidom.parseString('<mxfile host="myhost" Modified="now" />')
#            self.content.createAttribute("abc")
#            self.content.setAttribute("abc","xyz")
            root = self.content.documentElement
            line = self.content.createElement("diagram")
            line.setAttribute("id","adfhdf4534")
            line.setAttribute("name", "myfilename")
            root.appendChild(line)
            