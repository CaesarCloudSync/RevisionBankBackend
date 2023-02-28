from physicsaqa import PhysicsAQA

data = PhysicsAQA().collectdata()
#print(data.keys())
#chapt = list({"label":chapter,"value":ind}for ind,chapter in enumerate(list(data.keys())))
#print(chapt)
topic = list(top for dic in list(data.values()) for top in dic.keys() if "MS" not in top)
topicms = list(top for dic in list(data.values()) for top in dic.keys() if "MS" in top)
resulttop = [{"label":top,"value":ind} for ind,top in enumerate(topic)]
resulttopms = [{"label":top,"value":ind} for ind,top in enumerate(topicms)]
#print(resulttop)
dic = {}
dic["physicsaqadata"] = {}
for key,val in data.items():
    dic["physicsaqadata"][key] = [{"label":val,"value":ind}for ind,val in enumerate(list(val.keys()))]

## = list(for key,val in data.items())
print(dic) #["physicsaqadata"]["Section 2: Particles & Radiation"]
