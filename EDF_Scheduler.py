from Task_Object import TaskIns, TaskType
from Task_Object import tasktype_cmp, priority_cmp

import re
import copy

class EDF_scheduler(object):
    def __init__(self,Task_Input,processor,FRAME_LENGTH):
        self.task_input=copy.deepcopy(Task_Input)
        self.processor=copy.deepcopy(processor)
        self.LCM=FRAME_LENGTH  #hyperperiod, or LCM, or FRAME_LENGTH
        self.energy_sum=0
        self.html = "<!DOCTYPE html><html><head><title>EDF Scheduling</title></head><body>"
        self.html_color = { 'Task1':'red', 'Task2':'blue', 'Task3':'green', 'Task4':'aqua', 'Task5':'coral', 'Empty':'grey', 'Finish':'black'}
        self.tasksIns=[]
        self.task_counter=[0,0,0,0,0]

    def Task_freq_energy_update(self,opt_freq_list):
        #Update frequency and Energy
        for i in xrange(0,5):
            if self.task_input[i][7]<opt_freq_list[0][i]:
                self.task_input[i][2]=opt_freq_list[2][i]
                self.task_input[i][5]=opt_freq_list[1][i]
        
        return 1

                 
    def Generate_taskIns(self):
        task_types = []
        tasks=[]
        for row in self.task_input:
            task_types.append(TaskType(period=row[0], release=row[1], execution=row[2], deadline=row[3], name=row[4]))
        
        #Sort types EDF
        task_types = sorted(task_types, tasktype_cmp)
        task_counter=[0, 0, 0, 0, 0]
        for i in xrange(0, self.LCM):
            for task_type in task_types:
                if  (i - task_type.release) % task_type.period == 0 and i >= task_type.release:
                    start = i
                    end = start + task_type.execution
                    priority = start + task_type.deadline
                    if task_type.name=='Task1':
                        task_counter[0]+=1
                        tasks.append(TaskIns(start=start, end=end, priority=priority, name=task_type.name,id=task_counter[0],engy=self.task_input[0][5]))
                    elif task_type.name=='Task2':
                        task_counter[1]+=1
                        tasks.append(TaskIns(start=start, end=end, priority=priority, name=task_type.name,id=task_counter[1],engy=self.task_input[1][5]))
                    elif task_type.name=='Task3':
                        task_counter[2]+=1
                        tasks.append(TaskIns(start=start, end=end, priority=priority, name=task_type.name,id=task_counter[2],engy=self.task_input[2][5]))
                    elif task_type.name=='Task4':
                        task_counter[2]+=1
                        tasks.append(TaskIns(start=start, end=end, priority=priority, name=task_type.name,id=task_counter[3],engy=self.task_input[3][5]))
                    elif task_type.name=='Task5':
                        task_counter[2]+=1
                        tasks.append(TaskIns(start=start, end=end, priority=priority, name=task_type.name,id=task_counter[4],engy=self.task_input[4][5]))    
        self.tasksIns=tasks  
        self.tasksIns.sort(key=lambda TaskIns:TaskIns.engy)
        return self.tasksIns 

    def Drop_tasksIns(self):
        #sort the schdule in descending order of energy consumption 
        #drop one by one
        if not self.tasksIns:
            return 0
        else: 
            self.tasksIns.pop()
            return 1

    def Scheduler(self): 
        self.task_counter=[0,0,0,0,0]
        if not self.tasksIns:
            return 0
        else:
            #generate a schedule use optimal frequency
            #calculate the energy consumption 
            
            clock_step = 1
            tasksIns_copy=copy.deepcopy(self.tasksIns)
            for i in xrange(0, self.LCM, clock_step):
                #Fetch possible tasks that can use cpu and sort by priority
                possible = []
                for t in tasksIns_copy:
                    if t.start <= i and i+t.end-t.start<=t.priority+t.usage:  #remove those cannot be finished before deadline
                        possible.append(t)
                possible = sorted(possible, priority_cmp)

                #Select task with highest priority
                if len(possible) > 0:
                    on_cpu = possible[0]
                    #print on_cpu.get_unique_name() , " uses the processor. " , 
                    self.html += '<div style="float: left; text-align: center; width: 110px; height: 20px; background-color:' + self.html_color[on_cpu.name] + ';">' + on_cpu.get_unique_name() + '</div>'
                    if on_cpu.use(clock_step):
                        #find the name tag of this cask
                        task_index=re.findall('\d+', on_cpu.name)
                        task_index=int(task_index[0])-1
                        self.task_counter[task_index]+=1
                        tasksIns_copy.remove(on_cpu)
                        self.html += '<div style="float: left; text-align: center; width: 10px; height: 20px; background-color:' + self.html_color['Finish'] + ';"></div>'
                else:
                    self.html += '<div style="float: left; text-align: center; width: 110px; height: 20px; background-color:' + self.html_color['Empty'] + ';">Empty</div>'
            self.html += "<br /><br />"
            for p in self.tasksIns:
                #print p.get_unique_name() + " is dropped due to overload!"
                self.html += "<p>" + p.get_unique_name() + " is dropped due to overload!</p>"
        
            #Html output end
            self.html += "</body></html>"
            
        return 1
    
      
      
        

    def print_html(self):
        output = open('output.html', 'w')
        output.write(self.html)
        output.close()

        return 1

    def Energy_consumption(self):
        self.energy_sum=0
        for i in xrange(0,5):
            self.energy_sum+=self.task_input[i][5]*self.task_counter[i]
        return self.energy_sum

    def Implement_Algorithm1(self,opt_freq_list):
        Task_freq_energy_update(self,opt_freq_list)
        Generate_taskIns(self)
        Scheduler(self)
        Energy_consumption(self)