import{H as e,K as t,U as n,a as r,c as i,f as a,v as o,w as s,x as c,y as l}from"./chunk-CSCIHK7Q-DshIDzEl.js";import{_ as u,v as d}from"./src-DtrW_ym7.js";import{n as f}from"./path-HTXttWil.js";import{m as p}from"./dist-D4B_Bs5p.js";import{t as m}from"./array-BifhSqXX.js";import{i as h,p as g}from"./chunk-5ZQYHXKU-CIWtHQms.js";import{d as _,k as v,u as y}from"./index-BVA7ZKFx.js";import{t as b}from"./mermaid-parser.core-CWNDhgFu.js";import{t as x}from"./chunk-4BX2VUAB-B2KlDyB0.js";function S(e,t){return t<e?-1:t>e?1:t>=e?0:NaN}function C(e){return e}function w(){var e=C,t=S,n=null,r=f(0),i=f(p),a=f(0);function o(o){var s,c=(o=m(o)).length,l,u,d=0,f=Array(c),h=Array(c),g=+r.apply(this,arguments),_=Math.min(p,Math.max(-p,i.apply(this,arguments)-g)),v,y=Math.min(Math.abs(_)/c,a.apply(this,arguments)),b=y*(_<0?-1:1),x;for(s=0;s<c;++s)(x=h[f[s]=s]=+e(o[s],s,o))>0&&(d+=x);for(t==null?n!=null&&f.sort(function(e,t){return n(o[e],o[t])}):f.sort(function(e,n){return t(h[e],h[n])}),s=0,u=d?(_-c*b)/d:0;s<c;++s,g=v)l=f[s],x=h[l],v=g+(x>0?x*u:0)+b,h[l]={data:o[l],index:s,value:x,startAngle:g,endAngle:v,padAngle:y};return h}return o.value=function(t){return arguments.length?(e=typeof t==`function`?t:f(+t),o):e},o.sortValues=function(e){return arguments.length?(t=e,n=null,o):t},o.sort=function(e){return arguments.length?(n=e,t=null,o):n},o.startAngle=function(e){return arguments.length?(r=typeof e==`function`?e:f(+e),o):r},o.endAngle=function(e){return arguments.length?(i=typeof e==`function`?e:f(+e),o):i},o.padAngle=function(e){return arguments.length?(a=typeof e==`function`?e:f(+e),o):a},o}var T=a.pie,E={sections:new Map,showData:!1,config:T},D=E.sections,O=E.showData,k=structuredClone(T),A={getConfig:u(()=>structuredClone(k),`getConfig`),clear:u(()=>{D=new Map,O=E.showData,r()},`clear`),setDiagramTitle:t,getDiagramTitle:s,setAccTitle:n,getAccTitle:l,setAccDescription:e,getAccDescription:o,addSection:u(({label:e,value:t})=>{if(t<0)throw Error(`"${e}" has invalid value: ${t}. Negative values are not allowed in pie charts. All slice values must be >= 0.`);D.has(e)||(D.set(e,t),d.debug(`added new section: ${e}, with value: ${t}`))},`addSection`),getSections:u(()=>D,`getSections`),setShowData:u(e=>{O=e},`setShowData`),getShowData:u(()=>O,`getShowData`)},j=u((e,t)=>{x(e,t),t.setShowData(e.showData),e.sections.map(t.addSection)},`populateDb`),M={parse:u(async e=>{let t=await b(`pie`,e);d.debug(t),j(t,A)},`parse`)},N=u(e=>`
  .pieCircle{
    stroke: ${e.pieStrokeColor};
    stroke-width : ${e.pieStrokeWidth};
    opacity : ${e.pieOpacity};
  }
  .pieOuterCircle{
    stroke: ${e.pieOuterStrokeColor};
    stroke-width: ${e.pieOuterStrokeWidth};
    fill: none;
  }
  .pieTitleText {
    text-anchor: middle;
    font-size: ${e.pieTitleTextSize};
    fill: ${e.pieTitleTextColor};
    font-family: ${e.fontFamily};
  }
  .slice {
    font-family: ${e.fontFamily};
    fill: ${e.pieSectionTextColor};
    font-size:${e.pieSectionTextSize};
    // fill: white;
  }
  .legend text {
    fill: ${e.pieLegendTextColor};
    font-family: ${e.fontFamily};
    font-size: ${e.pieLegendTextSize};
  }
`,`getStyles`),P=u(e=>{let t=[...e.values()].reduce((e,t)=>e+t,0),n=[...e.entries()].map(([e,t])=>({label:e,value:t})).filter(e=>e.value/t*100>=1);return w().value(e=>e.value).sort(null)(n)},`createPieArcs`),F={parser:M,db:A,renderer:{draw:u((e,t,n,r)=>{d.debug(`rendering pie chart
`+e);let a=r.db,o=c(),s=h(a.getConfig(),o.pie),l=y(t),u=l.append(`g`);u.attr(`transform`,`translate(225,225)`);let{themeVariables:f}=o,[p]=g(f.pieOuterStrokeWidth);p??=2;let m=s.textPosition,b=_().innerRadius(0).outerRadius(185),x=_().innerRadius(185*m).outerRadius(185*m);u.append(`circle`).attr(`cx`,0).attr(`cy`,0).attr(`r`,185+p/2).attr(`class`,`pieOuterCircle`);let S=a.getSections(),C=P(S),w=[f.pie1,f.pie2,f.pie3,f.pie4,f.pie5,f.pie6,f.pie7,f.pie8,f.pie9,f.pie10,f.pie11,f.pie12],T=0;S.forEach(e=>{T+=e});let E=C.filter(e=>(e.data.value/T*100).toFixed(0)!==`0`),D=v(w).domain([...S.keys()]);u.selectAll(`mySlices`).data(E).enter().append(`path`).attr(`d`,b).attr(`fill`,e=>D(e.data.label)).attr(`class`,`pieCircle`),u.selectAll(`mySlices`).data(E).enter().append(`text`).text(e=>(e.data.value/T*100).toFixed(0)+`%`).attr(`transform`,e=>`translate(`+x.centroid(e)+`)`).style(`text-anchor`,`middle`).attr(`class`,`slice`);let O=u.append(`text`).text(a.getDiagramTitle()).attr(`x`,0).attr(`y`,-400/2).attr(`class`,`pieTitleText`),k=[...S.entries()].map(([e,t])=>({label:e,value:t})),A=u.selectAll(`.legend`).data(k).enter().append(`g`).attr(`class`,`legend`).attr(`transform`,(e,t)=>{let n=22*k.length/2;return`translate(216,`+(t*22-n)+`)`});A.append(`rect`).attr(`width`,18).attr(`height`,18).style(`fill`,e=>D(e.label)).style(`stroke`,e=>D(e.label)),A.append(`text`).attr(`x`,22).attr(`y`,14).text(e=>a.getShowData()?`${e.label} [${e.value}]`:e.label);let j=512+Math.max(...A.selectAll(`text`).nodes().map(e=>e?.getBoundingClientRect().width??0)),M=O.node()?.getBoundingClientRect().width??0,N=450/2-M/2,F=450/2+M/2,I=Math.min(0,N),L=Math.max(j,F)-I;l.attr(`viewBox`,`${I} 0 ${L} 450`),i(l,450,L,s.useMaxWidth)},`draw`)},styles:N};export{F as diagram};