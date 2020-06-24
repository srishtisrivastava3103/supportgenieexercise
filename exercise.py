'''Assume that we have a table called Agent_Availability with Attributes- issue_id, start_time, abandoned_time, 
answer_time, resolved_time, wait_time, resolving_time, avg_wait_time, avg_resolving_time
issue_id: PRIMARY KEY
avg_wait_time: Average of all previous wait times
resolving_time=resolved_time-answer_time
avg_resolving_time: Average of all resolving times'''

import sqlite3
from datetime import datetime
from datetime import timedelta

conn = sqlite3.connect('support.db')
c=conn.cursor()
sql_select_Query='select * from Agent_Availability'
c.execute(sql_select_Query)
records=c.fetchall()
    

def to_td(h): #converts to timedelta object
    ho, mi, se = h.split(':')
    return timedelta(hours=int(ho), minutes=int(mi), seconds=int(se))

def new_wait_time(start_time):
    FMT = '%H:%M:%S'
    
    if records[-1][4] == None and records[-1][2] == None: #if previous issue is neither resolved nor abandoned
        
        if start_time<records[-1][1]: #if start_time< last start time
            print("Can't work on past time. Please select time after ",records[-1][1]) #Select a time after last start time
            return
    
        #predicted_wait_time = (avg_wait_time[-1]+(avg_resolved_time[-1]-answer_time[-2]))
        previous_issue_timelag = str(datetime.strptime(records[-2][-1], FMT) - (datetime.strptime(start_time,FMT)-datetime.strptime(records[-1][3], FMT))).split()[1]
        temp = [records[-1][-4],previous_issue_timelag]
        predicted_wait_time = str(sum(map(to_td,temp), timedelta()))

    else: #if previous issue is closed
        
        if records[-1][2]!=None and start_time < records[-1][2]: #if previous issue was abandoned and start time is less than previous abandoned time
            print("Can't work on past time. Please select time after ",records[-1][2]) #Select a time after previous abandoned time
            return
        if records[-1][2] == None and start_time < records[-1][4]:#if last issue was not abandoned and start_time is less than previous resolved time 
            print("Can't work on past time. Please select time after ",records[-1][4])#Select a time after last resolved time
            return

    
        predicted_wait_time = records[-1][-2]  #predicted_wait_time=avg_wait_time
    return(predicted_wait_time)


'''You can add an entry to the table through the given function or directly in the database.'''

def add_entry():
    FMT = '%H:%M:%S'
    h1 = []
    h2 = []
    issue_id = int(input("Enter issue id: "))
    start_time = input("Enter start time: ")
    abandoned = input("Was the issue abandoned? [y/n]: ")
    
    if abandoned.lower() == 'y':
        abandoned_time = input("Enter Abandoned Time: ")
        answer_time = None
        resolved_time = None
        wait_time = None
        resolving_time = None
        avg_wait_time = records[-1][-2]
        avg_resolving_time = records[-1][-1]
        
    elif abandoned.lower() == 'n':
        answer_time = input("Enter Answer Time: ")
        resolved_time = input("Enter Resolved Time: ")
        abandoned_time = None
        wait_time = str(datetime.strptime(answer_time, FMT) - datetime.strptime(start_time, FMT))
        
        for col in records: #Finding avg_wait_time
            h1 = h1 + [col[-4]]
            h1 = h1 + [wait_time]
        avg_wait_time = str((sum(map(to_td, h1), timedelta()))/len(h1))
        
        resolving_time=str(datetime.strptime(resolved_time, FMT) - datetime.strptime(answer_time, FMT))
        #Finding avg_resoving_time
        for col in records:
            h2 = h2 + [col[-3]]
        h2 = h2 + [resolving_time]
        avg_resolving_time = str((sum(map(to_td, h2), timedelta()))/len(h2))
        
    else:
        print("Invalid Entry: Please Enter y/n")
        return
    
    input_list = [issue_id,start_time,abandoned_time,answer_time,resolved_time,wait_time,resolving_time,avg_wait_time,avg_resolving_time]
    c.execute('insert into Agent_Availability values (?,?,?,?,?,?,?,?,?)', input_list)
    print("Entry successful!")
    conn.commit()
    c.close()
    conn.close()

            
        
    
# add_entry() 
print("Predicted Wait Time: ",new_wait_time('14:07:00'))
   