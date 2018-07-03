###############################################################################
#                                                                             #
#                 SFyPy Salesforce Python dataLoader                          #
#                                                                             #
###############################################################################

import os
import csv
import pyodbc
import requests
from xml.etree import ElementTree as ET
from datetime import datetime
from simple_salesforce import Salesforce

queryPath = os.getcwd() + "/Queries/"
outputPath = os.getcwd() + "/filesToUpload/"
settingsPath = os.getcwd() + "/settings.txt" 
logPath = os.getcwd() + "/log.txt" 
sfParentChildDelimeter = "}"

def readSettings():
        with open(settingsPath, "r") as f: 
                    settings = f.read()

        global txtRecordType, optionAction, txtServerName, txtDatabaseName, txtServerUsername, txtServerPassword, txtSfUsername, txtSfPassword, txtSfSecurityToken, txtUseSfSandbox, txtBatchSize
        txtRecordType, optionAction, txtServerName, txtDatabaseName, txtServerUsername, txtServerPassword, txtSfUsername, txtSfPassword, txtSfSecurityToken, txtUseSfSandbox, txtBatchSize = settings.split('|')


def isDate(date_text):
    try:
        if date_text != datetime.strptime(date_text, "%Y-%m-%d").strftime('%Y-%m-%d'):
            raise ValueError
        return True
    except ValueError:
        return False

def uploadResultsToSalesforce(sfObject, action, rows, sfUsername, sfPassword, sfSecurityToken, useSfSandbox):
        #login to Salesforce
        #get the XML response
        #parse the session ID
        #parse the Salesforce url
        #parse the Salesforce instance
        #when parsing, if an exception is caught, the login was invalid
        #The external ID field name should be the first column of the first row
        #for each row
                #add each row to a batch 
                #if the row index match the batch size
                        #start a batch Job
                        #reset and start a new batch
                        #insert the column headers into the first row of the batch rows
        #if the rows are smaller than the batch size, then just execute a batch
        
        try:
                loginXmlResponse = salesforceLogin(sfUsername, sfPassword + sfSecurityToken, useSfSandbox)
                loginXmlRoot = ET.fromstring(loginXmlResponse)                
                
                try:
                        sessionId = loginXmlRoot[0][0][0][4].text
                        url = loginXmlRoot[0][0][0][3].text                        
                        instance = url[8:12]
                except:
                        print("\r\n Invalid Salesforce Login \r\n")
                        return "Invalid Salesforce Login"
                
                externalId = rows[0][0]
                batchRows = []
                j = 0
                for i in range(len(rows)):
                        j += 1
                        batchRows.append(rows[i])
                        if(str(j) == txtBatchSize):
                                batchJob(batchRows, action, instance, externalId, sessionId, sfObject, sfUsername, sfPassword, sfSecurityToken, useSfSandbox)
                                batchRows = []
                                batchRows.insert(0, rows[0])
                                j = 0
                              
                batchResult = batchJob(batchRows, action, instance, externalId, sessionId, sfObject, sfUsername, sfPassword, sfSecurityToken, useSfSandbox)                
                                
                return batchResult
                
        except Exception as e:
                print("\n\r" + str(e))
                input("")
                return str(e)

def batchJob(batchRows, action, instance, externalId, sessionId, sfObject, sfUsername, sfPassword, sfSecurityToken, useSfSandbox):
        #Create a new Salesforce Job
        #get the XML response from the job
        #get the job ID from the response
        #if the job ID is invalid, return the error
        #Create the XML of objects to be added to a batch
        #if no objects were added to the XML, return no objects were found to be updated
        #Start a new batch with the XML, job ID, session ID, and the Salesforce instance
        #Close the Job
        
        jobXmlResponse = createJob(instance, externalId, sessionId, action, sfObject)                
        jobXmlRoot = ET.fromstring(jobXmlResponse)
        jobId = jobXmlRoot[0].text
        
        if(jobId == "InvalidJob"):
                return jobXmlRoot[1].text
        
        print("\r\n ...creating xml\r\n")     
        objectXml = createObjectXml(batchRows, sfObject, action, sfUsername, sfPassword, sfSecurityToken, useSfSandbox)        
        print("\r\n finished xml \r\n")
        
        if(objectXml == "<sObject></sObject>"):
                print("Could not find records to update")
                return "Could not find records to update"
        
        print("\r\n ...adding batch \r\n")        
        bResults = addBatch(instance, sessionId, jobId, objectXml)
        print("\r\n" + bResults)
        
        print("\r\n ...closing job \r\n")
        closeResponse = closeJob(instance, sessionId, jobId)
        print("\r\n" + bResults)
        
        return bResults + "\n\r" + closeResponse


def createObjectXml(rows, sfObject, action, sfUsername, sfPassword, sfSecurityToken, useSfSandbox):        
        #for each row in the csv file
                #if it is an update
                        #log into Salesforce
                        #set select query 'select id from object where '
                        #for each row
                                #if the data is a date, don't add quotes
                                #else add quotes
                                #if the delimeter '}' is in the header row, then it is a relationship field
                                        #get the parent and child from the column name and remove the 'r' from object__r
                                        #add to the select query ' parent.child = data and '
                                #else add to select query ' columnName = data and '                                
                        #remove the last 'and' from the select query
                        #execute the query
                        #if no records were found, skip
                        #get the ID from the record found (should only be one)
                        #insert the ID at the beginning of the row
                        #if 'ID' is not in the column headers, then add it to the first column of the headers
                #open the object
                #for each item in the row
                        #if the delimeter '}' is in the header row, then it is a relationship field
                                #get the parent and child from the column name and remove the 'r' from object__r
                                #convert the parent, child, and data to XML format
                        #else it is not a relationship field
                                #if an ampersand is in the data item, then replace it with 'and' (Salesforce doesn't like '&' in the XML file)
                                #if the data item is not null or blank, convert it to an XML format
                                #else the data is null or blank and the XML field needs to have 'xsi:nil=true'
                #close the object
        #return the object
        
        sfFields = rows[0]        
        iterrows = iter(rows)
        next(iterrows)
        isIDinHeader = False
        sObjects = ""
        for row in iterrows:
                if(action == "update"):                        
                        sf = Salesforce(username=sfUsername, password=sfPassword, security_token=sfSecurityToken, sandbox=useSfSandbox)
                        selectIdQuery = "SELECT Id FROM " + sfObject + " WHERE "   
                        for i in range(len(row)):
                                if(isDate(row[i])):
                                        sfData = row[i]
                                else:
                                        sfData = "'" + row[i] + "'"
                                if(sfParentChildDelimeter in str(sfFields[i])):
                                        sfParentChild = sfFields[i].split(sfParentChildDelimeter)
                                        sfChild = sfParentChild[1]
                                        sfParent = sfParentChild[0]
                                        sfParent = sfParent[:-1] + "r"
                                        
                                        selectIdQuery += sfParent + "." + sfChild + " = " + sfData + " and "                                                
                                else:                                        
                                        selectIdQuery += sfFields[i] + " = " + sfData + " and "
                                        
                        selectIdQuery = selectIdQuery[:-4]

                        queryRecords = sf.query(selectIdQuery)
                        if(queryRecords["totalSize"] == 0):
                                continue             
                        records = queryRecords["records"]
                        recordID = ""
                        for record in records:
                                recordID = record["Id"]
                        row.insert(0, recordID)
                        
                        if(isIDinHeader == False):
                                sfFields.insert(0, "Id")
                                isIDinHeader = True
                
                sObject = "<sObject>"
                j = 0 
                for item in row:                                
                        if(sfParentChildDelimeter in str(sfFields[j])):                                
                                sfParentChild = sfFields[j].split(sfParentChildDelimeter)
                                sfChild = sfParentChild[1]
                                sfParent = sfParentChild[0]
                                sfParent = sfParent[:-1] + "r"
                                if item:
                                        sObject += "<" + sfParent + "><sObject><" + sfChild + ">" + item + "</" + sfChild + "></sObject></" + sfParent + ">"
                        else:
                                if("&" in item):
                                        item = item.replace("&", "and")
                                if item:
                                        sObject += "<" + sfFields[j] + ">" + item + "</" + sfFields[j] + ">"
                                else:
                                        sObject += "<" + sfFields[j] + " xsi:nil='true'/>"
                        
                                
                        j += 1
                sObject += "</sObject>"
                sObjects += sObject
        return sObjects

def addBatch(instance, sessionId, jobId, objects):
        #Add the XML of objects to the XML header
        #encode the XML
        #add the Salesforce instance and the job ID in the url to be posted
        #add parameters to the header
        #Send the request to Salesforce
        #return the response
        
  request = u"""<?xml version="1.0" encoding="UTF-8"?>
                <sObjects xmlns="http://www.force.com/2009/06/asyncapi/dataload" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                     """ + objects + """
                  </sObjects>"""

  encoded_request = request.encode('utf-8')
  url = "https://" + instance + ".salesforce.com/services/async/30.0/job/" + jobId + "/batch"
   
  headers = {"X-SFDC-Session": sessionId,
             "Content-Type": "application/xml; charset=UTF-8"}
                             
  response = requests.post(url=url,
                           headers = headers,
                           data = encoded_request,
                           verify=False)

  return response.text
                
def createJob(instance, externalId, sessionId, operation, object):
        #Add the type of operation(upsert,update,insert), the object name, and the external ID to the Job Info XML
        #encode the Job info XML
        #Add the Salesforce instance in the url to be posted
        #Add the parameters to the header
        #Send the request to Salesforce
        #return the response
        
  request = u"""<?xml version="1.0" encoding="UTF-8"?>
  <jobInfo xmlns="http://www.force.com/2009/06/asyncapi/dataload">
      <operation>""" + operation + """</operation>
      <object>"""+ object + """</object>
      <externalIdFieldName>""" + externalId + """</externalIdFieldName>
      <contentType>XML</contentType>
  </jobInfo>"""
  
  encoded_request = request.encode('utf-8')
  url = "https://" + instance + ".salesforce.com/services/async/30.0/job"
   
  headers = {"X-SFDC-Session": sessionId,
             "Content-Type": "application/xml; charset=UTF-8"}
                             
  response = requests.post(url=url,
                           headers = headers,
                           data = encoded_request,
                           verify=False)

  return response.text

def salesforceLogin(userName, password, useSandbox):
        #Add the username and password to the login XML
        #encode the login XML
        #If the sandbox checkbox is checked, use the test url
        #else use the production url
        #Add the parameters to the header
        #Send the request to Salesforce
        #return the response
        
        request = u"""<?xml version="1.0" encoding="utf-8" ?>
                <env:Envelope xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
                <env:Body>
                <n1:login xmlns:n1="urn:partner.soap.sforce.com">
                <n1:username>""" + userName + """</n1:username>
                <n1:password>""" + password + """</n1:password>
                </n1:login>
                </env:Body>
                </env:Envelope>"""

        encoded_request = request.encode('utf-8')
        
        if(useSandbox == '1'):
                url = "https://test.salesforce.com/services/Soap/u/30.0"
        else:
                url = "https://login.salesforce.com/services/Soap/u/30.0"
   
        headers = {"Content-Type": "text/xml; charset=UTF-8",
             "SOAPAction": "login"}
                             
        response = requests.post(url=url,
                           headers = headers,
                           data = encoded_request,
                           verify=False)
        
        return response.text

def closeJob(instance, sessionId, jobId):
        #Add the state of the job to the Job Info XML
        #encode the Job info XML
        #Add the Salesforce instance and the Job ID in the url to be posted
        #Add the parameters to the header
        #Send the request to Salesforce
        #return the response
        
  request = u"""<?xml version="1.0" encoding="UTF-8"?>
  <jobInfo xmlns="http://www.force.com/2009/06/asyncapi/dataload">
    <state>Closed</state>
  </jobInfo>"""

  encoded_request = request.encode('utf-8')
  url = "https://" + instance + ".salesforce.com/services/async/30.0/job/" + jobId
   
  headers = {"X-SFDC-Session": sessionId,
             "Content-Type": "application/xml; charset=UTF-8"}
                             
  response = requests.post(url=url,
                           headers = headers,
                           data = encoded_request,
                           verify=False)

  return response.text

def executeQuery(query, record):
        #get the settings for the server, database, username and password
        #if no query was passed through the parameters, then return 'no query'
        #if the username was not found, then the database server credentials were set to trusted
        #connect to the database
        #execute the query
        #create a new CSV if one was not found
        #write the results of the query to the CSV file
        #return finished
        
        try:
                readSettings()

                if(query == ""):
                    return "No query"
                   
                if(txtServerUsername != ""):
                    con_string= 'DRIVER={SQL Server};PORT=1433;TDS_Version=8.0;SERVER='+txtServerName+';DATABASE='+txtDatabaseName+';UID=' + txtServerUsername + ';PWD=' + txtServerPassword + ';'
                else:
                    con_string= 'DRIVER={SQL Server};PORT=1433;TDS_Version=8.0;SERVER='+txtServerName+';DATABASE='+txtDatabaseName+';Trusted_Connection=true;'
                              
                cnxn=pyodbc.connect(con_string)
                cursor=cnxn.cursor()
                cursor.execute("set nocount on; " + query)
                
                dirname = os.path.dirname(outputPath + record + ".csv")        
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

                with open(outputPath + record + ".csv", "w+", encoding="utf-8") as csvFile:
                        for row in cursor:
                                csv.writer(csvFile, delimiter="|", quoting=csv.QUOTE_NONE, quotechar='').writerow(row)
                        
                return "Finished Created the CSV file"

        except Exception as e:
                return str(e)


def readCSV(filename):
        #open the CSV file and read each row into an array
        #return the array
        
        try:
                with open(outputPath + filename + ".csv", "r", encoding="utf-8") as f:
                        lines = [line.strip().split('|') for line in f if line != '\n']
                
                return lines
        
        except Exception as e:
                return str(e)

def main():
        #read the settings
        #for each file in the Queries folder
                #get the filename without the numbers and hyphen
                #read the query in the file
                #execute the query
                #read from the newly created CSV file
                #if only the headers are in the CSV, then no results, so skip
                #upload the results to salesforce
                #write to the log file
        #return finished
        
        try:        
                readSettings()

                for file in sorted(os.listdir(queryPath)):
                        filename = os.path.splitext(file)[0]
                        filename = filename.split('-')[1]
                        with open(queryPath + file, "r") as f:
                                query = f.read()
                        
                        executeQuery(query, filename)
                   
                        rows = readCSV(filename)
                        
                        if(len(rows) == 1):
                                continue
                        result = uploadResultsToSalesforce(filename, optionAction, rows, txtSfUsername, txtSfPassword, txtSfSecurityToken, txtUseSfSandbox)
                        with open(logPath, "a+") as f: 
                                f.write(result + '\r\n')
                return "Finished. You can find the results in " + logPath + ", or you can check the Bulk Data Load Jobs in Salesforce."

        except Exception as e:
                return str(e)
