import json

def tagIDToTag(p):
  with open(p) as infile:
    data = json.load(infile)

  res = {}
  for c, j in data.iteritems() :
    jobs = j["jobs"]
    for sk in jobs:
      if sk["name"] not in res and sk["tag_type"] == "SkillTag":
        res[sk["name"]] = sk["id"] #skillTag?

  with open('json/skills_id.json', 'w') as outfile:
    json.dump(res, outfile)

#TODO: could also do a tag_name to company id 
#i'd then open json file in an outer wrapping function
if __name__ == '__main__':
  tagIDToTag('json/alljobs.json')

  def vectorCompDict(self, data, al):
    skill_to_id = load_json('json/skills_id.json')
    vec_info = {}
    for k, v in data.iteritems() :
      if v in skill_to_id:
        # print skill_to_id[v]
        info = al.getJobByTag(al.access_token, skill_to_id[v])["jobs"]
        for comp in info : #comp is a dict with that startup's info and all jobs it's offering
          startup = comp["startup"]
          jobs = comp["tags"]
          c_id = startup["id"]
          name = startup["name"]
          #store comp
          for j in comp["tags"]:
            if k in j["name"] : #j["name"] is the skill name
              if c_id not in vec_info:
                vec_info[c_id] = {j["name"] : 1}
              else: #what if the skill isnt' there yet? :'D
                print j["name"]
                if j["name"] in  vec_info[c_id] :
                  vec_info[c_id][j["name"]] += 1
                else:
                  vec_info[c_id][j["name"]] = 1
    write_json('json/comp_vec_dict.json', vec_info)

