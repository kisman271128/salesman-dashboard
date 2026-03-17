async function loadAllDashboardData(){

const files = [
"data/d.30pareto.json",
"data/d.area.json",
"data/d.channel.json",
"data/d.channelproj.json",
"data/d.d.dashboard.json",
"data/d.depoproses.json",
"data/d.details.json",
"data/d.harijks.json"
];

let result = {};

for(let f of files){

try{

let res = await fetch(f);
let json = await res.json();

result[f] = json;

}catch(e){

console.log("file tidak ada:",f);

}

}

return result;
}