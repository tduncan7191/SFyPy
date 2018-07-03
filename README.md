# SFyPy

SFyPy inserts, updates, and upserts data from your database to multiple Salesforce objects in a bulk transfer.

SFyPy Overview
SFyPy collects data from the database and stores it into csv files. 
Once the data has been collected, the application will transfer that data into Salesforce using a bulk method. 
This transfer can be completed using insert, update, or upsert. 



# Using the Console

Run the application labeled 'SFyPy.exe' in the SFyPy folder. 
Enter the Salesforce object you want to perform the task on. Use the object's API name such as Account__c.
Pick insert, update, or upsert from the dropdown. 
Insert creates a new record in Salesforce under the object.
The Update task replaces the old Salesforce entry with the new data if there is already a record in Salesforce. 
If there isn't a record to update, then the update will skip that record.
This method will create an API call for every record needing updated. This is because a query for the Id of the record
is needed to associate the new data with the correct Salesforce old data.
Upsert allows the record to be updated, but if there is no record, then it inserts the record instead.
To get data from your database, use the querybox and the settings for your server below.
Connect to your database with the server name, database name, server user name and server password.
If you are using a trusted connection without the username and password, then leave those fields blank. 
The query format used in development is found here:

select
'API_1__c'
,'API_2__c'
...
union all
select
cast([TABLE].APIdata1 as nvarchar(50)) as API_1__c
,cast([TABLE].APIdata2 as nvarchar(50)) as API_2__c
... 
FROM [SERVER].[database].[dbo].[TABLE]

To add a record that contains a master-detail custom object, use this format:

 select
'API_1__c'
,'Master__c}Detail__c'
...
union all
select
cast([TABLE].APIdata1 as nvarchar(50)) as API_1__c
,cast([TABLE].DetailData as nvarchar(50)) as Detail__c
...
FROM [SERVER].[database].[dbo].[TABLE]

If you would like to save your settings without running anything, click the SAVE SETTINGS button.
You can also generate a csv file of the data by clicking GENERATE TEST FILE. 
This will produce a CSV located in the filesToUpload folder of your installed package.
The queries you save will also be located in the installed package under the QUERIES folder.
If you want to just run the query written in the querybox, click RUN QUERY and it will generate a CSV 
and upload the contents to Salesforce.
To run all of the queries in the QUERIES folder click the UPLOAD ALL CSVs button and it will execute all of
the queries in the QUERIES folder.
The results of the upload can be found after clicking RUN QUERY or UPLOAD ALL CSVs in the SalesforceLog.txt file.

One of the features this application has is the ability to run on a schedule. 
To do this, open Task Scheduler and set a task to run ScheduleJob.py.
This will run a task to execute all queries in the QUERIES folder and produce a CSV file for every query ran and 
imports the results to Salesforce.



# Manual Process

You added a new object into Salesforce

Open SQL Server and create a new view in the database. 
Name this view in this format: vw_Salesforce_Object__c.
Add your query to the view in this format:

select
'API_1__c'
,'API_2__c'
...
union all
select
cast([TABLE].APIdata1 as nvarchar(50)) as API_1__c
,cast([TABLE].APIdata2 as nvarchar(50)) as API_2__c
... 
FROM [SERVER].[database].[dbo].[TABLE]

To add a record that contains a master-detail custom object, use this format:

 select
'API_1__c'
,'Master__c}Detail__c'
...
union all
select
cast([TABLE].APIdata1 as nvarchar(50)) as API_1__c
,cast([TABLE].DetailData as nvarchar(50)) as Detail__c
...
FROM [SERVER].[database].[dbo].[TABLE]

Locate the Queries folder within the SFyPy folder and open it up. 
Create a new text file and name it in this format: 00-Object__c.txt
The two zeros represent the order you want the files to execute and the Object__c is the name of your custom object.
Open the text file and add your select from the view you created, then click save.
Example: Select * FROM [Database].[dbo].[vw_Object__c].

# From Dev to Production

If any changes are needing to be done to the code, then these are the steps to move the code from dev to production.

1. If you don't have Python installed on your machine, be sure to install the latest version.
2. After changes are made, use the pyinstaller in the command prompt to create an executable file - https://www.pyinstaller.org/
3. open cmd and if pyinstaller is not already on your machine, then use pip install pyinstaller.
4. In the cmd prompt, change directory and navigate to the folder where ScheduleJobs.py is located 
5. type 'pyinstaller ScheduleJob.py'
6. In your File Explorer, navigate to the folder ScheduleJob.py is stored and some new files/folders will have been created.
7. Go to dist, ScheduleJob, and copy the ScheduleJob.exe from that folder into Automate SFyPy


# Troubleshooting

Check Salesforce Bulk API results

Open Salesforce, and navigate to setup.
In the search bar, type "bulk" and the results should populate "Bulk Data Load Jobs".
In Bulk Data Load Jobs, find the object, then click its Job ID.
Click "View Result".
The error message for the record is in result>errors>message>.

Error message: 
    Foreign key external ID not found for field
Solution:
    Check that the value is in Salesforce. If it is not, then that value needs to be added to Salesforce.
    Example: 
    Invoice Number was the external ID for Shipment Tracking. 
    When upserting Tracking data, no Invoice was found for that Shipment resulting in the error message above.
    Either the Invoice needed to be added, or this tracking data needed to be skipped.

Error message:
    Comment Text: data value too large (max length=50)
Solution:
    Increase the size of the field in Salesforce, or reduce the text to under the max length as shown above.



