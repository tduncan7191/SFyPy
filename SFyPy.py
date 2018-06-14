###############################################################################
#                                                                             #
#                 SFyPy Salesforce Python dataLoader                          #
#                                                                             #
###############################################################################

import os
from tkinter import *
import tkinter.scrolledtext as tkscrolled
import tkinter.messagebox as tkMessageBox
import Job

settingsPath = os.getcwd() + "\settings.txt" 
arrAction = ['upsert','insert','update'] 

with open(settingsPath, "r") as f: 
        settings = f.read()

txtRecordType, optionAction, txtServerName, txtDatabaseName, txtServerUsername, txtServerPassword, txtSfUsername, txtSfPassword, txtSfSecurityToken, txtUseSfSandbox = settings.split('|')
    
def main():
    root = Tk()
    root.title('SFyPy')
    root.resizable(width=False, height=False)
    render(root)
            
def btnGenerate_Clicked():
    try:
        queryResult = Job.executeQuery(str(eQuery.get(1.0, END)), str(eRecordType.get()))
        tkMessageBox.showinfo("Finished", queryResult)
    except Exception as e:
        tkMessageBox.showinfo("Error", e)        

def btnSave_Clicked():
    try:
        with open(settingsPath, 'w') as f:
            f.write(eRecordType.get() + "|" + strVarAction.get() + "|" + eServerName.get() + "|" + eDatabaseName.get() + "|" + eServerUsername.get() + "|" + eServerPassword.get() + "|" + eSfUsername.get() + "|" + eSfPassword.get() + "|" + eSfSecurityToken.get() + "|" + str(vUseSfSandbox.get()))

        #queryPath = os.getcwd() + "\\Queries\\" + eRecordType.get() + ".txt" 
        #with open(queryPath, 'w+') as f:
        #    f.write(eQuery.get(1.0, END))
        
        tkMessageBox.showinfo("Saved", "Your settings have been saved.")
    except Exception as e:
        tkMessageBox.showinfo("Error", e)

def btnRunAll_Clicked():
    try:
        result = Job.main()
        tkMessageBox.showinfo("Finished", result)
                 
    except Exception as e:
        tkMessageBox.showinfo("Error", str(e))


def btnRun_Clicked():    
    try:   
        if(str(eRecordType.get()) == ""):
            tkMessageBox.showinfo("Error", "Enter an object to update")
            return
        
        Job.executeQuery(str(eQuery.get(1.0, END)), str(eRecordType.get()))        
        rows = Job.readCSV(str(eRecordType.get()))        
        result = Job.uploadResultsToSalesforce(str(eRecordType.get()), str(strVarAction.get()), rows, str(eSfUsername.get()), str(eSfPassword.get()), str(eSfSecurityToken.get()), str(vUseSfSandbox.get()))           
        tkMessageBox.showinfo("Finished", result)
                 
    except Exception as e:
        tkMessageBox.showinfo("Error", str(e))
        
def render(root):
    try:
        queryPath = os.getcwd() + "\\queries\\" + txtRecordType + ".txt" 
        with open(queryPath, "r") as f: 
            global txtQuery
            txtQuery = f.read()
    except Exception as e:
        txtQuery = ""
        
    lblSfUsername = Label(root, text="Salesforce Username")
    lblSfUsername.grid(row=1, column=0)

    global eSfUsername
    vSfUsername = StringVar(root, value=txtSfUsername)
    eSfUsername = Entry(root, textvariable=vSfUsername, width=130)
    eSfUsername.grid(row=1, column=1)
    
    lblSfPassword = Label(root, text="Salesforce Password")
    lblSfPassword.grid(row=2, column=0)
    
    global eSfPassword
    vSfPassword = StringVar(root, value=txtSfPassword)
    eSfPassword = Entry(root, show="*", textvariable=vSfPassword, width=130)
    eSfPassword.grid(row=2, column=1)
    
    lblSfSecurityToken = Label(root, text="Salesforce Security Token")
    lblSfSecurityToken.grid(row=3, column=0)

    global eSfSecurityToken
    vSfSecurityToken = StringVar(root, value=txtSfSecurityToken)
    eSfSecurityToken = Entry(root, show="*", textvariable=vSfSecurityToken, width=130)
    eSfSecurityToken.grid(row=3, column=1)

    global vUseSfSandbox
    vUseSfSandbox = IntVar(root, value=txtUseSfSandbox)
    chkUseSfSandbox = Checkbutton(root, text="Use Salesforce Sandbox", variable=vUseSfSandbox)
    chkUseSfSandbox.grid(row=4, column=0)
    
    lblRecordType = Label(root, text="Object")
    lblRecordType.grid(row=5, column=0)

    global eRecordType
    vRecordType = StringVar(root, value=txtRecordType)
    eRecordType = Entry(root, textvariable=vRecordType)
    eRecordType.grid(row=5, column=1)

    lblAction = Label(root, text="Action")
    lblAction.grid(row=6, column=0)

    global strVarAction
    strVarAction = StringVar()
    strVarAction.set(optionAction) 
    omAction = OptionMenu(root,strVarAction,*arrAction)
    omAction.grid(row=6, column=1)
    
    lblQuery = Label(root, text="Query")
    lblQuery.grid(row=7, column=0)

    global eQuery
    eQuery = tkscrolled.ScrolledText(root, height=20, width=100)
    eQuery.insert(INSERT, txtQuery)
    eQuery.grid(row=7, column=1)

    lblServerName = Label(root, text="Server Name")
    lblServerName.grid(row=8, column=0)

    global eServerName
    vServerName = StringVar(root, value=txtServerName)
    eServerName = Entry(root, textvariable=vServerName, width=130)
    eServerName.grid(row=8, column=1)

    lblDatabaseName = Label(root, text="Database Name")
    lblDatabaseName.grid(row=9, column=0)

    global eDatabaseName
    vDatabaseName = StringVar(root, value=txtDatabaseName)
    eDatabaseName = Entry(root, textvariable=vDatabaseName, width=130)
    eDatabaseName.grid(row=9, column=1)

    lblServerUsername = Label(root, text="Server Username")
    lblServerUsername.grid(row=10, column=0)

    global eServerUsername
    vServerUsername = StringVar(root, value=txtServerUsername)
    eServerUsername = Entry(root, textvariable=vServerUsername, width=130)
    eServerUsername.grid(row=10, column=1)

    lblServerPassword = Label(root, text="Server Password")
    lblServerPassword.grid(row=11, column=0)

    global eServerPassword
    vServerPassword = StringVar(root, value=txtServerPassword)
    eServerPassword = Entry(root, show="*", textvariable=vServerPassword, width=130)
    eServerPassword.grid(row=11, column=1)
    
    lblHidden = Label(root)
    lblHidden.grid(row=12, column=0)

    btnSave = Button(root, text="Save Settings", command=btnSave_Clicked)
    btnSave.grid(row=13, column=0)

    btnRun = Button(root, text="Upload Query", command=btnRun_Clicked)
    btnRun.grid(row=13, column=2)
    
    btnRunAll = Button(root, text="Upload all CSVs", command=btnRunAll_Clicked)
    btnRunAll.grid(row=13, column=3)
    
    btnGenerate = Button(root, text="Generate Test File", command=btnGenerate_Clicked)
    btnGenerate.grid(row=13, column=1)
    
    lblHidden = Label(root)
    lblHidden.grid(row=14, column=0)

    root.update()
    root.mainloop()

main()
