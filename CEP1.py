from random import randint
from pyamaze import maze,agent

def sugGen(dirs,pSize,jSize,choice=True): # produces a random population 
    if choice: return [[dirs[randint(0,3)] for __ in range(jSize)] for _ in range(int(pSize+pSize/4))]
    return [[dirs[_]]*jSize for __ in range(int(pSize/4)) for _ in range(4)] + [['N']*int(jSize/2)+['W']*int(jSize/2) for _ in range(int(pSize/4))]

def mutation(dirs,pop): # function to perform mutation on the population, (100-58=)42% chance of mutation of every gene
    mut=lambda l: dirs[randint(0,3)] if randint(0,100)>=58 else l
    return [[mut(j) for j in i] for i in pop]

def crossover(pop,fitnessList): # function to perform random point crossover on the population
    for i in range(0,int(len(fitnessList)/2),2):
        x= randint(2,len(pop[0])-2)
        pop[fitnessList[-i-1][-1]]=pop[fitnessList[i][-1]][:x]+pop[fitnessList[i+1][-1]][x:]
        pop[fitnessList[-i-2][-1]]=pop[fitnessList[i+1][-1]][:x]+pop[fitnessList[i][-1]][x:]
    return pop

def pathPTs(r,c,dirKey,chro): # returns the path followed by the chromosome
    for i in chro:
        r+=dirKey[i][0]
        c+=dirKey[i][1]
        yield (r,c)

def obsVals(mMap,sp,dirKey,chro,chrId=0): # returns the fitness value, end point and id of current chromosome
    obs,endPointReached=0,False
    path=(sp,*pathPTs(*sp,dirKey,chro))
    for i in range(len(chro)):
        if path[i]==(1,1):
            endPointReached=True
            break
        try: 
            if mMap[path[i]][chro[i]]==0:obs+=1
        except: obs+=2
    obs+=int(1.5*(len(path)-len(set(path))))
    return (obs, (1,1) if endPointReached else path[-1], chrId)

def fitness(mMap,pop,spd,dirKey):
    return tuple(sorted([obsVals(mMap,spd,dirKey,pop[ind],ind) for ind in range(len(pop))]))

def regression(ptDir,pathDir,regC,blackList):
    for _ in range(regC):
        if len(pathDir)>0:
            # pathDir.popitem()
            last_item = pathDir.popitem()
            if _==0:blackList.append(last_item[1])
        if len(ptDir)>1:ptDir.pop()
        else:return 0,ptDir,pathDir,blackList
    return 1,ptDir,pathDir,blackList

def check_solution(path,start,dirKey,mMap): # checks if the solution path is valid
    if obsVals(mMap,start,dirKey,path,0)[0]==0:
        allPoints=list(pathPTs(*start,dirKey,path)) # this path does not have the start point thus the previous value of path corresponds to each point
        if (1,1) in allPoints: return path[:allPoints.index((1,1))+1]
        return path
    else: return False

r,c=eval(input("Enter the number of rows and columns you would like in your map: "))
pSize=eval(input("Enter population size (100 suggested minimum): "))
jSize=eval(input("How many steps should the program solve at once (10 suggested): "))
loopPer=eval(input('Enter the loop percent for this maze: '))
pop_rng=eval(input('How many generations should each step run for? (scale the value with map size) \n(suggested: 300-1200 for loopPercent<70 and 200-400 for loopPercent>70): '))
re=eval(input('How many times should the program try the same starting point before regressing? '))-1
dirs,dirKey=["N","W","S","E"],{"N":(-1,0),"E":(0,1),"S":(1,0),"W":(0,-1)}
m=maze(r,c)
m.CreateMaze(loadMaze='maze--2023-04-02--12-39-28.csv') # saveMaze=True,loopPercent=loopPer #loadMaze='.csv'
mMap=m.maze_map
genPathDir,startPointDir,blackList={},[(r,c)],[]
oo7,regr,regC=agent(m,filled=True,footprints=True),0,0
d=50 if (r*c)>=300 else 150
while True:
    if loopPer<=30:pop=sugGen(dirs,pSize,jSize)
    elif loopPer>=75: pop=sugGen(dirs,pSize,jSize,False)  
    else: pop=sugGen(dirs,int(pSize/2),jSize)+sugGen(dirs,int(pSize/2),jSize,False)
    check=False
    for _ in range(pop_rng):
        fitnessList=fitness(mMap,pop,startPointDir[-1],dirKey)
        # if fitnessList[0][0]==0:
        #     chrId,sp=fitnessList[0][-1],fitnessList[0][1]
        for fitVal,sp,chrId in fitnessList:
            if fitVal>0:break
            chromosome,dirlen=pop[chrId],len(genPathDir)
            addition=check_solution(genPathDir[dirlen]+chromosome if dirlen else chromosome,startPointDir[0],dirKey,mMap)
            if addition and addition not in blackList:
                genPathDir[dirlen+1]=addition
                startPointDir.append(sp)
                print(f'ye {dirlen+1}')
                check=True
                break
        if check:break 
        pop=mutation(dirs,crossover(pop,fitnessList))
    if startPointDir[-1]==(1,1): break
    if regr>re: 
        regr=0
        regC,startPointDir,genPathDir,blackList=regression(startPointDir,genPathDir,regC,blackList)
        # regC,startPointDir,genPathDir=regression(startPointDir,genPathDir,regC)
        print('Nom')
    regr+=1
pathStr=''.join(map(str,genPathDir[len(genPathDir)]))
m.tracePath({oo7:pathStr},delay=d)
m.run()