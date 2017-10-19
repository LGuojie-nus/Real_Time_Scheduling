import string
import random
import re
import math
import copy
from EDF_Scheduler import EDF_scheduler
from Task_Object import TaskIns, TaskType
from Task_Object import tasktype_cmp, priority_cmp



MAX_FREQUENCY=1000
PEAK_VALUE=30.0
V_TARGET_MAX=14.0
MAX_STORAGE=5000

global Cap #capacity
global Frame_number
global FRAME_LEN
global gamma

FRAME_LEN=300
Frame_number=140		   
Cap=30 
gamma=100
E_storage = 0
theta=1.0 
flag=''
Epv=0

# frequency, voltage, power, each coloum is a value set, P(f) and V(f)
processor=[[ 500, 600, 700, 800, 900, 1000],
		   [ 1.0, 1.2, 1.4, 1.6, 1.8,  2.0],
		   [0.62,0.89,1.21,1.58,2.00,2.47]]  

#period, arrival time, workload/max_frequency, deadline,task name, energy consumption,task_ID 
tasks=[ [ 50, 0, 10,  50, 'Task1', 24.7,  0],
		[ 60, 0, 10,  60, 'Task2', 24.7,  1],
		[100, 0, 15, 100, 'Task3', 37.05, 2],
		[150, 0, 15, 150, 'Task4', 37.05, 3],
		[300, 0, 30, 300, 'Task5', 74.1,  4],]  



def V_target(t):
    #Target Voltage
    return (-V_TARGET_MAX*(t+1)*(t-140)/4900)

def PV_Panel(t):
    #Power input
    return (-PEAK_VALUE*t*(t-140)/4900)

#converter energy loss
def P_conv_in(t,V_cap):
    effi=0.2
    return effi*PV_Panel(t)

#converter energy loss
def P_conv_out(freq,V_cap):
    return math.sqrt(freq)*V_cap/200

#actual input energy for a frame
def E_in(t,V_cap):
    return FRAME_LEN*(PV_Panel(t)-P_conv_in(t,V_cap))

#estimated total input energy
def Ee_in_total(t,V_cap,Frame_number):
    ans=0
    for i in xrange(t,Frame_number+1):
        ans+=(PV_Panel(i)-P_conv_in(t,V_cap))
    return ans*FRAME_LEN

#estimated total output energy
def Ee_out_total(t,energy_consump):
    #energy_consump:receive value from scheduler object
    return (Frame_number-t+1)*energy_consump
    
#total self discharge
def Ee_sd_total(t,V_cap,Frame_number):
    ans=0.1*(Frame_number-t+1)*Cap*math.pow(V_cap,2)*FRAME_LEN/gamma
    return ans

#self discharge for one frame
def E_sd(t,V_cap):
    return 0.1*Cap*math.pow(V_cap,2)*FRAME_LEN/gamma

def Print_results(alphabet):
    print format(frame,'>3d'),alphabet,format(V_tar, '>5.1f'),format(V_cap,'>4.1f'),format(Ee_in_tot,'>10.1f'),format(Ee_out_tot,'>10.1f'),format(Ein,'>8.1f'),format(E_storage,'6.1f'),format(E_consump,'>8.1f'),format(Ee_sd_tot,'>11.1f')
    return 1 

#assign random frequency to each task instance
def tasks_assign_random(tasks,processor,V_cap):
    new_tasks=copy.deepcopy(tasks)
    for task in new_tasks:
        i=random.randint(0,5)
        task[2]=task[2]*1000.0/processor[0][i]
        task[5]=(task[2])*(processor[2][i]+P_conv_out(processor[0][i],V_cap))
        task.append(processor[0][i])
    return new_tasks 

#find_optimal_freq at given V_cap: DVFS
def find_optimal_freq(processor,tasks,V_cap):
    #find optimal frequency for each task type
    optimal_freq=[[],[],[]]
    for task in tasks:
        res=[]
        for i in xrange(0,6):
            freq=processor[0][i]
            E_extract=(task[2]*1000/freq)*(processor[2][i]+P_conv_out(freq,V_cap))
            res.append(E_extract)
        minimal=min(res)
        index=res.index(minimal)
        optimal_freq[0].append(processor[0][index])
        optimal_freq[1].append(minimal)
        optimal_freq[2].append(task[2]*1000/processor[0][index])
    return optimal_freq

'''
Start of the program
Version:
Microsoft VS2015
Python 2.7
'''
def Interactive_input():
    Optimal_On_Off = raw_input("Optimal Frequency On/Off?")
    print "you entered", Optimal_On_Off
    Iteration = raw_input("How many rounds of simulation you want?")
    print "you entered",Iteration
    Print_detail = raw_input("Do you want to display details of each frame?(Y/N)")
    print "you entered",Print_detail
    return [Optimal_On_Off,Iteration,Print_detail] 

input=Interactive_input()

if input[2]=='Y' or input[2]=='y':
    print 'format','V_tar','V_cap','Ee_in_tot','Ee_sd_tot','   Ein','E_storage','E_consump','Ee_sd_tot'

#create task_scheduler object
Task_Scheduler=EDF_scheduler(tasks,processor,FRAME_LEN)

#loop for multiple simulation start here
for ind in range(0,int(input[1])):
    tasks_total=[0,0,0,0,0]
    #loop for one simulation start here
    for frame in xrange(1,Frame_number+1):
        #initialization
        V_cap=math.sqrt(2*E_storage/Cap)
        V_tar=V_target(frame) #manual set up target
    
        #randomly assign frequency to each task instance
        new_tasks=tasks_assign_random(tasks,processor,V_cap)
        Task_Scheduler.__init__(new_tasks,processor,FRAME_LEN)

        if input[0]=='on' or input[0]=='On' or input[0]=='ON':
            #find optimal frequency
            opt_freq_energy=find_optimal_freq(processor,tasks,V_cap)
            #update freq and energy in the tasks matrix
            Task_Scheduler.Task_freq_energy_update(opt_freq_energy)
    
        Task_Scheduler.Generate_taskIns()
        Task_Scheduler.Scheduler()
        E_consump=Task_Scheduler.Energy_consumption()
        Ee_out_tot=Ee_out_total(frame,E_consump)
        Ein=E_in(frame,V_cap)
        Esd=E_sd(frame,V_cap)
        Ee_in_tot=Ee_in_total(frame,V_cap,Frame_number)
        Ee_sd_tot=Ee_sd_total(frame,V_cap,Frame_number)
    
        if Ee_in_tot+E_storage>=Ee_out_tot+Ee_sd_tot and E_storage>E_consump+Esd-Ein: #implement algorithm 1, update E_storage
           
            #update E_storage
            E_storage+=Ein-E_consump-Esd
            if E_storage>MAX_STORAGE:
                E_storage=MAX_STORAGE
            flag='A'
        
            
        else:
            E_tar=0.5*Cap*math.pow(V_tar,2)	
            err_tar=E_storage-E_tar
            if err_tar>=0 and E_storage>E_consump+Esd-Ein:
                #implement algorithm 1, update E_storage
                E_storage+=Ein-E_consump-Esd
                if E_storage>MAX_STORAGE:
                    E_storage=MAX_STORAGE

                flag='B'
                
            else:
                if err_tar<0:
                    while(E_storage+Ein-E_consump-Esd<E_storage+theta*abs(err_tar)):                      
                        #drop most energy consuming tasks
                        Task_Scheduler.Drop_tasksIns()
                        #update scheudle 
                        Task_Scheduler.Scheduler()
                        E_consump=Task_Scheduler.Energy_consumption()
                                   
                    E_storage+=Ein-E_consump-Esd
                    if E_storage>MAX_STORAGE:
                        E_storage=MAX_STORAGE
                else:
                    while(E_storage<E_consump+Esd-Ein):
                        Task_Scheduler.Drop_tasksIns()
                        Task_Scheduler.Scheduler()
                        E_consump=Task_Scheduler.Energy_consumption()
                flag='C'    
        for i in xrange(0,5):
            tasks_total[i]+=Task_Scheduler.task_counter[i] 
        
        if input[2]=='Y' or input[2]=='y':                    
            Print_results(flag)
        Epv+=PV_Panel(frame)*300
       

    print ind,'total tasks executed',tasks_total,input[0]
    #print Epv


f = open('output.txt', 'w')
print >> f, 'Tasks_executed', tasks_total,',',input  # or f.write('...\n')
f.close()



