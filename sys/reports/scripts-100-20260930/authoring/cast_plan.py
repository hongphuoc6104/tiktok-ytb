# Main companion is mustard; an additional professional/guest is lavender.
CAST={
246:('Adult classroom teacher',['teacher'],'Adult fellow learner',['friend']),
247:('Adult paper-folding instructor',['instructor','teacher'],None,[]),
248:('Adult dinner companion',['friend'],'Adult invited dinner guest',['arriving adult','guest']),
252:('Adult packing supervisor',['supervisor'],None,[]),
255:('Adult woman factory worker',['worker','woman'],'Adult visitor guide',['guide']),
256:('Adult friend whose father farms',['friend'],'Adult father and farmer',['farmer','father']),
257:('Adult woman engineer',['engineer','woman'],'Adult companion',['friend']),
258:('Adult companion passenger',['friend','companion','passenger'],'Adult driver',['driver']),
259:('Adult travel companion',['friend'],'Adult female police officer',['officer']),
260:('Adult painter',['painter'],'Adult companion',['friend']),
261:('Adult male singer',['singer','performer'],'Adult organizer and stage helper',['organizer','helper']),
262:('Adult male actor',['actor','performer'],'Adult companion',['friend']),
263:('Adult sister and writer',['sister','writer'],'Adult visiting friend',['friend']),
264:('Adult friend whose uncle cooks',['friend'],'Adult uncle and cook',['cook','uncle']),
266:('Adult acquaintance and colleague',['acquaintance'],None,[]),
282:('Adult cafe employee',['staff'],None,[]),
289:('Adult travel companion',['friend'],'Adult information attendant',['attendant']),
292:('Adult travel companion',['friend'],'Adult bus driver',['driver']),
297:('Adult travel companion',['friend'],'Adult dock attendant',['attendant']),
301:('Adult travel companion',['friend'],'Adult local pedestrian giving directions',['pedestrian','local']),
303:('Adult travel companion',['friend'],'Adult checkpoint attendant',['attendant']),
304:('Adult reader occupying neighboring seat',['reader'],None,[]),
306:('Adult travel companion',['friend'],'Adult airport attendant',['attendant']),
307:('Adult friend who drives the car',['friend','driver'],None,[]),
309:('Adult friend driving the car',['driver'],'Adult parking attendant',['attendant']),
310:('Adult friend meeting at hotel',['friend'],'Adult pedestrian giving directions',['pedestrian']),
311:('Adult travel companion',['friend'],'Adult hotel receptionist',['receptionist']),
312:('Adult travel companion',['friend'],'Adult hotel pool employee',['staff','attendant']),
315:('Adult travel companion',['friend'],'Adult hotel receptionist',['receptionist']),
318:('Adult friend living in town',['friend'],'Adult shopkeeper',['shopkeeper']),
319:('Adult visiting friend',['friend'],'Grandmother in modest plain lavender clothing',['grandmother']),
320:('Adult companion helping find street',['friend'],'Adult acquaintance waiting at cafe',['acquaintance']),
321:('Adult travel companion',['friend'],'Adult local pedestrian',['local']),
323:('Adult walking companion',['companion'],'Adult friend waiting across river',['waiting friend','waiting person']),
328:('Adult travel companion',['friend'],'Adult postal clerk',['clerk']),
330:('Adult companion',['friend'],'Adult entrance attendant',['adult at entrance']),
339:('Adult walking companion',['friend'],'Adult waiting acquaintance',['acquaintance']),
340:('Adult local giving directions',['local','adult'],None,[]),
}
def apply_cast(n,c):
 name2,keys2,name3,keys3=CAST.get(n,('Adult friend or companion',['friend','companion','colleague'],None,[]))
 c['characters'][1]['appearance']=name2+'. Minimal flat ink style; consistent adult face, age, gender and identity across all scenes. Distinct from canonical mascot. Plain mustard top; only explicitly required work outerwear, helmet or life jacket.'
 c['characters'][1]['name']='Nhân vật đồng hành chính'
 if name3:
  c['characters'][2]['appearance']=name3+'. Minimal flat ink style; keep one consistent adult identity across scenes. Distinct from mascot and main companion. Plain lavender top with explicitly required professional outerwear only.'
 else:c['characters']=c['characters'][:2]
 for sc in c['scenes']:
  v=sc['action'].lower();ids=['CH01']
  if any(w in v for w in keys2) or any(w in v for w in ['both','two people','two friends','travelers','two adults']):ids.append('CH02')
  if name3 and any(w in v for w in keys3):ids.append('CH03')
  sc['character_ids']=ids
  for im in sc['images']:im['character_ids']=ids
