(() => {
  const raw=document.getElementById('domain-experts-data');
  const svg=document.getElementById('domain-experts-graph');
  const detail=document.getElementById('domain-expert-detail');
  if(!raw||!svg||!detail)return;
  let people=[];
  try{people=JSON.parse(raw.textContent);}catch(_){detail.textContent='专家数据格式错误。';return;}
  const NS='http://www.w3.org/2000/svg';
  const colors={ai:'#245a96',epox:'#a56a2c'};
  let works=[];try{works=JSON.parse(document.getElementById('domain-expert-papers-data').textContent).papers||[];}catch(_){}
  let history=[];try{history=JSON.parse(document.getElementById('domain-expert-candidates-data').textContent).candidates||[];}catch(_){}
  // Browser TTS is an accessible pronunciation aid, not a verified recording.
  // Native voice availability depends on the user's operating system.
  const pronunciationLocales = {
    xin: 'en-US', kitchin: 'en-US', lopez: 'es-ES', kulik: 'en-US',
    ulissi: 'en-US', corma: 'es-ES', coperet: 'fr-FR',
    hutchings: 'en-GB', weckhuysen: 'nl-NL', davis: 'en-US'
  };
  function speakPerson(p) {
    if (!('speechSynthesis' in window) || !('SpeechSynthesisUtterance' in window)) {
      window.alert('当前浏览器不支持语音播放。');
      return;
    }
    const speech = window.speechSynthesis;
    speech.cancel();
    // Never pass bilingual display labels (e.g. "Xiang Feng（冯翔）") to English TTS.
    // Prefer original Chinese characters for Chinese names with Mandarin TTS.
    // Other names use only their Latin-script display name; pronunciation is approximate.
    const chineseNames = { cao_yueqiang: '曹约强', feng_xiang: '冯翔', lin_dong: '林栋', xin: '辛洪良' };
    const isChinese = Object.prototype.hasOwnProperty.call(chineseNames, p.id);
    const spokenName = isChinese ? chineseNames[p.id] : p.name.split(/[（(]/, 1)[0].trim();
    const utterance = new SpeechSynthesisUtterance(spokenName);
    utterance.lang = isChinese ? 'zh-CN' : (pronunciationLocales[p.id] || 'en-US');
    utterance.rate = 0.82;
    const voices = speech.getVoices();
    const matchingVoice = voices.find(v => v.lang.toLowerCase() === utterance.lang.toLowerCase())
      || voices.find(v => v.lang.toLowerCase().split('-')[0] === utterance.lang.toLowerCase().split('-')[0]);
    if (matchingVoice) utterance.voice = matchingVoice;
    utterance.onerror = event => {
      if (event.error !== 'canceled' && event.error !== 'interrupted')
        console.warn('姓名语音播放失败:', p.id, event.error);
    };
    speech.speak(utterance);
  }
  function pronounceButton(p) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'domain-pronounce-button';
    button.setAttribute('aria-label', '播放 ' + p.name + ' 的姓名读音');
    button.title = '播放姓名读音（浏览器合成语音）';
    button.textContent = '🔊 发音';
    button.addEventListener('click', () => speakPerson(p));
    return button;
  }
  let filter='all';
  const topicGroups={};
  const evidenceTopics={};
  const allWorks=[...works.map(w=>({expertNames:w.author_names||[],tags:w.match_tags||[],group:w.group})),
    ...history.map(w=>({expertNames:[w.expert_name],tags:w.relevance_tags||[],group:people.find(p=>p.id===w.expert_id)?.group}))];
  allWorks.forEach(w=>w.expertNames.forEach(name=>{
    const person=people.find(p=>p.name===name);if(!person)return;
    (evidenceTopics[person.id]??=new Set());
    w.tags.forEach(t=>evidenceTopics[person.id].add(t));
  }));
  people.forEach(p=>[...new Set([...p.topics,...(evidenceTopics[p.id]||[])])].forEach(t=>{
    (topicGroups[t]??=new Set()).add(p.group);
  }));
  function s(tag,attrs={}){const n=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,String(v)));return n;}
  function clear(el){while(el.firstChild)el.removeChild(el.firstChild);}
  function txt(node,text){node.appendChild(document.createTextNode(text));return node;}
  function detailPerson(p){clear(detail);const h=document.createElement('h3');h.textContent=p.name;h.append(document.createTextNode(' '), pronounceButton(p));detail.append(h);const a=document.createElement('p');a.textContent=p.institution+'｜'+p.intro;detail.append(a);const t=document.createElement('p');t.textContent='研究主题（人工整理）：'+p.topics.join('、')+'；论文主题线索（自动）：'+[...(evidenceTopics[p.id]||[])].join('、');detail.append(t);const link=document.createElement('a');link.href=p.official_url;link.target='_blank';link.rel='noopener noreferrer';link.textContent='官方资料 ↗';detail.append(link);if(p.orcid){detail.append(document.createTextNode(' · '));const o=document.createElement('a');o.href='https://orcid.org/'+p.orcid;o.target='_blank';o.rel='noopener noreferrer';o.textContent='ORCID ↗';detail.append(o);}const subset=works.filter(w=>(w.author_names||[]).includes(p.name)).slice(0,5);if(subset.length){const h2=document.createElement('h4');h2.textContent='最近匹配论文';detail.append(h2);const ul=document.createElement('ul');subset.forEach(w=>{const li=document.createElement('li');const a=document.createElement('a');a.textContent=w.publication_date+' · '+w.title;a.href=w.doi_url;a.target='_blank';a.rel='noopener noreferrer';li.append(a);ul.append(li);});detail.append(ul);}detail.scrollIntoView({behavior:'smooth',block:'nearest'});}
  function detailTopic(topic){clear(detail);const h=document.createElement('h3');h.textContent=topic;detail.append(h);const p=document.createElement('p');p.textContent='关联专家（实线为人工整理的研究兴趣；虚线为论文关键词自动匹配）：'+people.filter(x=>(x.topics.includes(topic)||(evidenceTopics[x.id]||new Set()).has(topic))&&(filter==='all'||x.group===filter)).map(x=>x.name).join('、');detail.append(p);}
  function render(){clear(svg);
    const active=people.filter(p=>filter==='all'||p.group===filter);
    const perGroup={ai:active.filter(p=>p.group==='ai'),epox:active.filter(p=>p.group==='epox')};
    const topics=[...new Set(active.flatMap(p=>[...p.topics,...(evidenceTopics[p.id]||[])]))];
    const pos={};
    const groupX={ai:270,epox:630};
    for(const g of ['ai','epox']){
      perGroup[g].forEach((p,i,arr)=>{pos[p.id]={x:groupX[g],y:270+(i-(arr.length-1)/2)*67};});
    }
    topics.forEach(t=>{const g=topicGroups[t].has('ai')&&topicGroups[t].has('epox')?'both':([...topicGroups[t]][0]);
      const catList=topics.filter(x=>(topicGroups[x].has('ai')&&topicGroups[x].has('epox')?'both':[...topicGroups[x]][0])===g);
      const rank=catList.indexOf(t);const x=g==='both'?450:g==='ai'?90:810;
      const y=90+rank*(g==='both'?68:62);pos['topic:'+t]={x,y};
    });
    const back=s('g'); svg.append(back);
    active.forEach(p=>[...new Set([...p.topics,...(evidenceTopics[p.id]||[])])].forEach(t=>{const a=pos[p.id],b=pos['topic:'+t];if(!a||!b)return;
      back.append(s('line',{x1:a.x,y1:a.y,x2:b.x,y2:b.y,stroke:p.group==='ai'?'#a4bdd6':'#d4b79d','stroke-width':1.6,opacity:.7,'stroke-dasharray':p.topics.includes(t)?'':'3 4'}));}));
    svg.append(txt(s('text',{x:255,y:33,'text-anchor':'middle',fill:colors.ai,'font-size':17,'font-weight':600}), 'AI 结合知识学习'));
    svg.append(txt(s('text',{x:645,y:33,'text-anchor':'middle',fill:colors.epox,'font-size':17,'font-weight':600}),'烯烃环氧化'));
    topics.forEach(t=>{const p=pos['topic:'+t],g=s('g',{class:'domain-topic-node',tabindex:0,role:'button','aria-label':'研究主题：'+t});
      g.append(s('rect',{x:p.x-64,y:p.y-16,width:128,height:33,rx:3,fill:'#edf1f4',stroke:'#a7afb7'}));g.append(txt(s('text',{x:p.x,y:p.y+4,'text-anchor':'middle',class:'domain-node-label',fill:'#26333f'}),t));
      const fire=()=>detailTopic(t);g.addEventListener('click',fire);g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();fire();}});svg.append(g);});
    active.forEach(p=>{const q=pos[p.id],g=s('g',{class:'domain-person-node',tabindex:0,role:'button','aria-label':'专家：'+p.name});
      g.append(s('rect',{x:q.x-95,y:q.y-18,width:190,height:36,rx:4,fill:'#fff',stroke:colors[p.group],'stroke-width':2,class:'domain-node-shape'}));
      g.append(txt(s('text',{x:q.x,y:q.y+4,'text-anchor':'middle',class:'domain-node-label',fill:'#233344'}),p.name));
      const fire=()=>detailPerson(p);g.addEventListener('click',fire);g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();fire();}});svg.append(g);});
    const recent=works.filter(w=>filter==='all'||w.group===filter).slice(0,6);
    recent.forEach((w,i)=>{const x=105+(i%3)*345,y=585+Math.floor(i/3)*54;
      (w.author_names||[]).forEach(name=>{const match=active.find(p=>p.name===name);if(match&&pos[match.id]){const a=pos[match.id];back.append(s('line',{x1:a.x,y1:a.y,x2:x,y2:y,stroke:colors[match.group],'stroke-width':1.2,opacity:.55,'stroke-dasharray':'4 3'}));}});
      const group=s('g',{class:'domain-paper-node',tabindex:0,role:'link','aria-label':'论文：'+w.title});
      const color=colors[w.group]||'#777';
      group.append(s('rect',{x:x-90,y:y-19,width:235,height:38,rx:3,fill:'#fafafa',stroke:color,'stroke-width':1.4}));
      group.append(txt(s('text',{x:x-80,y:y-3,'font-size':11,fill:'#26333f'}),(w.title||'').slice(0,30)+((w.title||'').length>30?'…':'')));
      group.append(txt(s('text',{x:x-80,y:y+12,'font-size':10,fill:'#666'}),w.publication_date||''));
      const fire=()=>{clear(detail);const h=document.createElement('h3');h.textContent=w.title;detail.append(h);const p=document.createElement('p');p.textContent='相关领域：'+w.group_label+'；匹配标签：'+w.match_tags.join('、');detail.append(p);const link=document.createElement('a');link.href=w.doi_url;link.target='_blank';link.rel='noopener noreferrer';link.textContent='论文 DOI ↗';detail.append(link);detail.scrollIntoView({behavior:'smooth',block:'nearest'});};
      group.addEventListener('click',fire);group.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();fire();}});svg.append(group);
    });
    document.querySelectorAll('[data-person-group],[data-paper-group],[data-milestone-group]').forEach(el=>el.classList.toggle('domain-hidden',filter!=='all'&&el.dataset.personGroup!==filter&&el.dataset.paperGroup!==filter&&el.dataset.milestoneGroup!==filter));
  }
  document.querySelectorAll('[data-domain-filter]').forEach(btn=>btn.addEventListener('click',()=>{
    filter=btn.dataset.domainFilter;
    document.querySelectorAll('[data-domain-filter]').forEach(b=>{const selected=b===btn;b.classList.toggle('domain-active',selected);b.setAttribute('aria-pressed',selected?'true':'false');});render();
  }));
  document.querySelectorAll('[data-pronounce-id]').forEach(btn=>btn.addEventListener('click',()=>{
    const p=people.find(person=>person.id===btn.dataset.pronounceId);
    if(p)speakPerson(p);
  }));
  document.querySelectorAll('[data-person-id]').forEach(btn=>btn.addEventListener('click',()=>{const p=people.find(p=>p.id===btn.dataset.personId);if(p)detailPerson(p);}));
  render();
})();
