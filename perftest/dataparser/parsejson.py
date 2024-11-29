import json
import sys
import os
import re

hostcpudict = {}
hostmemdict = {}

nodecpudict = {}
nodememdict = {}
nodecpupercent = {}
nodemempercent = {} 
pp_podcpudict = {}
pp_podmemdict = {}
ppac_podcpudict = {}
ppac_podmemdict = {}
ppp_podcpudict = {}
ppp_podmemdict = {}
ppgp_podcpudict = {}
ppgp_podmemdict = {} 

dictlist=[ hostcpudict, hostmemdict,
    nodecpudict,nodecpupercent,nodememdict,nodemempercent,pp_podcpudict,pp_podmemdict,ppac_podcpudict,ppac_podmemdict,ppp_podcpudict,ppp_podmemdict,ppgp_podcpudict,ppgp_podmemdict]

def processNode(data,index,topfile):
    nodecpudict[index] = data["items"][0]["usage"]["cpu"][:-1]
    nodememdict[index] = data["items"][0]["usage"]["memory"][:-2]
    with open(sys.argv[1]+topfile, 'r') as f:
        line = f.readlines()[1]
        fields = line.split()
        nodecpupercent[index] = fields[2][:-1]
        nodemempercent[index] = fields[4][:-1]
    return

def processHost(data,index,topfile):
    with open(sys.argv[1]+topfile, 'r') as f:
        data = f.read()

    cpu_match = re.search(r'Average CPU Usage: ([0-9.]+)%', data)
    memory_match = re.search(r'Average Memory Used: (\d+) KB', data)

    if cpu_match and memory_match:
        hostcpudict[index] = float(cpu_match.group(1))
        hostmemdict[index] = int(memory_match.group(1))
    return

class PodVals:
    def __init__(self):
        self.cpusum = 0
        self.cpunums = 0
        self.memsum = 0
        self.memnums = 0

    def add_cpu(self, cpuval):
        #print(cpuval)
        if cpuval!="0":
            self.cpusum += int(cpuval[:-1])
            self.cpunums += 1

    def add_mem(self, memval):
        #print(memval)
        if memval!="0":
            self.memsum += int(memval[:-2])
            self.memnums += 1
    
    def get_avg(self):
        memavg=0
        cpuavg=0
        #print(self.memsum)
        #print(self.cpusum)

        if self.memnums!=0:
            memavg=self.memsum/self.memnums
        if self.cpunums!=0:
            cpuavg=self.cpusum/self.cpunums
        return cpuavg, memavg

def processPod(data,index):
    ppac = PodVals()
    pp = PodVals()
    ppgp = PodVals() 
    ppp = PodVals() 
  
    for item in data["items"]:
        if len(item["containers"]) == 0:
            continue
        #print(item)
        if "authorize-cc" in item["containers"][0]["name"]:
            ppac.add_cpu(item["containers"][0]["usage"]["cpu"])
            ppac.add_mem(item["containers"][0]["usage"]["memory"])
        elif "product-purchase-publish" in item["containers"][0]["name"]:
            ppp.add_cpu(item["containers"][0]["usage"]["cpu"])
            ppp.add_mem(item["containers"][0]["usage"]["memory"])
        elif "product-purchase-get-price" in item["containers"][0]["name"]:
            ppgp.add_cpu(item["containers"][0]["usage"]["cpu"])
            ppgp.add_mem(item["containers"][0]["usage"]["memory"])
        elif "product-purchase" in item["containers"][0]["name"]:
            pp.add_cpu(item["containers"][0]["usage"]["cpu"])
            pp.add_mem(item["containers"][0]["usage"]["memory"])
        
    pp_podcpudict[index], pp_podmemdict[index] = pp.get_avg()
    ppp_podcpudict[index], ppp_podmemdict[index] = ppp.get_avg()
    ppac_podcpudict[index], ppac_podmemdict[index] = ppac.get_avg()
    ppgp_podcpudict[index], ppgp_podmemdict[index] = ppgp.get_avg()

    return

if __name__== '__main__':
    # the first argument is the directory name to process
    for filename in os.listdir(sys.argv[1]):
        if filename.endswith(".json"): 
            data = json.load(open(sys.argv[1]+filename, 'r'))
            index = int("".join(filter(str.isdigit, filename)))
            if filename.startswith("node"):
                topfile = os.path.dirname(filename)+"nodetop"+str(index)+".txt"
                processNode(data,index,topfile)
                hosttopfile = os.path.dirname(filename)+"top"+str(index)+".txt"
                processHost(data, index, hosttopfile)
            elif filename.startswith("pod"):
                processPod(data,index)
        else:
            pass


    #for dictionary in dictlist:
    #    print(dictionary)
    
    output = open(sys.argv[2], "w")
    output.write("Index,HostCPU,HostMem,NodeCPU,NodeCPU%,NodeMEM,NodeMEM%,PP_CPU,PP_MEM,PPAC_CPU,PPAC_MEM,PPP_CPU,PPP_MEM,PPGP_CPU,PPGP_MEM\n")
    
    for i in range(1,99):
        line = ",".join(list(map(lambda x: str(x[i]),dictlist)))
        output.write(str((i-1)*15)+","+line+"\n")
        print(line)

    output.close()

