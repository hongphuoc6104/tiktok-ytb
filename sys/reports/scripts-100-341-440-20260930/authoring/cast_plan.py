import copy
# Explicit role allocation. Mascot core appearance never changes.
CAST={
376:('Adult animal caretaker',['caretaker','carer'],None,[]),
378:('Adult travel companion',['friend','companion'],'Adult farm guide',['guide']),
379:('Adult travel companion',['friend','companion'],'Adult farm guide',['guide']),
380:('Adult travel companion',['friend','companion','visitors'],'Adult farm guide',['guide','caretaker']),
394:('Adult friend receiving the rose',['friend'],'Adult florist',['florist','vendor']),
395:('Adult visiting companion',['friend','companion'],'Adult uncle who hosts the farm visit',['uncle','host']),
401:('Adult spectator friend',['friend','supporter'],'Adult football player wearing mustard practice bib',['player']),
403:('Adult teammate in friendly table tennis match',['teammate'],'Adult opposing player and scorekeeper at rest',['scorekeeper','opponent']),
404:('Adult friend in beanbag game',['friend'],None,[]),
405:('Adult friend explaining card game',['friend'],'Adult third participant',['two adults','group']),
406:('Adult spectator companion',['friend','spectators'],'Adult scoring football player',['player','team']),
412:('Adult friend at pool reception',['friend'],'Adult swimming instructor',['instructor']),
414:('Adult football friend',['friend'],'Adult additional football participant',['third','group','two adult']),
416:('Adult volleyball friend',['friend'],'Adult additional volleyball participant',['group','teammates','friends']),
420:('Adult friend choosing a swimming class',['friend'],'Adult reception employee',['staff','receptionist']),
421:('Adult cycling companion',['friend'],'Adult additional cycling participant',['group','friends']),
424:('Adult friend waiting at cinema',['friend'],'Adult mall attendant',['attendant']),
425:('Adult viewing companion',['friend'],'Fictional adult woman interviewed on television, appears only within the screen',['interviewee']),
428:('Adult companion watching news',['friend'],'Fictional adult news presenter, visible only within screen',['presenter']),
432:('Adult friend posing for photograph',['friend','adults'],'Adult second portrait participant',['two adults','group']),
433:('Adult event presenter',['presenter','friend'],'Adult sound helper and listener',['helper','listeners']),
435:('Adult friend explaining tabletop game',['friend'],'Adult third participant',['two adults','three adults']),
437:('Adult listening companion',['friend'],'Adult additional gathering guest',['group']),
439:('Adult friend singing with mascot',['friend'],'Adult audience member',['group']),
440:('Adult audience companion',['friend'],'Adult band singer on stage',['band','singer']),
}
def apply_cast(n,c):
 name2,keys2,name3,keys3=CAST.get(n,('Adult friend or companion',['friend','companion','both','two people','two adults'],None,[]))
 c['characters'][1]['appearance']=name2+'. Minimal flat ink style. Maintain age, gender, clothing and identity across all scenes; use mustard top and only explicitly needed accessory. Distinct from canonical mascot.'
 c['characters'][1]['name']='Người đồng hành trong tình huống'
 if name3:c['characters'][2]['appearance']=name3+'. Minimal flat ink style; consistent role, adult identity and lavender clothing with only scenario-required outerwear. Distinct from mascot and companion.'
 else:c['characters']=c['characters'][:2]
 if n==440:
  for cid,name,look in [('CH04','Người chơi ghi-ta','Adult band guitarist wearing muted sage top, playing a realistic guitar on stage.'),('CH05','Người chơi trống','Adult band drummer wearing muted coral top, seated at realistic drum kit on stage.')]:
   c['characters'].append({'id':cid,'name':name,'appearance':look+' Minimal flat ink style; maintain same identity throughout.','outfit':'Plain single top in specified color; no logos.'})
 for sc in c['scenes']:
  v=sc['action'].lower();ids=['CH01']
  if any(w in v for w in keys2) or any(w in v for w in ['both','two people','travelers','visitors','two adults']):ids.append('CH02')
  if name3 and any(w in v for w in keys3):ids.append('CH03')
  if n==440:ids=list(dict.fromkeys(ids+['CH02','CH03','CH04','CH05']))
  sc['character_ids']=ids
  for im in sc['images']:im['character_ids']=ids
